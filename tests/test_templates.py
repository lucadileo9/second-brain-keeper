"""Unit and integration tests for TemplateEngine, note creation, and auto-routing."""

import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

from sbk.config import load_vault_config
from sbk.core.indices import IndexManager
from sbk.core.templates import TemplateEngine, resolve_target_folder
from sbk.exceptions import CreationError, TaxonomyError, TemplateError
from sbk.vault import Vault


@pytest.fixture
def temp_vault() -> Iterator[Path]:
    """Create a temporary sandbox vault directory tree with Johnny.Decimal folders."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        root = Path(tmp_dir).resolve()

        # 01-09 Meta / System
        meta_dir = root / "01-09_Risorse_Di_Sistema" / "01_Templates"
        meta_dir.mkdir(parents=True, exist_ok=True)

        taxonomy_content = """# Tassonomia dei Tag

## Categorie di Primo Livello
- #tipo/appunto
- #tipo/progetto
- #tipo/risorsa
- #carriera/networking
- #tech/python
- #uni/sistemi
"""
        (meta_dir / "00_Tassonomia_Tag.md").write_text(taxonomy_content, encoding="utf-8")

        # Sample templates
        tmpl_progetto = """---
tipo: Sistema
priorità: media
stato: attivo
tags:
  - sistema
---
# {{title}}

## Obiettivi del Progetto

## Task Operativi
- [ ] Inizializzare {{stem}}
"""
        (meta_dir / "Template_Progetto.md").write_text(tmpl_progetto, encoding="utf-8")

        # 10-19 Progetti
        progetti_dir = root / "10-19_Progetti"
        progetti_dir.mkdir(parents=True, exist_ok=True)
        (progetti_dir / "Progetto_Alpha.md").write_text(
            "---\ntipo: Progetto\ntags:\n  - tipo/progetto\n---\n# Progetto Alpha\n\nDescrizione.",
            encoding="utf-8",
        )

        # 20-29 Istruzione (Area)
        istruzione_dir = root / "20-29_Istruzione"
        istruzione_dir.mkdir(parents=True, exist_ok=True)

        # 30-39 Carriera / 32_CRM
        crm_dir = root / "30-39_Carriera" / "32_CRM"
        crm_dir.mkdir(parents=True, exist_ok=True)

        # Config file vault.toml
        cfg_text = f"""[vault]
root_path = "{root.as_posix()}"
allowed_extensions = [".md", ".png"]
ignored_folders = [".obsidian", ".trash", ".git"]
templates_folder = "01-09_Risorse_Di_Sistema/01_Templates"

[frontmatter]
type_field = "tipo"
allowed_types = ["Appunto", "Contatto", "Progetto", "Risorsa", "Indice", "Sistema"]

[tags]
taxonomy_file = "01-09_Risorse_Di_Sistema/01_Templates/00_Tassonomia_Tag.md"
strict_taxonomy = true
"""
        (root / "vault.toml").write_text(cfg_text, encoding="utf-8")

        yield root


def test_template_engine_discovery_and_resolution(temp_vault: Path) -> None:
    """Test template engine locates templates, lists them, and resolves paths."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    templates = engine.list_templates()
    assert "Template_Progetto.md" in templates
    assert "00_Tassonomia_Tag.md" in templates

    # Resolution by exact name or stem (without magic prefixing)
    p1 = engine.resolve_template_path("Template_Progetto.md")
    assert p1 is not None and p1.name == "Template_Progetto.md"

    p2 = engine.resolve_template_path("Template_Progetto")
    assert p2 is not None and p2.name == "Template_Progetto.md"

    # Magic prefixing removed: 'progetto' does NOT match 'Template_Progetto.md'
    with pytest.raises(TemplateError) as exc_info:
        engine.resolve_template_path("progetto")
    assert "progetto" in str(exc_info.value)

    # None returns None (Tier 3 fallback) when default_template is not configured
    assert engine.resolve_template_path(None) is None
    assert engine.resolve_template_path("") is None

    # Missing template raises TemplateError
    with pytest.raises(TemplateError) as exc_info:
        engine.resolve_template_path("Nonexistent_Template")
    assert "Nonexistent_Template" in str(exc_info.value)


