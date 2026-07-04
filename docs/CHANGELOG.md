# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `manager` skill: a behavior-preserving structural refactor that splits
  oversized files into cohesive modules and regroups directories, with import
  rewrites and re-export shims keeping the public surface stable. Ships a
  `survey_structure.py` detector that reports oversized files, wide and deep
  directories, and empty directories.
- Two-skill marketplace support. `scripts/convert.py` now generates bundles for
  every skill under `skills/`; per-skill output for codex, cursor, openclaw, and
  opencode, and both skill bodies concatenated for the single-file copilot and
  gemini targets.

### Changed
- Renamed the `janitor` skill to `cleaner`. The package and marketplace name
  stays `janitor`, so install commands are unchanged, but the skill invocation
  name is now `cleaner` instead of `janitor`.
- `plugin.yaml` `provides_skills` updated from `[janitor]` to
  `[cleaner, manager]`.
- Marketplace, plugin, and integration manifests now describe both skills and
  carry `reorganize` and `structure` keywords.
- `README.md` reframed to document both skills, with updated manual-fallback
  install paths.
