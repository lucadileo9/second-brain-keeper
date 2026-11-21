"""Isolated sandbox vault generator and lifecycle reset engine for safe testing."""

import shutil
from pathlib import Path
from typing import Optional

from ..config import generate_default_config_content


def get_default_sandbox_path() -> Path:
    """Return the default system sandbox directory path."""
    return Path.home() / ".sbk" / "sandbox"


def init_sandbox(target_path: Optional[Path] = None, force: bool = False) -> Path:
    """Initialize a fully functional, self-contained mock Obsidian vault for experimentation.

    Args:
        target_path: Destination path for the sandbox vault (defaults to ~/.sbk/sandbox).
        force: Overwrite existing directory if it already exists.

    Returns:
        Absolute Path to the initialized sandbox vault root.
    """
    dest = (target_path or get_default_sandbox_path()).resolve()

    if dest.exists():
        if not force:
            raise FileExistsError(
                f"Sandbox directory already exists at: {dest}. "
                "Use 'sbk sandbox reset' to wipe and recreate it, or pass --force."
            )
        shutil.rmtree(dest)

    dest.mkdir(parents=True, exist_ok=True)

    # 1. Create standard folder structure
    (dest / "00_Inbox").mkdir(parents=True, exist_ok=True)
    (dest / "00-09_Meta").mkdir(parents=True, exist_ok=True)
    (dest / "10-19_Progetti").mkdir(parents=True, exist_ok=True)
    (dest / "20-29_Aree").mkdir(parents=True, exist_ok=True)
    (dest / "90-99_Allegati").mkdir(parents=True, exist_ok=True)
    (dest / ".obsidian").mkdir(parents=True, exist_ok=True)
    (dest / ".trash").mkdir(parents=True, exist_ok=True)

    archive_dir = dest.parent / "Archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    # 2. Write vault.toml
    config_file = dest / "vault.toml"
    config_file.write_text(generate_default_config_content(dest), encoding="utf-8")

    # 3. Write 00_Tassonomia_Tag.md
    taxonomy_file = dest / "00-09_Meta" / "00_Tassonomia_Tag.md"
    taxonomy_content = """# Tassonomia Tag del Vault

- #area/infrastruttura
- #area/sviluppo
- #area/business
- #tipo/appunto
- #tipo/progetto
- #tipo/risorsa
- #tipo/sistema
- #tipo/indice
- #stato/attivo
- #stato/completato
"""
    taxonomy_file.write_text(taxonomy_content, encoding="utf-8")

    # 4. Write sample note 1 (Progetto_Alpha.md)
    note1 = dest / "10-19_Progetti" / "Progetto_Alpha.md"
    note1_content = """---
tipo: Progetto
tags:
  - tipo/progetto
  - stato/attivo
---

# Progetto Alpha

Questo e' un progetto di test che collega [[Nota_Beta]] e [[Allegato_Documento.pdf]].
"""
    note1.write_text(note1_content, encoding="utf-8")

    # 5. Write sample note 2 (Nota_Beta.md)
    note2 = dest / "20-29_Aree" / "Nota_Beta.md"
    note2_content = """---
tipo: Appunto
tags:
  - tipo/appunto
  - area/sviluppo
---

# Nota Beta

Nota concettuale dell'area sviluppo collegata a [[Progetto_Alpha]].
"""
    note2.write_text(note2_content, encoding="utf-8")

    # 6. Write sample attachment
    attachment = dest / "90-99_Allegati" / "Allegato_Documento.pdf"
    attachment.write_bytes(b"%PDF-1.4 test dummy sandbox pdf attachment")

    return dest


def reset_sandbox(target_path: Optional[Path] = None) -> Path:
    """Wipe and re-initialize the sandbox vault to a pristine state."""
    return init_sandbox(target_path=target_path, force=True)
