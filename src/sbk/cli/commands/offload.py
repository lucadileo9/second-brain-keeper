"""Implementation of 'sbk offload' command."""

import logging
from argparse import Namespace

from ...exceptions import OffloadError, VaultKeeperError
from ...utils.helpers import format_bytes
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_offload(args: Namespace, logger: logging.Logger) -> int:
    """Offload heavy binary files (>50MB or specific target) to cold storage."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    target_arg = getattr(args, "target", None)
    dry_run = getattr(args, "dry_run", False)
    prefix = "[DRY-RUN] " if dry_run else ""

    try:
        res = v.offload(
            target=target_arg,
            dry_run=dry_run,
        )
    except (OffloadError, VaultKeeperError) as exc:
        logger.error("Offload rejected: %s", exc)
        return EXIT_ERROR
    except Exception as exc:
        logger.error("Unexpected error during offload: %s", exc)
        return EXIT_ERROR

    if not res.offloaded_files:
        logger.info("No heavy binary files found matching criteria.")
        return EXIT_SUCCESS

    logger.info(
        "%sOffloaded %d files (Saved: %s):",
        prefix,
        len(res.offloaded_files),
        format_bytes(res.total_bytes_saved),
    )
    for src, dst, size in res.offloaded_files:
        logger.info("  - %s -> %s (%s)", src.name, dst.name, format_bytes(size))

    logger.info("  - Updated notes with external links: %d", res.updated_notes_count)
    if res.tx_id:
        logger.debug("  - Transaction ID: %s (reversible with 'sbk undo')", res.tx_id)

    return EXIT_SUCCESS
