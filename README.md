# Janitor

Janitor is the cleaner for your codebase. AI wrote too much trash? Files and
classes insanely big? Dead code everywhere? Janitor cleans it up, optimizing
and refactoring **without changing behavior**.

It is built for the boring cleanup work that piles up after fast development:
removing unused code, splitting files that became impossible to read, and
deduplicating repeated logic so the next change is smaller.

Janitor is intentionally conservative. It runs checks before and after cleanup,
keeps public behavior stable, and flags risky code instead of guessing.

## What Janitor cleans

- Dead imports, variables, functions, types, and files.
- Oversized files and classes that need to be split into smaller pieces.
- Repeated logic that should live in one place.

It does not do broad architecture rewrites or taste-based reviews. Janitor is
for cleanup that can be checked.

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

Manual fallback:

```bash
cp -R integrations/codex/skills/janitor ~/.agents/skills/janitor
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

Copy the generated command and skill bundle into your project config:

```bash
mkdir -p .opencode/command .opencode/skills
cp integrations/opencode/command/janitor.md .opencode/command/
cp -R integrations/opencode/skills/janitor .opencode/skills/
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/skills
cp -R integrations/openclaw/skills/janitor ~/.openclaw/skills/
```

### Cursor

```bash
mkdir -p .cursor/rules
cp integrations/cursor/rules/janitor.mdc .cursor/rules/
```

Pre-built bundles for every supported tool live in
[`integrations/`](integrations).

## For maintainers

`skills/janitor/SKILL.md` is the source of truth for generated integrations.

```bash
python3 scripts/convert.py
python3 scripts/convert.py --tool cursor --json
```

Run the quick checks:

```bash
python3 examples/sample_cleanup.py
python3 tests/check_integrations.py
```
