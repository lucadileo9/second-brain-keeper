"""Implementation of 'sbk audit' command."""

import json
import logging
from argparse import Namespace
from pathlib import Path

from ...vault import Vault
from ..constants import EXIT_ERROR, EXIT_ISSUES_FOUND, EXIT_SUCCESS


def handle_audit(args: Namespace, logger: logging.Logger) -> int:
    """Execute unified multi-phase audit and format results."""
    try:
        v = Vault(root_path=getattr(args, "root", None), config_file=getattr(args, "config", None))
    except Exception as exc:
        logger.error("Failed to initialize vault: %s", exc)
        return EXIT_ERROR

    steps = [int(args.step)] if getattr(args, "step", None) else [1, 2, 3, 4, 5]
    logger.info("Executing VaultKeeper audit for: %s", v.root)
    logger.info("Phases to execute: %s", ", ".join(str(s) for s in steps))

    report = v.audit(phases=steps)

    logger.info("-" * 60)
    for phase in report.phases:
        status_text = "OK" if phase.is_clean() else f"{len(phase.issues)} ISSUES"
        logger.info("[Phase %d] %s: %s (%d warnings)", phase.phase_id, phase.title, status_text, len(phase.warnings))
        for issue in phase.issues[:10]:
            logger.warning("  - Issue: %s", issue)
        if len(phase.issues) > 10:
            logger.warning("  ... and %d more issues", len(phase.issues) - 10)
        for warn in phase.warnings[:10]:
            logger.warning("  - Warning: %s", warn)
        if len(phase.warnings) > 10:
            logger.warning("  ... and %d more warnings", len(phase.warnings) - 10)

    logger.info("-" * 60)
    logger.info("Total Issues: %d", report.total_issues)
    logger.info("Vault Health Score: %.2f / 100.0", report.health_score)

    # Export reports if requested
    outputs = list(getattr(args, "outputs", None) or [])
    if getattr(args, "output", None) and isinstance(args.output, str):
        outputs.append(args.output)
    if getattr(args, "json", None):
        outputs.append(args.json)
    if getattr(args, "report_md", None):
        outputs.append(args.report_md)

    from ...utils.formatters import ReportWriter

    md_lines = [
        f"# Audit Report - {report.vault_root.name}",
        f"**Timestamp:** {report.timestamp}",
        f"**Health Score:** {report.health_score:.2f} / 100.0",
        f"**Total Issues:** {report.total_issues}",
        "",
    ]
    for phase in report.phases:
        md_lines.append(f"## Phase {phase.phase_id}: {phase.title}")
        md_lines.append(f"- Issues: {len(phase.issues)}")
        md_lines.append(f"- Warnings: {len(phase.warnings)}")
        if phase.issues:
            md_lines.append("")
            md_lines.append("### Issues")
            for iss in phase.issues:
                md_lines.append(f"- {iss}")
        if phase.warnings:
            md_lines.append("")
            md_lines.append("### Warnings")
            for warn in phase.warnings:
                md_lines.append(f"- {warn}")
        md_lines.append("")

    fmt = getattr(args, "format", "md")
    rw = ReportWriter(
        data=report.to_dict(),
        md_rendered="\n".join(md_lines),
        title=f"Audit Report - {report.vault_root.name}",
    )

    if fmt in ("json", "yaml"):
        rw.write_reports(
            console_format=fmt,
            output_files=outputs,
            quiet=getattr(args, "quiet", False),
            logger=logger,
        )
    elif outputs:
        rw.write_reports(
            console_format="md",
            output_files=outputs,
            quiet=True,
            logger=logger,
        )

    return EXIT_SUCCESS if report.is_clean() else EXIT_ISSUES_FOUND
