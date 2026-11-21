"""Implementation of 'sbk map' command."""

import logging
from argparse import Namespace

from ...core.map import VaultMapEngine
from ...exceptions import SBKError, VaultKeeperError
from ...utils.formatters import ReportWriter
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_map(args: Namespace, logger: logging.Logger) -> int:
    """Generate high-level Johnny.Decimal area telemetry and master vault map."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    outputs = ReportWriter.extract_outputs(args)
    fmt = getattr(args, "format", "md")

    try:
        report, _ = v.vault_map(output_file=None)
    except (SBKError, VaultKeeperError) as exc:
        logger.error("Failed to generate vault map: %s", exc)
        return EXIT_ERROR

    md_content = VaultMapEngine(v.config).render_markdown_map(report)
    rw = ReportWriter(
        data=report.to_dict(),
        md_rendered=md_content,
        title=f"Mappa del Vault - {v.root.name}",
    )
    rw.write_reports(
        console_format=fmt,
        output_files=outputs,
        quiet=getattr(args, "quiet", False),
        logger=logger,
    )

    return EXIT_SUCCESS
