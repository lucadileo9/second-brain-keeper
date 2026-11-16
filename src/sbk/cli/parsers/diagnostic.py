"""Diagnostic CLI parsers: audit and graph-health."""

import argparse


def register_diagnostic_parsers(subparsers: argparse._SubParsersAction) -> None:
    """Register diagnostic subcommands (audit, graph-health)."""
    # sbk audit
    audit_parser = subparsers.add_parser("audit", help="Run 5-phase vault diagnostics and compute Health Score.")
    audit_parser.add_argument(
        "--target",
        type=str,
        default=None,
        help="Restrict audit scan to a specific note or subfolder.",
    )
    audit_parser.add_argument(
        "--step",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=None,
        help="Execute only a specific phase: Filesystem (1), Naming (2), Frontmatter (3), Taxonomy (4), Referential Integrity (5).",
    )
    audit_parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="md",
        choices=["md", "json", "yaml"],
        help="Console output format (default: md).",
    )
    audit_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Export audit report to file (format auto-detected: .md, .json, .yaml). Can be specified multiple times.",
    )
    audit_parser.add_argument("--json", type=str, default=None, help="Export diagnostic results to a JSON file.")
    audit_parser.add_argument(
        "--report-md", type=str, default=None, help="Export diagnostic results to a Markdown report."
    )

    # sbk graph-health
    graph_parser = subparsers.add_parser("graph-health", help="Execute non-punitive topological graph diagnostics.")
    graph_parser.add_argument(
        "--format", type=str, default="md", choices=["md", "json", "yaml"], help="Output format."
    )
    graph_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Export graph report to file (format auto-detected). Can be specified multiple times.",
    )
