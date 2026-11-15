"""Implementation of 'sbk sandbox' commands: init, reset, path."""

import logging
from argparse import Namespace
from pathlib import Path

from ...core.sandbox import get_default_sandbox_path, init_sandbox, reset_sandbox
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_sandbox(args: Namespace, logger: logging.Logger) -> int:
    """Manage isolated testing sandbox environments."""
    action = getattr(args, "sandbox_action", None)
    if not action:
        logger.error("No sandbox action specified. Choose from: init, reset, path.")
        return EXIT_ERROR

    target_dir = Path(args.target).resolve() if getattr(args, "target", None) else None

    if action == "path":
        dest = target_dir or get_default_sandbox_path()
        print(str(dest.resolve()))
        return EXIT_SUCCESS

    if action == "init":
        force = getattr(args, "force", False)
        try:
            dest = init_sandbox(target_path=target_dir, force=force)
        except Exception as exc:
            logger.error("Failed to initialize sandbox: %s", exc)
            return EXIT_ERROR

        logger.info("Sandbox vault initialized at: %s", dest)
        return EXIT_SUCCESS

    if action == "reset":
        try:
            dest = reset_sandbox(target_path=target_dir)
        except Exception as exc:
            logger.error("Failed to reset sandbox: %s", exc)
            return EXIT_ERROR

        logger.info("Sandbox vault reset to pristine state at: %s", dest)
        return EXIT_SUCCESS

    logger.error("Unknown sandbox action: %s", action)
    return EXIT_ERROR
