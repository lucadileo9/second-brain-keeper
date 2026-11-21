"""Unit tests for the 5-phase audit diagnostics engine."""

from pathlib import Path

from sbk.config import load_vault_config
from sbk.core.audit import compute_health_score, run_audit
from sbk.models import PhaseResult


def test_run_full_audit(mock_vault: Path) -> None:
    """Verify running full 5-phase audit on mock vault."""
    cfg = load_vault_config(root_path=mock_vault)
    report = run_audit(cfg)

    assert report.vault_root == mock_vault
    assert len(report.phases) == 5
    assert report.total_issues > 0  # Broken link [[Nota_Inesistente]] should be an issue
    assert report.health_score < 100.0

    # Phase 5 should contain broken link
    phase5 = report.phases[4]
    assert phase5.phase_id == 5
    assert len(phase5.issues) >= 1
    assert any("Nota_Inesistente" in is_msg for is_msg in phase5.issues)

    # Convert to dict
    d = report.to_dict()
    assert "health_score" in d
    assert len(d["phases"]) == 5


def test_compute_health_score_clean() -> None:
    """Verify health score is 100.0 for clean vault."""
    phases = [PhaseResult(phase_id=i, title=f"Phase {i}", issues=[], warnings=[], metrics={}) for i in range(1, 6)]
    score = compute_health_score(phases)
    assert score == 100.0


def test_compute_health_score_deductions() -> None:
    """Verify health score deductions."""
    phases = [PhaseResult(phase_id=5, title="Links", issues=["Broken 1", "Broken 2"], warnings=[], metrics={})]
    score = compute_health_score(phases)
    # 100 - (2 * 3.0) = 94.0
    assert score == 94.0


def test_audit_edge_cases(mock_vault: Path) -> None:
    """Verify audit detecting long path, invalid types, and unregistered tags."""
    cfg = load_vault_config(root_path=mock_vault)
    cfg.max_path_length = 20  # Force long path issue

    # Note with invalid tipo and unregistered tag
    bad_note = mock_vault / "10-19_Progetti" / "Bad_Metadata_Note.md"
    bad_note.write_text(
        "---\ntipo: InvalidType\ntags:\n  - tag/non_censito\n---\n# Bad Note\n",
        encoding="utf-8",
    )

    report = run_audit(cfg)
    assert any("Path length" in iss for iss in report.phases[0].issues)
    assert any("Invalid tipo" in iss for iss in report.phases[2].issues)
    assert any("Unregistered tag" in iss for iss in report.phases[3].issues)


def test_audit_target_scope(mock_vault: Path) -> None:
    """Verify audit --target restricts analysis scope while keeping global catalog resolution."""
    cfg = load_vault_config(root_path=mock_vault)

    # 1. Target single clean note
    clean_note = mock_vault / "10-19_Progetti" / "Progetto_Alpha.md"
    rep_single = run_audit(cfg, target=clean_note)
    assert rep_single.total_issues == 0
    assert rep_single.health_score == 100.0

    # 2. Target note with broken link
    broken_note = mock_vault / "20-29_Aree" / "Nota_Beta.md"
    rep_broken = run_audit(cfg, target=broken_note)
    assert rep_broken.total_issues == 1
    assert any("Nota_Inesistente" in iss for iss in rep_broken.phases[4].issues)

    # 3. Target folder
    proj_folder = mock_vault / "10-19_Progetti"
    rep_folder = run_audit(cfg, target=proj_folder)
    assert rep_folder.total_issues == 0


def test_audit_multiline_stem_collision(mock_vault: Path) -> None:
    """Verify stem collision in Phase 5 prints multiline indentation with paths."""
    cfg = load_vault_config(root_path=mock_vault)

    # Create stem collision
    dup = mock_vault / "20-29_Aree" / "Progetto_Alpha.md"
    dup.write_text("# Duplicate Progetto Alpha", encoding="utf-8")

    rep = run_audit(cfg, phases_to_run=[5])
    phase5 = rep.phases[0]
    collision_warns = [w for w in phase5.warnings if "Stem collision" in w]
    assert len(collision_warns) == 1
    assert "e' ambiguo e risolve a molteplici file:" in collision_warns[0]
    assert "* 10-19_Progetti/Progetto_Alpha.md" in collision_warns[0]
    assert "* 20-29_Aree/Progetto_Alpha.md" in collision_warns[0]


def test_audit_relative_target_from_external_cwd(mock_vault: Path, monkeypatch, tmp_path: Path) -> None:
    """Verify relative target paths are resolved against vault root when CWD is outside vault."""
    monkeypatch.chdir(tmp_path)
    cfg = load_vault_config(root_path=mock_vault)

    # 1. Target relative note path from outside CWD
    rep_note = run_audit(cfg, target="10-19_Progetti/Progetto_Alpha.md")
    assert rep_note.total_issues == 0
    assert rep_note.health_score == 100.0

    # 2. Target relative folder path from outside CWD
    rep_folder = run_audit(cfg, target="10-19_Progetti")
    assert rep_folder.total_issues == 0
    assert rep_folder.health_score == 100.0
