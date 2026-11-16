"""Naming normalization strategy pattern and global wikilink synchronization."""

import re
from pathlib import Path
from typing import Any, List, Optional, Set, Tuple

from ..exceptions import NamingError
from ..models import VaultCatalog, VaultConfig
from .traversal import walk_vault_files


def clean_disallowed_characters(text: str, disallowed_regex: str) -> str:
    """Remove disallowed punctuation and symbols from filename string."""
    pattern = re.compile(disallowed_regex)
    return pattern.sub("", text)


def normalize_words_title_case(stem: str, acronyms: Set[str]) -> str:
    """Convert words to Title_Case with underscores while preserving uppercase acronyms."""
    # Split by spaces, underscores, or hyphens
    tokens = [t for t in re.split(r"[\s_\-]+", stem) if t]
    norm_tokens = []

    for token in tokens:
        upper = token.upper()
        if upper in acronyms:
            norm_tokens.append(upper)
        else:
            # Capitalize first letter, keep lowercase remainder
            norm_tokens.append(token[:1].upper() + token[1:].lower())

    return "_".join(norm_tokens)


def normalize_words_kebab_case(stem: str) -> str:
    """Convert stem to kebab-case with hyphens."""
    tokens = [t.lower() for t in re.split(r"[\s_\-]+", stem) if t]
    return "-".join(tokens)


def normalize_words_snake_case(stem: str) -> str:
    """Convert stem to snake_case with underscores."""
    tokens = [t.lower() for t in re.split(r"[\s_\-]+", stem) if t]
    return "_".join(tokens)


def normalize_stem(stem: str, config: VaultConfig) -> str:
    """Normalize a filename stem according to the configured naming strategy."""
    if config.naming_style == "none":
        return stem

    # Strip disallowed characters
    cleaned = clean_disallowed_characters(stem, config.disallowed_chars_regex)

    # Check for prefix preservation (e.g. "00_", "10-19_")
    prefix = ""
    prefix_match = re.match(config.preserve_prefix_pattern, cleaned)
    if prefix_match:
        prefix = prefix_match.group(0)
        remainder = cleaned[len(prefix) :]
    else:
        remainder = cleaned

    if config.naming_style == "Title_Case":
        norm_body = normalize_words_title_case(remainder, config.acronyms)
        res = f"{prefix}{norm_body}" if prefix else norm_body
    elif config.naming_style == "kebab-case":
        norm_body = normalize_words_kebab_case(remainder)
        res = f"{prefix.lower()}{norm_body}" if prefix else norm_body
    elif config.naming_style == "snake_case":
        norm_body = normalize_words_snake_case(remainder)
        res = f"{prefix.lower()}{norm_body}" if prefix else norm_body
    else:
        res = cleaned

    # Collapse multiple consecutive underscores or hyphens
    res = re.sub(r"_+", "_", res)
    res = re.sub(r"-+", "-", res)
    return res.strip(" _-")


def normalize_name(filename_or_folder: str, config: VaultConfig, is_directory: bool = False) -> str:
    """Normalize a file or directory name."""
    if is_directory or "." not in filename_or_folder:
        return normalize_stem(filename_or_folder, config)

    # For files with extension
    p = Path(filename_or_folder)
    stem = p.stem
    ext = p.suffix
    norm_stem = normalize_stem(stem, config)
    return f"{norm_stem}{ext}"


def update_wikilinks_in_content(
    content: str,
    old_target: str,
    new_target: str,
) -> Tuple[str, int]:
    """Replace all wikilinks referencing old_target with new_target.

    Handles [[OldTarget]], [[OldTarget|Alias]], [[OldTarget#Anchor]], and ![[OldTarget]].
    Returns (new_content, count_of_replacements).
    """
    count = 0
    # Escape old target for regex
    escaped_old = re.escape(old_target)

    # Match [[old_target(#anchor)?(|alias)?]] or ![[...]]
    pattern = re.compile(r"(!?\[\[)" + escaped_old + r"((?:#[^\]|]*)?)((?:\|[^\]]*)?)(\]\])")

    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        prefix = m.group(1)
        anchor = m.group(2)
        alias = m.group(3)
        suffix = m.group(4)
        return f"{prefix}{new_target}{anchor}{alias}{suffix}"

    new_content = pattern.sub(repl, content)
    return new_content, count


def rename_vault_item(
    catalog: VaultCatalog,
    config: VaultConfig,
    old_path: Path,
    new_name: str,
    dry_run: bool = False,
    transaction: Optional[Any] = None,
) -> Tuple[Path, int]:
    """Rename a file or folder and synchronize all incoming wikilinks and folder indices.

    Maintained as a convenience helper; delegates directly to lifecycle.rename_item.
    """
    from .indices import IndexManager
    from .lifecycle import rename_item
    from .links import WikilinkEngine

    res = rename_item(
        catalog=catalog,
        config=config,
        index_manager=IndexManager(config),
        wikilink_engine=WikilinkEngine(config),
        source_path=old_path,
        new_name=new_name,
        skip_links=False,
        transaction=transaction,
        dry_run=dry_run,
    )
    return res.new_path, res.updated_links_count


def batch_normalize(
    catalog: VaultCatalog,
    config: VaultConfig,
    target_dir: Optional[Path] = None,
    dry_run: bool = False,
    transaction: Optional[Any] = None,
) -> List[Tuple[Path, Path, int]]:
    """Scan and normalize all file and directory names in target directory.

    Synchronizes wikilinks, H1 headings, and folder indices (00_Indice.md).
    Returns list of:
        (old_path, new_path, updated_links_count)
    """
    from .indices import IndexManager
    from .lifecycle import rename_item
    from .links import WikilinkEngine

    idx_mgr = IndexManager(config)
    wl_engine = WikilinkEngine(config)

    results: List[Tuple[Path, Path, int]] = []
    root = target_dir or config.root_path

    # First normalize files
    for file_path in list(walk_vault_files(config, target_dir=root, extensions=None)):
        norm_fname = normalize_name(file_path.name, config, is_directory=False)
        if norm_fname != file_path.name:
            res = rename_item(
                catalog=catalog,
                config=config,
                index_manager=idx_mgr,
                wikilink_engine=wl_engine,
                source_path=file_path,
                new_name=norm_fname,
                skip_links=False,
                transaction=transaction,
                dry_run=dry_run,
            )
            results.append((file_path, res.new_path, res.updated_links_count))

    return results
