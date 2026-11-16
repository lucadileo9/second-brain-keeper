"""Implementation of 'sbk history' command."""

import logging
from argparse import Namespace
from typing import Any, Dict, List

from ...utils.formatters import OutputFormat, ReportWriter, format_output
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_history(args: Namespace, logger: logging.Logger) -> int:
    """List historical vaultkeeper transactions."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    limit = getattr(args, "limit", 20)
    fmt_str = getattr(args, "format", "md")
    fmt = OutputFormat.from_str(fmt_str)

    records = v.history(limit=limit)
    if not records:
        if fmt == OutputFormat.MD:
            logger.info("Nessuna transazione registrata nella cronologia.")
        else:
            print(format_output([], format=fmt))
        return EXIT_SUCCESS

    # Prepare tabular projection
    data: List[Dict[str, Any]] = []
    for r in records:
        status = "Reverted" if r.reverted else "Active"
        data.append(
            {
                "Transaction ID": r.tx_id,
                "Timestamp": r.timestamp[:19].replace("T", " "),
                "Command": r.command,
                "Status": status,
                "Actions": len(r.actions),
                "Description": r.description or "-",
            }
        )

    outputs = ReportWriter.extract_outputs(args)

    rw = ReportWriter(
        data=data,
        headers=["Transaction ID", "Timestamp", "Command", "Status", "Actions", "Description"],
        title="Cronologia Transazioni VaultKeeper",
    )
    rw.write_reports(
        console_format=fmt,
        output_files=outputs,
        quiet=getattr(args, "quiet", False),
        logger=logger,
    )
    return EXIT_SUCCESS
