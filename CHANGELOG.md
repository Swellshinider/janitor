# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Claude Code plugin manifests (`.claude-plugin/marketplace.json`,
  `.claude-plugin/plugin.json`) so janitor installs via
  `/plugin marketplace add <owner>/janitor` then `/plugin install janitor@janitor`.
- Janitor skill: behavior-preserving codebase cleanup (dead code removal,
  splitting oversized files or classes, deduplication). See
  `skills/janitor/SKILL.md`.
- Detection scripts: `find_oversized.py`, `find_unused.py`,
  `find_duplicates.py` (stdlib Python, `--json` output).
- `references/cleanup-safety.md`: dynamic-reference and public-API detection
  per language, test and rollback patterns.
- `scripts/convert.py`: single-source generator for Codex, Cursor, and Copilot
  integration bundles.
- `examples/sample_cleanup.py`: runnable self-check.
- MIT License (`LICENSE`).
