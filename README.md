# Janitor

Janitor is the cleaner and the manager for your codebase. AI wrote too much
trash? Files and classes insanely big? Dead code everywhere? Folders a mess?
Janitor handles it, optimizing and refactoring **without changing behavior**.

It ships two skills:

- **cleaner** - the boring cleanup that piles up after fast development: remove
  unused code, split files that became impossible to read, and deduplicate
  repeated logic so the next change is smaller.
- **manager** - the structural work the cleaner refuses: split oversized files
  into cohesive modules and regroup directories into a layout grouped by
  feature or responsibility.

Both are intentionally conservative. They run checks before and after every
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

Manual fallback (both skills):

```bash
cp -R integrations/codex/skills/cleaner ~/.agents/skills/cleaner
cp -R integrations/codex/skills/manager ~/.agents/skills/manager
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
cp -R integrations/opencode/skills/cleaner integrations/opencode/skills/manager .opencode/skills/
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/skills
cp -R integrations/openclaw/skills/cleaner integrations/openclaw/skills/manager ~/.openclaw/skills/
```

### Cursor

```bash
mkdir -p .cursor/rules
cp integrations/cursor/rules/cleaner.mdc integrations/cursor/rules/manager.mdc .cursor/rules/
```

Pre-built bundles for every supported tool live in
[`integrations/`](integrations).

## For maintainers

Each `skills/<name>/SKILL.md` (`cleaner` and `manager`) is a source of truth for
the generated integrations.

```bash
python3 scripts/convert.py
python3 scripts/convert.py --tool cursor --json
```

Run the quick checks:

```bash
python3 examples/sample_cleanup.py
python3 tests/check_integrations.py
```
