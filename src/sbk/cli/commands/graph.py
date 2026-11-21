"""Implementation of 'sbk graph-health' command."""

import logging
from argparse import Namespace

from ...exceptions import SBKError, VaultKeeperError
from ...utils.formatters import ReportWriter, format_output
from ..common import get_vault
from ..constants import EXIT_ERROR, EXIT_SUCCESS


def handle_graph_health(args: Namespace, logger: logging.Logger) -> int:
    """Execute non-punitive topological graph analysis."""
    v = get_vault(args, logger)
    if not v:
        return EXIT_ERROR

    fmt = getattr(args, "format", "md")

    try:
        report = v.graph_health()
    except (SBKError, VaultKeeperError) as exc:
        logger.error("Graph telemetry failed: %s", exc)
        return EXIT_ERROR

    lines = [
        "# Diagnostica Topologica del Grafo Concettuale",
        "",
        "> [!NOTE] Diagnostica Non-Punitiva",
        "> I valori riportati hanno scopo puramente informativo ed esplorativo.",
        "> Nessuna penalita' viene applicata al Vault Health Score di audit.",
        "",
        f"- **Totale Nodi (Note):** {report.total_nodes}",
        f"- **Totale Archi (Collegamenti):** {report.total_edges}",
        f"- **Note Isolate (True Orphans):** {len(report.true_orphans)}",
        f"- **Vicoli Ciechi (Dead-Ends):** {len(report.dead_ends)}",
        f"- **Componenti Disconnesse (<=3 note):** {len(report.disconnected_components)}",
        "",
        "## Top 10 Note Piu' Collegate (Hub)",
        "",
    ]

    if report.top_hubs:
        hub_rows = [
            {
                "Nota": f"[[{h.stem}]]",
                "Backlink in Ingresso": h.in_degree,
                "Link in Uscita": h.out_degree,
            }
            for h in report.top_hubs
        ]
        lines.append(
            format_output(
                hub_rows,
                format="md",
                headers=["Nota", "Backlink in Ingresso", "Link in Uscita"],
            )
        )
    else:
        lines.append("*(Nessun hub rilevato con collegamenti in ingresso)*")

    lines.extend(["", "## Note Isolate (Senza link ne' indice)", ""])
    if report.true_orphans:
        for o in report.true_orphans:
            lines.append(f"- [[{o}]]")
    else:
        lines.append("*(Nessuna nota totalmente orfana rilevata)*")

    lines.extend(["", "## Vicoli Ciechi (Zero link uscenti)", ""])
    if report.dead_ends:
        for de in report.dead_ends[:20]:
            lines.append(f"- [[{de}]]")
        if len(report.dead_ends) > 20:
            lines.append(f"*... e altri {len(report.dead_ends) - 20} vicoli ciechi*")
    else:
        lines.append("*(Nessun vicolo cieco rilevato)*")

    outputs = ReportWriter.extract_outputs(args)

    rw = ReportWriter(
        data=report.to_dict(),
        md_rendered="\n".join(lines),
        title="Diagnostica Topologica del Grafo Concettuale",
    )
    rw.write_reports(
        console_format=fmt,
        output_files=outputs,
        quiet=getattr(args, "quiet", False),
        logger=logger,
    )
    return EXIT_SUCCESS
