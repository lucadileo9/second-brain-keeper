"""Implementation of 'sbk redo' command."""

import logging
from argparse import Namespace

from ...vault import Vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_redo(args: Namespace, logger: logging.Logger) -> int:
    """Reapply the most recent or specified reverted transaction."""
    try:
        v = Vault(root_path=getattr(args, "root", None), config_file=getattr(args, "config", None))
    except Exception as exc:
        logger.error("Failed to initialize vault: %s", exc)
        return EXIT_ERROR

    tx_id = getattr(args, "tx", None)
    dry_run = getattr(args, "dry_run", False)

    try:
        result = v.redo(tx_id=tx_id, dry_run=dry_run)
    except Exception as exc:
        logger.error("Redo failed: %s", exc)
        return EXIT_ERROR

    if not result.success:
        logger.warning(result.message)
        return EXIT_ERROR

    logger.info(result.message)
    if result.affected_files:
        logger.info("File coinvolti (%d):", len(result.affected_files))
        for f in result.affected_files:
            logger.info("  - %s", f)

    return EXIT_SUCCESS
