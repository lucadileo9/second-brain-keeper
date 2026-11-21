"""Main CLI entrypoint and argument parser for the sbk command."""

import argparse
import sys
from typing import List, Optional

from .. import __version__
from .commands.archive import handle_archive
from .commands.attachments import handle_attachments
from .commands.audit import handle_audit
from .commands.config import handle_config
from .commands.create import handle_create
from .commands.frontmatter import handle_frontmatter
from .commands.graph import handle_graph_health
from .commands.history import handle_history
from .commands.indices import handle_indices
from .commands.init import handle_init
from .commands.map import handle_map
from .commands.move import handle_move
from .commands.naming import handle_naming
from .commands.offload import handle_offload
from .commands.redo import handle_redo
from .commands.rename import handle_rename
from .commands.sandbox import handle_sandbox
from .commands.search import handle_search
from .commands.tags import handle_tags
from .commands.undo import handle_undo
from .logging import close_cli_logger, setup_cli_logger
from .parsers import (
    register_diagnostic_parsers,
    register_governance_parsers,
    register_lifecycle_parsers,
    register_maintenance_parsers,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser for sbk."""
    parser = argparse.ArgumentParser(
        prog="sbk",
        description="Universal Second Brain governance engine and maintenance CLI for Obsidian vaults.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug logging output.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress informational output, displaying errors only.",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to an optional plain-text logfile to record operational history.",
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Override vault root directory path.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Explicit path to vault.toml or config.toml.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    register_diagnostic_parsers(subparsers)
    register_lifecycle_parsers(subparsers)
    register_governance_parsers(subparsers)
    register_maintenance_parsers(subparsers)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entrypoint execution function."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "rename" and not getattr(args, "batch", None) and (not args.file or not args.new_name):
        parser.error("the following arguments are required: file, new_name (or use --batch)")

    if args.command == "move" and not getattr(args, "batch", None) and (not args.target or not args.destination):
        parser.error("the following arguments are required: target, destination (or use --batch)")

    if args.command == "frontmatter":
        if args.fm_action == "set-type" and not getattr(args, "batch", None) and (not args.target or not args.type):
            parser.error("the following arguments are required: --target, --type (or use --batch)")
        elif args.fm_action == "add-tags" and not getattr(args, "batch", None) and (not args.target or not args.tags):
            parser.error("the following arguments are required: --target, --tags (or use --batch)")

    logger = setup_cli_logger(
        name="sbk",
        verbose=args.verbose,
        quiet=args.quiet,
        log_file=args.log_file,
    )

    try:
        if not args.command:
            parser.print_help()
            return 0

        command_handlers = {
            "init": handle_init,
            "audit": handle_audit,
            "clean-attachments": handle_attachments,
            "normalize-names": handle_naming,
            "generate-indices": handle_indices,
            "frontmatter": handle_frontmatter,
            "history": handle_history,
            "undo": handle_undo,
            "redo": handle_redo,
            "rename": handle_rename,
            "move": handle_move,
            "archive": handle_archive,
            "offload": handle_offload,
            "tags": handle_tags,
            "config": handle_config,
            "search": handle_search,
            "graph-health": handle_graph_health,
            "map": handle_map,
            "create": handle_create,
            "sandbox": handle_sandbox,
        }

        handler = command_handlers.get(args.command)
        if handler:
            try:
                return handler(args, logger)
            except Exception as exc:
                logger.error("Command execution failed: %s", exc)
                return 1

        parser.print_help()
        return 0
    finally:
        close_cli_logger(logger)


if __name__ == "__main__":
    sys.exit(main())