def test_template_engine_tier2_configured_default(temp_vault: Path) -> None:
    """Test Tier 2 template resolution using configured default_template."""
    config = load_vault_config(root_path=temp_vault)
    config.default_template = "Template_Progetto.md"
    engine = TemplateEngine(config)

    # When template is None, falls back to config.default_template
    resolved = engine.resolve_template_path(None)
    assert resolved is not None and resolved.name == "Template_Progetto.md"

    # Explicit template still takes precedence over default_template
    resolved_explicit = engine.resolve_template_path("Template_Progetto")
    assert resolved_explicit is not None and resolved_explicit.name == "Template_Progetto.md"

    # When configured default template does not exist, raises TemplateError
    config.default_template = "Template_Non_Esistente.md"
    with pytest.raises(TemplateError) as exc_info:
        engine.resolve_template_path(None)
    assert "Template_Non_Esistente.md" in str(exc_info.value)


def test_template_engine_default_templates(temp_vault: Path) -> None:
    """Test built-in fallback minimal 4-line scaffold for all types."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    for tipo in ["Appunto", "Contatto", "Progetto", "Risorsa", "Indice", "Sistema", "Custom"]:
        tmpl = engine.get_default_template(tipo)
        assert f"tipo: {tipo.capitalize() if tipo != 'Custom' else tipo}" in tmpl
        assert "# {{title}}" in tmpl
        # Verify hardcoded Italian sections have been eliminated
        assert "Note e Concetti Chiave" not in tmpl
        assert "Obiettivi e Deliverable" not in tmpl
        assert "formato: libro" not in tmpl


def test_template_engine_render_variables(temp_vault: Path) -> None:
    """Test variable interpolation including date, time, stem, title, and extra vars."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    raw_tmpl = """---
tipo: Sistema
tags:
  - sistema
