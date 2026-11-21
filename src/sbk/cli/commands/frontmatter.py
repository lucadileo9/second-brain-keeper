"""Implementation of 'sbk frontmatter' subcommands."""

from __future__ import annotations

import logging
from argparse import Namespace

from ...core.frontmatter import (
    parse_note_content,
    update_frontmatter,
)
from ...core.traversal import walk_vault_files
from ...exceptions import FrontmatterError, VaultKeeperError
from ...utils.helpers import resolve_vault_path
from ...vault import Vault
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_frontmatter(args: Namespace, logger: logging.Logger) -> int:
    """Dispatch frontmatter subcommands."""
    subaction = getattr(args, "fm_action", None)
    if not subaction:
        logger.error("Unknown frontmatter action. Choose: set-type, add-tags, sanitize-tags.")
        return EXIT_ERROR

    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    if subaction == "set-type":
        return handle_set_type(args, logger, v)
    elif subaction == "add-tags":
        return handle_add_tags(args, logger, v)
    elif subaction == "sanitize-tags":
        return handle_sanitize_tags(args, logger, v)
    else:
        logger.error("Unknown frontmatter action. Choose: set-type, add-tags, sanitize-tags.")
        return EXIT_ERROR


def handle_set_type(args: Namespace, logger: logging.Logger, v: Vault) -> int:
    """Set or update the tipo YAML frontmatter field."""
    batch_arg = getattr(args, "batch", None)
    target = getattr(args, "target", None)
    new_type = getattr(args, "type", None)
    dry_run = getattr(args, "dry_run", False)
    prefix = "[DRY-RUN] " if dry_run else ""

    if batch_arg:
        try:
            results = v.batch_set_frontmatter_type(batch_arg, dry_run=dry_run)
        except (FrontmatterError, VaultKeeperError) as exc:
            logger.error("Batch set-type rejected: %s", exc)
            return EXIT_ERROR
        except Exception as exc:
            logger.error("Unexpected error during batch set-type: %s", exc)
            return EXIT_ERROR

        updated_count = 0
        for p, changed in results:
            if changed:
                logger.info("%sUpdated %s: set %s to '%s'", prefix, p.name, v.config.type_field, new_type or "new type")
                updated_count += 1
            else:
                logger.info("%sUnchanged: %s already has target %s", prefix, p.name, v.config.type_field)

        logger.info(
            "%sBatch set-type completed successfully: %d processed, %d updated.",
            prefix,
            len(results),
            updated_count,
        )
        return EXIT_SUCCESS

    if not target or not new_type:
        logger.error("Specify both --target and --type, or use --batch <file.json>.")
        return EXIT_ERROR

    target_path = resolve_vault_path(target, v.root)
    try:
        changed = v.set_frontmatter_type(target_path, new_type, dry_run=dry_run)
    except (FrontmatterError, VaultKeeperError) as exc:
        logger.error("Failed to set frontmatter type: %s", exc)
        return EXIT_ERROR

    if changed:
        logger.info("%sUpdated %s: %s -> %s", prefix, target_path.name, v.config.type_field, new_type)
    else:
        logger.info("Frontmatter already has %s: %s", v.config.type_field, new_type)

    return EXIT_SUCCESS


def handle_add_tags(args: Namespace, logger: logging.Logger, v: Vault) -> int:
    """Inject or overwrite tags in a note's frontmatter."""
    batch_arg = getattr(args, "batch", None)
    target = getattr(args, "target", None)
    tags = getattr(args, "tags", None)
    overwrite = getattr(args, "overwrite", False)
    dry_run = getattr(args, "dry_run", False)
    prefix = "[DRY-RUN] " if dry_run else ""

    if batch_arg:
        try:
            results = v.batch_add_frontmatter_tags(batch_arg, overwrite=overwrite, dry_run=dry_run)
        except (FrontmatterError, VaultKeeperError) as exc:
            logger.error("Batch add-tags rejected: %s", exc)
            return EXIT_ERROR
        except Exception as exc:
            logger.error("Unexpected error during batch add-tags: %s", exc)
            return EXIT_ERROR

        action_name = "overwritten" if overwrite else "added"
        updated_count = 0
        for p, changed in results:
            if changed:
                logger.info("%sUpdated %s: tags %s", prefix, p.name, action_name)
                updated_count += 1
            else:
                logger.info("%sUnchanged: %s already contains specified tags", prefix, p.name)

        logger.info(
            "%sBatch %s completed successfully: %d processed, %d updated.",
            prefix,
            "overwrite-tags" if overwrite else "add-tags",
            len(results),
            updated_count,
        )
        return EXIT_SUCCESS

    if not target or not tags:
        logger.error("Specify both --target and --tags, or use --batch <file.json>.")
        return EXIT_ERROR

    target_path = resolve_vault_path(target, v.root)
    changed = v.add_frontmatter_tags(target_path, tags, overwrite=overwrite, dry_run=dry_run)

    if changed:
        logger.info("%sInjected %d tags into: %s", prefix, len(tags), target_path.name)
    else:
        logger.info("Tags already present in: %s", target_path.name)

    return EXIT_SUCCESS


def handle_sanitize_tags(args: Namespace, logger: logging.Logger, v: Vault) -> int:
    """Sanitize and apply tag replacements based on taxonomy and config mapping."""
    dry_run = getattr(args, "dry_run", False)
    target = getattr(args, "target", None)
    prefix = "[DRY-RUN] " if dry_run else ""

    target_dir = resolve_vault_path(target, v.root) if target else v.root
    replacements = v.config.tag_replacements
    logger.info("%sSanitizing tags across notes in: %s", prefix, target_dir)

    modified_count = 0
    for note_path in walk_vault_files(v.config, target_dir=target_dir, extensions={".md"}):
        try:
            content = note_path.read_text(encoding="utf-8")
        except Exception:
            continue

        fm, body = parse_note_content(content, type_field=v.config.type_field)
        if not fm or not fm.tags:
            continue

        updated_tags = []
        changed = False
        for tag in fm.tags:
            if tag in replacements:
                updated_tags.append(replacements[tag])
                changed = True
            else:
                updated_tags.append(tag)

        if changed:
            updated_content = update_frontmatter(content, {"tags": updated_tags}, type_field=v.config.type_field)
            if not dry_run:
                note_path.write_text(updated_content, encoding="utf-8")
            modified_count += 1
            logger.info("  - %s: updated tags to %s", note_path.name, updated_tags)

    logger.info("%sCompleted tag sanitization. %d notes modified.", prefix, modified_count)
    return EXIT_SUCCESS
