<!-- markdownlint-disable-file MD033 MD041 -->
<h1 align="center">Janitor</h1>
<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" /></a>
</p>

<p align="center">
  Janitor is the cleaner, manager, and docs-cleaner for your codebase. AI wrote too much trash? Files and classes insanely big?  Dead code everywhere? Folders a mess? Documentation stale or incomplete? Janitor  handles it, improving and refactoring **without changing code behavior**.
</p>

## Three skills

- **cleaner** - the boring cleanup that piles up after fast development: remove
  unused code, split files that became impossible to read, and deduplicate
  repeated logic so the next change is smaller.
- **manager** - the structural work the cleaner refuses: split oversized files
  into cohesive modules and regroup directories into a layout grouped by
  feature or responsibility.
- **docs-cleaner** - audit and improve `README` files, guides, changelogs, and
  open-source community documentation while removing broken or redundant
  material conservatively.

All three are intentionally conservative. They run checks before and after every
change, keep public behavior stable, and flag risky code instead of guessing.

## What each skill does

### cleaner

- Dead imports, variables, functions, types, and files.
- Oversized files and classes that need to be split into smaller pieces.
- Repeated logic that should live in one place.

In-place cleanup. It does not do broad structural rewrites or taste-based
reviews; that is the manager's lane.

### manager

- Oversized files and classes split into cohesive modules.
- Files and directories regrouped into a feature/responsibility layout.

Behavior-preserving structural refactor. Every move rewrites imports and leaves
a re-export shim at the old path so callers keep resolving. Tests stay green and
the public surface is frozen.

### docs-cleaner

- Documentation inventory and broken local-link checks.
- README, changelog, contribution, security, conduct, and support guidance.
- GitHub issue and pull-request templates.
- Conservative consolidation of stale or redundant documentation.

It audits before editing, grounds claims in repository evidence, asks before
adding optional community files, and never changes application behavior.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for development checks and pull requests,
the [support guide](SUPPORT.md) for help, and [SECURITY.md](SECURITY.md) for
private vulnerability reporting. Please follow the
[code of conduct](CODE_OF_CONDUCT.md) when participating.

## Install

### Claude Code

```text
/plugin marketplace add Swellshinider/janitor
/plugin install janitor@janitor
```

### Codex

```bash
codex plugin marketplace add Swellshinider/janitor
codex plugin add janitor@janitor
```

Manual fallback (all skills):

```bash
cp -R integrations/codex/skills/cleaner ~/.agents/skills/cleaner
cp -R integrations/codex/skills/manager ~/.agents/skills/manager
cp -R integrations/codex/skills/docs-cleaner ~/.agents/skills/docs-cleaner
```

### GitHub Copilot CLI

```bash
copilot plugin marketplace add Swellshinider/janitor
copilot plugin install janitor@janitor
```

Editor fallback:

```bash
mkdir -p .github
cp integrations/copilot/copilot-instructions.md .github/copilot-instructions.md
```

### Gemini CLI

```bash
gemini extensions install https://github.com/Swellshinider/janitor
```

### OpenCode

Copy the generated commands and skill bundles into your project config:

```bash
mkdir -p .opencode/command .opencode/skills
cp integrations/opencode/command/cleaner.md integrations/opencode/command/manager.md .opencode/command/
cp integrations/opencode/command/docs-cleaner.md .opencode/command/
cp -R integrations/opencode/skills/cleaner integrations/opencode/skills/manager integrations/opencode/skills/docs-cleaner .opencode/skills/
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/skills
cp -R integrations/openclaw/skills/cleaner integrations/openclaw/skills/manager ~/.openclaw/skills/
cp -R integrations/openclaw/skills/docs-cleaner ~/.openclaw/skills/
```

### Cursor

```bash
mkdir -p .cursor/rules
cp integrations/cursor/rules/cleaner.mdc integrations/cursor/rules/manager.mdc .cursor/rules/
cp integrations/cursor/rules/docs-cleaner.mdc .cursor/rules/
```

Pre-built bundles for every supported tool live in
[`integrations/`](integrations).

## For maintainers

Each `skills/<name>/SKILL.md` (`cleaner`, `manager`, and `docs-cleaner`) is a source of truth for
the generated integrations.

```bash
python3 scripts/convert.py
python3 scripts/convert.py --tool cursor --json
```

Run the quick checks:

```bash
python3 examples/sample_cleanup.py
python3 examples/sample_docs_cleanup.py
python3 tests/check_integrations.py
```
