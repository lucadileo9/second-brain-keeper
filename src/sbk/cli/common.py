"""Shared CLI context helpers and common utilities."""

import logging
from argparse import Namespace
from typing import Optional

from ..vault import Vault


def get_vault(args: Namespace, logger: logging.Logger) -> Optional[Vault]:
    """Initialize and return Vault facade from CLI arguments with standardized logging."""
    try:
        return Vault(
            root_path=getattr(args, "root", None),
            config_file=getattr(args, "config", None),
        )
    except Exception as exc:
        logger.error("Failed to initialize vault: %s", exc)
        return None