---
# {{ title }}
Stem: {{stem}}
Type: {{type}}
Data: {{date}}
Custom: {{client_name}}
"""
    rendered = engine.render_template(
        raw_content=raw_tmpl,
        title="Incontro con Mario Rossi",
        stem="Incontro_Con_Mario_Rossi",
        tipo="Contatto",
        tags=["carriera/networking"],
        extra_vars={"client_name": "Acme Corp"},
    )

    assert "tipo: Contatto" in rendered
    assert "carriera/networking" in rendered
    assert "sistema" not in rendered  # dummy template tag removed
    assert "# Incontro con Mario Rossi" in rendered
    assert "Stem: Incontro_Con_Mario_Rossi" in rendered
    assert "Type: Contatto" in rendered
    assert "Custom: Acme Corp" in rendered


def test_resolve_target_folder(temp_vault: Path) -> None:
    """Test deterministic inbox routing and custom folder resolution."""
    # Default inbox routing
    f_default = resolve_target_folder(temp_vault, "Progetto")
    assert f_default == (temp_vault / "00_Inbox").resolve()

    f_app = resolve_target_folder(temp_vault, "Appunto")
    assert f_app == (temp_vault / "00_Inbox").resolve()

    # Configured custom inbox folder
    f_custom_inbox = resolve_target_folder(temp_vault, "Appunto", inbox_folder="Staging")
    assert f_custom_inbox == (temp_vault / "Staging").resolve()

    # Custom valid folder
    f_custom = resolve_target_folder(temp_vault, "Appunto", custom_folder="10-19_Progetti")
    assert f_custom == (temp_vault / "10-19_Progetti").resolve()

    # Custom folder outside vault raises CreationError
    with pytest.raises(CreationError):
        resolve_target_folder(temp_vault, "Appunto", custom_folder="/tmp/outside_vault")


def test_index_manager_add_and_remove_entry(temp_vault: Path) -> None:
    """Test IndexManager add_entry and remove_entry methods."""
    config = load_vault_config(root_path=temp_vault)
    mgr = IndexManager(config)
    target_folder = temp_vault / "10-19_Progetti"

    # Initially rebuild index
    mgr.rebuild_index(target_folder)
    idx_p = mgr.get_index_path(target_folder)
    assert idx_p.is_file()
    assert "[[Progetto_Alpha]]" in idx_p.read_text(encoding="utf-8")

    # Add entry
    added = mgr.add_entry(target_folder, "Nuovo_Progetto")
    assert added is True or idx_p.is_file()

    # Remove entry
    removed = mgr.remove_entry(target_folder, "Progetto_Alpha")
    assert removed is True
    assert "[[Progetto_Alpha]]" not in idx_p.read_text(encoding="utf-8")


def test_vault_create_note_success_and_undo(temp_vault: Path) -> None:
    """Test full creation workflow: explicit folder, index update, transaction journal, and undo."""
    vault = Vault(root_path=temp_vault)

    # Pre-generate folder index so it has initial state
    IndexManager(vault.config).rebuild_index(temp_vault / "10-19_Progetti")

    res = vault.create(
        title="Nuovo Sviluppo Backend",
        tipo="Progetto",
        folder="10-19_Progetti",
        tags=["tech/python"],
        template="Template_Progetto",
    )

    assert res.stem == "Nuovo_Sviluppo_Backend"
    assert res.file_path.is_file()
    assert res.file_path.parent.name == "10-19_Progetti"
    assert res.index_updated is True
    assert res.tx_id is not None
    assert res.dry_run is False

    content = res.file_path.read_text(encoding="utf-8")
    assert "tipo: Progetto" in content
    assert "tech/python" in content
    assert "# Nuovo Sviluppo Backend" in content
    assert "Inizializzare Nuovo_Sviluppo_Backend" in content

    # Check folder index includes new note
    idx_p = res.index_path
    assert idx_p is not None and idx_p.is_file()
    idx_content = idx_p.read_text(encoding="utf-8")
    assert "[[Nuovo_Sviluppo_Backend]]" in idx_content

    # Undo operation
    undo_res = vault.undo()
    assert undo_res.success is True
    assert not res.file_path.exists()

    # Folder index should have been reverted
    reverted_idx_content = idx_p.read_text(encoding="utf-8")
    assert "[[Nuovo_Sviluppo_Backend]]" not in reverted_idx_content


def test_vault_create_default_inbox(temp_vault: Path) -> None:
    """Verify default note creation lands deterministically in 00_Inbox."""
    vault = Vault(root_path=temp_vault)
    res = vault.create(title="Idea Rapida", tipo="Appunto")
    assert res.file_path.parent == (temp_vault / "00_Inbox").resolve()
    assert res.file_path.is_file()


def test_vault_create_dry_run(temp_vault: Path) -> None:
    """Test dry-run simulation of note creation."""
    vault = Vault(root_path=temp_vault)

    res = vault.create(
        title="Bozza Idea Innovativa",
        tipo="Appunto",
        dry_run=True,
    )

    assert res.dry_run is True
    assert not res.file_path.exists()
    assert res.tx_id is None
    assert res.stem == "Bozza_Idea_Innovativa"
    assert res.file_path.parent.name == "00_Inbox"


def test_vault_create_preflight_checks(temp_vault: Path) -> None:
    """Test pre-flight safety validations: empty title, invalid tipo, taxonomy tag error, collision."""
    vault = Vault(root_path=temp_vault)

    # Empty title
    with pytest.raises(CreationError) as exc:
        vault.create(title="   ", tipo="Appunto")
    assert "empty" in str(exc.value)

    # Invalid tipo
    with pytest.raises(CreationError) as exc:
        vault.create(title="Titolo Test", tipo="Invalido")
    assert "Invalid note type" in str(exc.value)

    # Invalid taxonomy tag
    with pytest.raises(TaxonomyError) as exc_tax:
        vault.create(title="Titolo Test", tipo="Progetto", tags=["tag/non_esistente"])
    assert "not registered in taxonomy" in str(exc_tax.value)

    # Stem collision with note in another folder
    with pytest.raises(CreationError) as exc:
        vault.create(title="Progetto Alpha", tipo="Progetto")
    assert "Stem collision" in str(exc.value)

    # Destination file collision
    dest_p = temp_vault / "10-19_Progetti" / "Collision_File.md"
    dest_p.write_text("Existing content", encoding="utf-8")
    with pytest.raises(CreationError) as exc:
        vault.create(title="Collision File", tipo="Progetto", folder="10-19_Progetti")
    assert "already exists at destination" in str(exc.value)


def test_template_engine_additional_edge_cases(temp_vault: Path) -> None:
    """Test explicit template path, missing template dir, unknown variable, and default tags cleanup."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    # Explicit relative and absolute path
    tmpl_abs = (temp_vault / "01-09_Risorse_Di_Sistema" / "01_Templates" / "Template_Progetto.md").resolve()
    assert engine.find_template(str(tmpl_abs)) == tmpl_abs
    assert engine.find_template("01-09_Risorse_Di_Sistema/01_Templates/Template_Progetto.md") == tmpl_abs

    # Unknown variable remains unchanged
    rendered = engine.render_template(
        raw_content="# {{title}}\nUnknown: {{unknown_variable}}",
        title="Test Titolo",
        stem="Test_Titolo",
        tipo="Sistema",
        tags=None,
    )
    assert "{{unknown_variable}}" in rendered
    assert "tipo: Sistema" in rendered

    # Deterministic inbox routing when no special folders exist
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as empty_dir:
        empty_root = Path(empty_dir).resolve()
        f_fallback = resolve_target_folder(empty_root, "Progetto")
        assert f_fallback == (empty_root / "00_Inbox").resolve()

        # Missing templates directory
        empty_cfg = load_vault_config(root_path=empty_root)
        empty_engine = TemplateEngine(empty_cfg)
        assert empty_engine.list_templates() == []
        assert empty_engine.find_template("Nonexistent") is None


