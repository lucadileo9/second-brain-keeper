"""Unit and integration tests for the sbk sandbox engine and CLI commands."""

from pathlib import Path

import pytest

from sbk.cli.main import main
from sbk.core.sandbox import init_sandbox, reset_sandbox


def test_sandbox_init_nominal_and_force(empty_temp_dir: Path) -> None:
    """Verify sandbox initialization creates all standard folders, notes, and attachments."""
    sb_dir = empty_temp_dir / "TestSandbox"
    created = init_sandbox(target_path=sb_dir)

    assert created == sb_dir
    assert (sb_dir / "vault.toml").is_file()
    assert (sb_dir / "00_Inbox").is_dir()
    assert (sb_dir / "00-09_Meta" / "00_Tassonomia_Tag.md").is_file()
    assert (sb_dir / "10-19_Progetti" / "Progetto_Alpha.md").is_file()
    assert (sb_dir / "20-29_Aree" / "Nota_Beta.md").is_file()
    assert (sb_dir / "90-99_Allegati" / "Allegato_Documento.pdf").is_file()

    # Repeated init without force raises FileExistsError
    with pytest.raises(FileExistsError, match="Sandbox directory already exists"):
        init_sandbox(target_path=sb_dir, force=False)

    # With force=True overwrites cleanly
    recreated = init_sandbox(target_path=sb_dir, force=True)
    assert recreated == sb_dir
    assert (sb_dir / "vault.toml").is_file()


def test_sandbox_reset(empty_temp_dir: Path) -> None:
    """Verify sandbox reset eliminates dirtied state and restores clean template."""
    sb_dir = empty_temp_dir / "TestSandbox"
    init_sandbox(target_path=sb_dir)

    # Dirty the sandbox
    dirty_note = sb_dir / "00_Inbox" / "Messy_Note.md"
    dirty_note.write_text("temporary mess", encoding="utf-8")
    (sb_dir / "10-19_Progetti" / "Progetto_Alpha.md").unlink()

    assert dirty_note.exists()
    assert not (sb_dir / "10-19_Progetti" / "Progetto_Alpha.md").exists()

    # Reset
    reset_sandbox(target_path=sb_dir)

    assert not dirty_note.exists()
    assert (sb_dir / "10-19_Progetti" / "Progetto_Alpha.md").is_file()


def test_cli_sandbox_commands(empty_temp_dir: Path, capsys) -> None:
    """Verify CLI subcommands: sbk sandbox path, init, reset."""
    sb_dir = empty_temp_dir / "CliSandbox"

    # 1. No action specified
    assert main(["sandbox"]) != 0

    # 2. Path action
    capsys.readouterr()
    code_path = main(["sandbox", "path", "--target", str(sb_dir)])
    assert code_path == 0
    assert str(sb_dir.resolve()) in capsys.readouterr().out

    # 3. Init action
    code_init = main(["sandbox", "init", "--target", str(sb_dir)])
    assert code_init == 0
    assert (sb_dir / "vault.toml").is_file()

    # 4. Init collision without force fails
    code_init_dup = main(["sandbox", "init", "--target", str(sb_dir)])
    assert code_init_dup == 1

    # 5. Reset action
    code_reset = main(["sandbox", "reset", "--target", str(sb_dir)])
    assert code_reset == 0
    assert (sb_dir / "vault.toml").is_file()
