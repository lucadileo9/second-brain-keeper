"""Tests for utility helpers."""

from pathlib import Path

from sbk.utils.helpers import compute_file_hash, format_bytes, resolve_vault_path, truncate_text


def test_format_bytes() -> None:
    """Verify human readable byte formatting."""
    assert format_bytes(100) == "100 B"
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1048576) == "1.00 MB"
    assert format_bytes(1073741824) == "1.00 GB"


def test_truncate_text() -> None:
    """Verify text truncation at word boundaries."""
    text = "Questo e' un testo sufficientemente lungo per testare il troncamento."
    assert truncate_text(text, 20) == "Questo e' un testo..."
    assert truncate_text("Breve", 20) == "Breve"


def test_compute_file_hash(empty_temp_dir: Path) -> None:
    """Verify SHA256 hash calculation."""
    f = empty_temp_dir / "sample.txt"
    f.write_text("Hello World", encoding="utf-8")
    h = compute_file_hash(f)
    assert len(h) == 64
    assert isinstance(h, str)


def test_is_ignored_path() -> None:
    """Verify ignored path filter."""
    from sbk.core.traversal import is_ignored_path

    ignored = {".obsidian", ".trash", "node_modules"}
    assert is_ignored_path(Path("/vault/.obsidian/plugins"), ignored) is True
    assert is_ignored_path(Path("/vault/10-19_Progetti/Note.md"), ignored) is False
    assert is_ignored_path(Path("/vault/.hidden_folder"), ignored) is True


def test_resolve_vault_path(empty_temp_dir: Path) -> None:
    """Verify resolve_vault_path anchors relative paths and preserves absolute paths."""
    vault_root = empty_temp_dir / "MyVault"
    vault_root.mkdir()
    sub = vault_root / "10-19_Progetti"
    sub.mkdir()
    target_file = sub / "Nota.md"
    target_file.touch()

    # Relative string
    res_str = resolve_vault_path("10-19_Progetti/Nota.md", vault_root)
    assert res_str == target_file.resolve()

    # Relative Path
    res_path = resolve_vault_path(Path("10-19_Progetti/Nota.md"), vault_root)
    assert res_path == target_file.resolve()

    # Absolute path
    res_abs = resolve_vault_path(target_file.resolve(), vault_root)
    assert res_abs == target_file.resolve()

    # Path with relative navigation (..)
    res_nav = resolve_vault_path("10-19_Progetti/../10-19_Progetti/Nota.md", vault_root)
    assert res_nav == target_file.resolve()
