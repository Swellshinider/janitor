# Janitor

Janitor is a behavior-preserving cleanup skill for AI agents. It helps remove
dead code, split oversized files or classes, and deduplicate repeated logic
without changing behavior.

The contract is narrow on purpose: tests run before and after each change, the
public API stays stable, and anything that may be reached dynamically is kept
and flagged instead of deleted on a guess.

Over-engineering review is out of scope. Janitor applies cleanup; it does not
hunt complexity.

## What it does

- **Dead code removal**: unused functions, imports, variables, types, and files.
- **Split oversized files or classes**: extract cohesive units while preserving
  old import paths with re-exports.
- **Deduplication**: merge repeated logic into one shared helper.

See [`skills/janitor/SKILL.md`](skills/janitor/SKILL.md) for the full skill.
The bundled detection scripts are stdlib Python and support `--json`:

- `skills/janitor/scripts/find_oversized.py`
- `skills/janitor/scripts/find_unused.py`
- `skills/janitor/scripts/find_duplicates.py`

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

## Regenerate integrations

`skills/janitor/SKILL.md` is the source of truth.

```bash
python3 scripts/convert.py
python3 scripts/convert.py --tool cursor --json
```

## Verify

```bash
python3 examples/sample_cleanup.py
python3 tests/check_integrations.py
```
