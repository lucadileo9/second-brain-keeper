# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-11-21

### Added
- **Dual-Head Architecture**: Introduced programmatic Python SDK Facade (`from sbk import Vault`) alongside the modernized CLI (`sbk`), operating without terminal side effects and returning immutable domain models.
- **Transaction Journal & Redo Engine**: Full ACID-inspired journaling with SHA-256 integrity verification, supporting atomic LIFO rollbacks (`sbk undo`) and reapplications (`sbk redo`).
- **Batch Processing**: Added `--batch <file.json>` support for bulk `move`, `rename`, and `frontmatter` modifications with strict All-or-Nothing preflight validation.
- **Interactive Sandbox Environment**: Added `sbk sandbox {init,reset,path}` for isolated, risk-free experimentation and test automation.
- **Git-Style Upward Root Discovery**: `sbk` commands automatically discover the nearest `vault.toml` up the directory hierarchy, enabling seamless execution from subdirectories.
- **Unified Multi-Target Formatting**: Support for multi-output serialization (`-o out.json -o out.yaml`) and `--format json|yaml|csv` via centralized `ReportWriter`.
- **Engineering Tooling**: Configured multi-platform CI matrix supporting Python 3.10 through 3.14, dynamic virtual environment detection in `Makefile`, `pre-commit` hooks, and structured GitHub Issue Forms.

### Changed
- **Staging-First Note Creation**: Replaced rigid type-based folder routing with a clean staging model defaulting to `00_Inbox/` (customizable via `inbox_folder` in `vault.toml`), while retaining explicit `--folder` targeting.
- **Modular CLI Architecture**: Decoupled monolithic command parsers into category registrars (`lifecycle`, `governance`, `diagnostic`, `maintenance`).
- **Contextual Index Naming**: Added support for contextual folder MOC names (`00_Indice_<Folder>.md`).
- **Refactoring & DRY Consolidations**: Centralized vault initialization, path resolution (`resolve_vault_path`), and wikilink synchronization.

### Removed
- **Breaking Changes**:
  - Removed deprecated `check-links` command in favor of `sbk audit --step 5`.
  - Removed deprecated `disambiguate` command in favor of `sbk search` and collision detection in `audit`.

## [1.1.1] - 2026-11-15

### Fixed
- Fixed vault file traversal to explicitly exclude `vault.toml` and hidden configuration artifacts.
- Resolved Windows test matrix compatibility and Bandit AST security scanner issues.

## [1.1.0] - 2026-11-10

### Added
- Initial implementation of the Transaction Journal for atomic note lifecycle mutations.
- Consolidated immutable domain models for audit reporting, orphan attachments, and broken link diagnostics.

## [1.0.0] - 2026-11-07

### Added
- Initial public release of Second Brain Keeper.
- 5-phase vault audit engine with Vault Health Score calculation.
- Automated attachment soft-delete and media offloading.
- Markdown naming normalization and contextual folder index generation.
- Johnny.Decimal hierarchy validation and wikilink integrity checks.
