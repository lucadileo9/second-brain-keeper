"""Implementation of 'sbk tags' command: show, add, remove."""

import logging
from argparse import Namespace

from ...exceptions import TaxonomyError, VaultKeeperError
from ...utils.formatters import ReportWriter
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_tags(args: Namespace, logger: logging.Logger) -> int:
    """Inspect and manipulate controlled tag taxonomy."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    action = getattr(args, "tag_action", None)
    if not action:
        logger.error("No tag action specified. Choose from: show, add, remove.")
        return EXIT_ERROR

    if action == "show":
        query = getattr(args, "query", None)
        fmt = getattr(args, "format", "md")
        tags = v.tags_show(query=query)

        outputs = ReportWriter.extract_outputs(args)

        data = [{"Tag": f"#{t}"} for t in tags]
        title = f"Tassonomia Tag ({len(tags)} registrati)" if not query else f"Tassonomia Tag (Filtro: '{query}')"
        rw = ReportWriter(data=data, headers=["Tag"], title=title)
        rw.write_reports(
            console_format=fmt,
            output_files=outputs,
            quiet=getattr(args, "quiet", False),
            logger=logger,
        )
        return EXIT_SUCCESS

    if action == "add":
        tag = getattr(args, "tag")
        section = getattr(args, "section", None)
        dry_run = getattr(args, "dry_run", False)
        prefix = "[DRY-RUN] " if dry_run else ""

        try:
            res = v.tags_add(tag, section=section, dry_run=dry_run)
        except (TaxonomyError, VaultKeeperError) as exc:
            logger.error("Failed to add tag: %s", exc)
            return EXIT_ERROR

        if res.action == "already_exists":
            logger.info("Tag '#%s' is already registered in %s", res.tag, res.taxonomy_file.name)
            return EXIT_SUCCESS

        logger.info("%sTag '#%s' successfully registered in %s", prefix, res.tag, res.taxonomy_file.name)
        if res.tx_id:
            logger.debug("  - Transaction ID: %s (reversible with 'sbk undo')", res.tx_id)
        return EXIT_SUCCESS

    if action == "remove":
        tag = getattr(args, "tag")
        force = getattr(args, "force", False)
        dry_run = getattr(args, "dry_run", False)
        prefix = "[DRY-RUN] " if dry_run else ""

        try:
            res = v.tags_remove(tag, force=force, dry_run=dry_run)
        except (TaxonomyError, VaultKeeperError) as exc:
            logger.error("Failed to remove tag: %s", exc)
            return EXIT_ERROR

        logger.info("%sTag '#%s' removed from %s", prefix, res.tag, res.taxonomy_file.name)
        if res.notes_affected_count > 0:
            logger.warning("  - Tag was referenced in %d note(s)", res.notes_affected_count)
        if res.tx_id:
            logger.debug("  - Transaction ID: %s (reversible with 'sbk undo')", res.tx_id)
        return EXIT_SUCCESS

    logger.error("Unknown tag action: %s", action)
    return EXIT_ERROR
