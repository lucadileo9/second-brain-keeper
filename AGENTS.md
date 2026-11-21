# AGENTS.md — Development Directives for AI Agents

This document defines the architecture, engineering standards, safety boundaries, and operational workflows for autonomous AI agents collaborating on the `second-brain-keeper` repository.

---

## 1. Project Overview & Core Mission

**`second-brain-keeper`** (distributed as CLI executable `sbk` and Python package `sbk`) is an enterprise-grade governance engine, link validator, and transactional maintenance toolkit for complex Markdown document vaults (specifically optimized for Obsidian vaults organized under the Johnny.Decimal classification system).

### Core Architecture (Dual-Head Paradigm)
1. **Programmatic Python SDK Facade (`from sbk import Vault`)**:
   - Zero terminal side-effects (no `print`, no `sys.exit`).
   - Clean dependency injection via `VaultConfig`.
   - Returns immutable dataclass models (`CreateResult`, `AuditReport`, `UndoResult`, `BatchResult`).
   - Raises strongly typed exceptions inheriting from `sbk.exceptions.VaultKeeperError`.
2. **Command Line Interface (`sbk`)**:
   - CLI parsers decoupled into domain categories (`lifecycle`, `governance`, `diagnostic`, `maintenance`).
   - Command handlers translate domain model results into structured stdout (Markdown tables, JSON, YAML, CSV).
   - Standard POSIX semantic exit codes (`EXIT_SUCCESS = 0`, `EXIT_ERROR = 1`).

---

## 2. Directory Layout

```
second-brain-keeper/
├── pyproject.toml              # Build metadata, dependencies, tool configurations
├── Makefile                    # Unified build, test, and linting targets
├── .pre-commit-config.yaml     # Static analysis hooks (ruff, mypy, yaml, json)
├── CHANGELOG.md                # Keep a Changelog standard release history
├── src/sbk/
│   ├── __init__.py             # Public SDK exports (Vault, models, exceptions)
│   ├── vault.py                # High-level Vault Facade orchestrator
│   ├── config.py               # TOML configuration loader and upward root discovery
│   ├── exceptions.py           # Typed domain exception hierarchy
│   ├── cli/
│   │   ├── main.py             # CLI entrypoint and global argument parser
│   │   ├── parsers/            # Modular argument parsers by category
│   │   └── commands/           # Command execution handlers
│   ├── core/                   # Core business logic engines
│   │   ├── audit.py            # 5-phase vault diagnostic engine
│   │   ├── journal.py          # Transaction journal, hashing, undo/redo
│   │   ├── templates.py        # 3-tier deterministic template engine
│   │   ├── document.py         # MarkdownDocument OO domain wrapper
│   │   ├── lifecycle.py        # Move, rename, delete, batch operations
│   │   ├── indices.py          # Contextual folder MOC generation
│   │   ├── taxonomy.py         # Tag taxonomy validation engine
│   │   ├── links.py            # Wikilink resolution and refactoring
│   │   └── attachments.py      # Orphan detection and heavy media offload
│   ├── models/                 # Pure dataclasses (config, entities, journal, results)
│   └── utils/                  # Formatters, helpers, string normalization
├── tests/                      # Pytest suite (unit, integration, and CLI tests)
└── docs/                       # Architecture, CLI, and testing manuals
```

---

## 3. Tooling, Environment & Verification Workflow

The project uses a standard `Makefile` with dynamic virtual environment detection (auto-detecting `.venv` if present).

### Primary Make Targets
- `make test`: Run complete pytest suite with line-by-line coverage report (`pytest --cov=sbk --cov-report=term-missing tests/`).
- `make lint`: Run Ruff linter checks (`ruff check src tests`).
- `make format`: Run Ruff code formatter (`ruff format src tests`).
- `make typecheck`: Run Mypy static type checker (`mypy src`).
- `make pre-commit`: Run all pre-commit hooks across all files.

### Why Verification Matters Before Committing
Git pre-commit hooks execute automatically during `git commit` to verify formatting and types. However, AI agents **MUST run `make test` before staging or committing changes**, because:
1. `pytest` is intentionally decoupled from commit hooks to keep micro-commits fast; committing without testing risks breaking integration.
2. Catching syntax, formatting, or type errors early prevents aborted commits that leave unstaged modifications in the working tree.

**Golden Rule for Agents**: Always execute `make pre-commit && make test` before creating a git commit. All 190+ tests must pass with 0 warnings.

---

## 4. Inviolable Safety & Engineering Directives

1. **Absolute Ban on Emojis (Zero Emojis Rule)**:
   - Never use emojis anywhere: code, docstrings, log messages, CLI output strings, markdown documentation, or git commit messages. Keep all output sober, clean, and professional.
2. **Strict Typing & Type Safety**:
   - Every function, method, and dataclass attribute must have complete, explicit type annotations.
   - Do not use `Any` when a concrete type, union, or generic can be expressed.
   - Code must pass `mypy src` with zero errors.
3. **Transactional Integrity & ACID Journaling**:
   - Any mutating operation (`create`, `move`, `rename`, `delete`, `batch`) must register a transaction in `JournalManager` (`.sbk/journal.json`) with before/after state and SHA-256 integrity verification.
   - Mutating commands must support atomic rollback via `sbk undo` / `v.undo()`.
4. **Preflight Validations & Dry-Run Support**:
   - Mutating CLI commands must support `--dry-run` to simulate actions without disk side-effects.
   - Batch operations must implement an **All-or-Nothing preflight check**: if any single item fails validation, no changes are committed to disk.
5. **Deterministic Template Engine**:
   - Note creation follows a strict 3-tier deterministic resolution:
     1. Tier 1: Explicit CLI `--template <name_or_path>`.
     2. Tier 2: Configured default template (`[templates].default_template`).
     3. Tier 3: Universal minimal 4-line code scaffold (`---\ntipo: <Tipo>\ntags: []\n---\n\n# {{title}}\n`).
   - Never reintroduce implicit type matching (`Template_{tipo}`) or language-specific hardcoded text blocks into the default scaffold.

---

## 5. Git & Release Conventions

1. **Branching Model**:
   - `main`: Production-ready release branch. Strictly mirrors published SemVer tags.
   - `develop`: Integration branch for tested features and bugfixes.
   - Feature/Fix branches: Create dedicated branches off `develop` (e.g. `feat/<feature-name>`, `fix/<issue-name>`).
2. **Conventional Commits**:
   - Format: `<type>(<scope>): <short imperative description>`
   - Allowed types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`.
   - If closing an issue, include `Closes #<id>` in the commit body.
   - Commits must be **atomic**: one logical change per commit.
3. **Release Protocol**:
   - Increment version in `pyproject.toml` and `src/sbk/__init__.py`.
   - Update `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) guidelines.
   - Commit release bump on `develop`: `chore(release): bump version to X.Y.Z`.
   - Merge `develop` into `main` (fast-forward).
   - Create annotated tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z: ..."`.
   - Push branches and tags: `git push origin main develop --tags`.
