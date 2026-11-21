"""Governance CLI parsers: clean-attachments, normalize-names, generate-indices, frontmatter, tags."""

import argparse


def register_governance_parsers(subparsers: argparse._SubParsersAction) -> None:
    """Register governance and taxonomy subcommands."""
    # sbk clean-attachments
    att_parser = subparsers.add_parser("clean-attachments", help="Find and clean orphan media attachments.")
    att_parser.add_argument("--target", type=str, default=None, help="Restrict search to a specific directory.")
    att_parser.add_argument("--dry-run", action="store_true", help="Simulate deletion without touching disk files.")
    att_parser.add_argument(
        "--hard-delete", action="store_true", help="Permanently delete files instead of moving to .trash."
    )

    # sbk normalize-names
    naming_parser = subparsers.add_parser(
        "normalize-names", help="Normalize note and file names according to naming style."
    )
    naming_parser.add_argument(
        "--target", type=str, default=None, help="Restrict normalization to a specific directory."
    )
    naming_parser.add_argument("--dry-run", action="store_true", help="Simulate normalization without renaming files.")

    # sbk generate-indices
    indices_parser = subparsers.add_parser("generate-indices", help="Generate or update folder MOC index notes.")
    indices_parser.add_argument("--target", type=str, default=None, help="Specific folder to generate index for.")
    indices_parser.add_argument(
        "--all", action="store_true", help="Recursively generate indices for all subdirectories."
    )
    indices_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate index generation without writing to disk."
    )

    # sbk frontmatter
    fm_parser = subparsers.add_parser("frontmatter", help="Inspect and manipulate YAML frontmatter.")
    fm_subparsers = fm_parser.add_subparsers(dest="fm_action", help="Frontmatter actions")

    set_type_parser = fm_subparsers.add_parser("set-type", help="Set or update the tipo frontmatter field.")
    set_type_parser.add_argument(
        "--target", type=str, required=False, default=None, help="Path to target markdown note."
    )
    set_type_parser.add_argument(
        "--type", type=str, required=False, default=None, help="Type value (e.g. Appunto, Progetto, Risorsa)."
    )
    set_type_parser.add_argument(
        "--batch",
        type=str,
        default=None,
        help="Path to JSON file mapping notes to note types ({note_path: type}).",
    )
    set_type_parser.add_argument("--dry-run", action="store_true", help="Simulate change without writing to disk.")

    add_tags_parser = fm_subparsers.add_parser("add-tags", help="Add tags to frontmatter.")
    add_tags_parser.add_argument(
        "--target", type=str, required=False, default=None, help="Path to target markdown note."
    )
    add_tags_parser.add_argument("--tags", nargs="+", required=False, default=None, help="One or more tags to inject.")
    add_tags_parser.add_argument(
        "--batch",
        type=str,
        default=None,
        help="Path to JSON file mapping notes to tag lists ({note_path: [tags...]}).",
    )
    add_tags_parser.add_argument("--overwrite", action="store_true", help="Replace existing tags instead of appending.")
    add_tags_parser.add_argument("--dry-run", action="store_true", help="Simulate change without writing to disk.")

    sanitize_tags_parser = fm_subparsers.add_parser("sanitize-tags", help="Sanitize tags based on taxonomy mapping.")
    sanitize_tags_parser.add_argument("--target", type=str, default=None, help="Restrict scan to a specific folder.")
    sanitize_tags_parser.add_argument("--dry-run", action="store_true", help="Simulate sanitization without saving.")

    # sbk tags
    tags_parser = subparsers.add_parser("tags", help="Inspect and manipulate controlled tag taxonomy.")
    tags_subparsers = tags_parser.add_subparsers(dest="tag_action", help="Tag action")

    tags_show_parser = tags_subparsers.add_parser("show", help="List registered taxonomy tags.")
    tags_show_parser.add_argument("--query", type=str, default=None, help="Filter tags matching search query.")
    tags_show_parser.add_argument(
        "--format", type=str, default="md", choices=["md", "json", "yaml", "csv"], help="Output format."
    )
    tags_show_parser.add_argument(
        "-o",
        "--output",
        action="append",
        dest="outputs",
        default=[],
        help="Export tag list to file (format auto-detected). Can be specified multiple times.",
    )

    tags_add_parser = tags_subparsers.add_parser("add", help="Add a tag into 00_Tassonomia_Tag.md.")
    tags_add_parser.add_argument("tag", type=str, help="Tag name to add (e.g. area/ricerca).")
    tags_add_parser.add_argument("--section", type=str, default=None, help="Section heading to insert under.")
    tags_add_parser.add_argument("--dry-run", action="store_true", help="Simulate tag insertion without saving.")

    tags_rm_parser = tags_subparsers.add_parser("remove", help="Remove a tag from 00_Tassonomia_Tag.md.")
    tags_rm_parser.add_argument("tag", type=str, help="Tag name to remove.")
    tags_rm_parser.add_argument("--force", action="store_true", help="Force removal even if referenced in notes.")
    tags_rm_parser.add_argument("--dry-run", action="store_true", help="Simulate tag removal without saving.")
