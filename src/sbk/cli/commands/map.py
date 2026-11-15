"""Implementation of 'sbk map' command."""

import logging
from argparse import Namespace

from ...exceptions import SBKError, VaultKeeperError
from ...utils.formatters import format_output
from ...vault import Vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_map(args: Namespace, logger: logging.Logger) -> int:
    """Generate high-level Johnny.Decimal area telemetry and master vault map."""
    try:
        v = Vault(root_path=getattr(args, "root", None), config_file=getattr(args, "config", None))
    except Exception as exc:
        logger.error("Failed to initialize vault: %s", exc)
        return EXIT_ERROR

    outputs = list(getattr(args, "outputs", None) or [])
    output_arg = getattr(args, "output", None)
    if output_arg:
        if isinstance(output_arg, list):
            outputs.extend(output_arg)
        elif isinstance(output_arg, str):
            outputs.append(output_arg)

    fmt = getattr(args, "format", "md")

    try:
        report, _ = v.vault_map(output_file=None)
    except (SBKError, VaultKeeperError) as exc:
        logger.error("Failed to generate vault map: %s", exc)
        return EXIT_ERROR

    from ...core.map import VaultMapEngine
    from ...utils.formatters import ReportWriter

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
