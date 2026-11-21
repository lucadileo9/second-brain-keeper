"""Lifecycle CLI parsers: create, rename, move, archive, and offload."""

import argparse


def register_lifecycle_parsers(subparsers: argparse._SubParsersAction) -> None:
    """Register lifecycle subcommands."""
    # sbk create
    create_parser = subparsers.add_parser(
        "create", help="Create a standardized note using templates, validation, and auto-routing."
    )
    create_parser.add_argument("title", type=str, help="Title of the new note.")
    create_parser.add_argument(
        "--type",
        dest="tipo",
        type=str,
        required=True,
        help="Note frontmatter tipo (e.g. Appunto, Progetto, Contatto, Risorsa).",
    )
    create_parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Target folder path (relative to vault root or Johnny.Decimal auto-routed).",
    )
    create_parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Comma-separated taxonomy tags (e.g. 'tech/python,uni/tesi').",
    )
    create_parser.add_argument(
        "--template",
        type=str,
        default=None,
        help="Template name, filename, or explicit path to instantiate from.",
    )
    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate creation and index update without modifying disk files.",
    )
    create_parser.add_argument(
        "--format",
        type=str,
        default="md",
        choices=["md", "json", "yaml", "csv"],
        help="Output format (default: md).",
    )
    body_group = create_parser.add_mutually_exclusive_group(required=False)
    body_group.add_argument(
        "--body",
        type=str,
        default=None,
        help="Initial markdown body text to inject into the note.",
    )
    body_group.add_argument(
        "--body-file",
        type=str,
        default=None,
        help="Path to an existing UTF-8 text file whose content will be injected into the note body.",
    )

    # sbk rename
    rename_parser = subparsers.add_parser("rename", help="Rename a note or asset with global wikilink refactoring.")
    rename_parser.add_argument("file", nargs="?", default=None, type=str, help="Path of the file to rename.")
    rename_parser.add_argument(
        "new_name",
        nargs="?",
        default=None,
        type=str,
        help="New file name (not a path, e.g. Note_Name.md). To move files use 'sbk move'.",
    )
    rename_parser.add_argument(
        "--batch",
        type=str,
        default=None,
        help="Path to JSON file mapping old paths to new names ({old_path: new_name}).",
    )
    rename_parser.add_argument(
        "--skip-links",
        action="store_true",
        help="Skip refactoring incoming wikilinks across other notes.",
    )
    rename_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate rename and refactoring without modifying files.",
    )

    # sbk move
    move_parser = subparsers.add_parser(
        "move", help="Move a note or folder into a different directory and update indices."
    )
    move_parser.add_argument("target", nargs="?", default=None, type=str, help="Path of the file or folder to move.")
    move_parser.add_argument("destination", nargs="?", default=None, type=str, help="Destination directory path.")
    move_parser.add_argument(
        "--batch",
        type=str,
        default=None,
        help="Path to JSON file mapping sources to destination folders ({source_path: dest_folder}).",
    )
    move_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate move without altering filesystem.",
    )

    # sbk archive
    archive_parser = subparsers.add_parser(
        "archive", help="Archive a note or project to mirror cold storage with Tombstone support."
    )
    archive_parser.add_argument("target", type=str, help="Path of the file or directory to archive.")
    archive_parser.add_argument(
        "--no-tombstone",
        action="store_true",
        help="Do not create a tombstone note in the active vault.",
    )
    archive_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate archiving without moving files.",
    )

    # sbk offload
    offload_parser = subparsers.add_parser(
        "offload", help="Offload heavy binary assets to cold storage and replace embeds with external links."
    )
    offload_parser.add_argument(
        "target",
        nargs="?",
        default=None,
        type=str,
        help="Specific file or directory to offload (default: all files exceeding threshold).",
    )
    offload_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate offloading without moving files.",
    )