def test_vault_create_in_custom_folder(temp_vault: Path) -> None:
    """Test creating a note in an explicit custom folder."""
    vault = Vault(root_path=temp_vault)
    custom_dir = "20-29_Istruzione/Informatica"

    res = vault.create(
        title="Architettura Microservizi",
        tipo="Appunto",
        folder=custom_dir,
        tags=["tech/python"],
    )

    assert res.file_path.is_file()
    assert res.file_path.parent == (temp_vault / "20-29_Istruzione" / "Informatica").resolve()
    assert res.stem == "Architettura_Microservizi"
    assert (temp_vault / "20-29_Istruzione" / "Informatica" / "00_Indice_Informatica.md").resolve().is_file()


def test_template_engine_render_with_body_placeholder(temp_vault: Path) -> None:
    """Test variable interpolation when {{body}} placeholder is present."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    raw_tmpl = """---
tipo: Appunto
tags: []
---
# {{title}}

## Sintesi
{{body}}

## Note
"""
    # 1. With body
    rendered = engine.render_template(
        raw_content=raw_tmpl,
        title="Nota Con Body",
        stem="Nota_Con_Body",
        tipo="Appunto",
        body="Contenuto iniettato nel placeholder.",
    )
    assert "# Nota Con Body" in rendered
    assert "Contenuto iniettato nel placeholder." in rendered
    assert "{{body}}" not in rendered

    # 2. Without body (body=None) replaces placeholder with empty string
    rendered_empty = engine.render_template(
        raw_content=raw_tmpl,
        title="Nota Senza Body",
        stem="Nota_Senza_Body",
        tipo="Appunto",
        body=None,
    )
    assert "# Nota Senza Body" in rendered_empty
    assert "{{body}}" not in rendered_empty


def test_template_engine_render_with_body_append(temp_vault: Path) -> None:
    """Test body appended cleanly when template has no {{body}} placeholder."""
    config = load_vault_config(root_path=temp_vault)
    engine = TemplateEngine(config)

    raw_tmpl = engine.get_default_template("Appunto")
    body_text = "## Sezione Libera\n\n- Punto 1\n- Punto 2"

    rendered = engine.render_template(
        raw_content=raw_tmpl,
        title="Nota Append",
        stem="Nota_Append",
        tipo="Appunto",
        body=body_text,
    )
    assert "# Nota Append" in rendered
    assert "## Sezione Libera\n\n- Punto 1\n- Punto 2" in rendered
    assert rendered.endswith("\n## Sezione Libera\n\n- Punto 1\n- Punto 2\n")
