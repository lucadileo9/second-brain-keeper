"""Maintenance CLI parsers: init, history, undo, redo, config, search, map, sandbox."""

import argparse


def register_maintenance_parsers(subparsers: argparse._SubParsersAction) -> None:
    """Register maintenance and support subcommands."""
    # sbk init
    init_parser = subparsers.add_parser("init", help="Initialize a default vault.toml configuration file.")
    init_parser.add_argument("--target", type=str, default=None, help="Directory to initialize vault.toml in.")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing configuration file.")

    # sbk history
    history_parser = subparsers.add_parser("history", help="List historical vaultkeeper transactions.")
    history_parser.add_argument("--limit", type=int, default=20, help="Maximum number of transactions to list.")
    history_parser.add_argument(
        "--format",
        type=str,
        default="md",
        choices=["md", "json", "yaml", "csv"],
        help="Output format (default: md).",
    )
    history_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Export transaction history to file (format auto-detected). Can be specified multiple times.",
    )

    # sbk undo
    undo_parser = subparsers.add_parser("undo", help="Revert the most recent or specified transaction.")
    undo_parser.add_argument(
        "--tx",
        type=str,
        default=None,
        help="Specific transaction ID to revert (default: latest active transaction).",
    )
    undo_parser.add_argument("--dry-run", action="store_true", help="Preview undo actions without modifying files.")

    # sbk redo
    redo_parser = subparsers.add_parser("redo", help="Reapply the most recently undone transaction.")
    redo_parser.add_argument(
        "--tx",
        type=str,
        default=None,
        help="Specific transaction ID to reapply (default: latest reverted transaction).",
    )
    redo_parser.add_argument("--dry-run", action="store_true", help="Preview redo actions without modifying files.")

    # sbk config
    config_parser = subparsers.add_parser("config", help="Inspect and update vault configuration directives.")
    config_subparsers = config_parser.add_subparsers(dest="config_action", help="Config action")

    config_show_parser = config_subparsers.add_parser("show", help="Display active configuration settings.")
    config_show_parser.add_argument(
        "--format", type=str, default="yaml", choices=["yaml", "json", "md"], help="Output format."
    )

    config_set_parser = config_subparsers.add_parser("set", help="Update a directive in vault.toml.")
    config_set_parser.add_argument("key", type=str, help="Configuration key path (e.g. naming.style).")
    config_set_parser.add_argument("value", type=str, help="New value to set.")
    config_set_parser.add_argument("--dry-run", action="store_true", help="Simulate configuration update.")

    # sbk search
    search_parser = subparsers.add_parser("search", help="Execute semantic query and filter search across notes.")
    search_parser.add_argument("query", nargs="?", default=None, type=str, help="Optional text search query.")
    search_parser.add_argument("--tag", type=str, default=None, help="Filter by tag (frontmatter or inline).")
    search_parser.add_argument("--type", type=str, default=None, help="Filter by note frontmatter tipo.")
    search_parser.add_argument("--links-to", type=str, default=None, help="Filter notes linking to target stem.")
    search_parser.add_argument("--folder", type=str, default=None, help="Restrict search to a folder path.")
    search_parser.add_argument(
        "--format", type=str, default="md", choices=["md", "json", "yaml", "csv"], help="Output format."
    )
    search_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Export search results to file (format auto-detected). Can be specified multiple times.",
    )

    # sbk map
    map_parser = subparsers.add_parser("map", help="Generate Johnny.Decimal area telemetry and master vault map.")
    map_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Output path for master MOC markdown note or exports. Can be specified multiple times.",
    )
    map_parser.add_argument(
        "--format", type=str, default="md", choices=["md", "json", "yaml"], help="Output format."
    )

    # sbk sandbox
    sandbox_parser = subparsers.add_parser("sandbox", help="Manage isolated testing sandbox environments.")
    sandbox_sub = sandbox_parser.add_subparsers(dest="sandbox_action", help="Sandbox actions")

    sb_init = sandbox_sub.add_parser("init", help="Initialize an isolated sandbox vault.")
    sb_init.add_argument("--target", type=str, default=None, help="Target directory (defaults to ~/.sbk/sandbox).")
    sb_init.add_argument("--force", action="store_true", help="Overwrite existing sandbox directory.")

    sb_reset = sandbox_sub.add_parser("reset", help="Reset sandbox vault to a pristine clean state.")
    sb_reset.add_argument("--target", type=str, default=None, help="Target directory (defaults to ~/.sbk/sandbox).")

    sb_path = sandbox_sub.add_parser("path", help="Print absolute path to the sandbox vault directory.")
    sb_path.add_argument("--target", type=str, default=None, help="Target directory (defaults to ~/.sbk/sandbox).")
