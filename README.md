# Janitor

Janitor is the cleaner for your codebase. AI wrote too much trash? Files and
classes insanely big? Dead code everywhere? Janitor cleans it up, optimizing
and refactoring **without changing behavior**.

Janitor is an AI skill. It guides an agent through three behavior-preserving
operations:

- **Dead code removal**: unused functions, imports, variables, types, files.
- **Split oversized files or classes**: extract cohesive units, keep the public
  surface stable with re-exports.
- **Deduplication**: merge repeated logic into one shared helper.

The hard rule is **no behavior changes**. Tests run before and after every
change, the public API stays frozen, and code that may be reached dynamically
(reflection, DI, string dispatch) is kept and flagged, never deleted on a guess.

Over-engineering review is intentionally out of scope; that belongs to a
dedicated review pass, not janitor. Janitor applies cleanup, it does not hunt
complexity.

## How it works

Assess with the detection scripts, propose a safety-ranked plan, execute one
change at a time with verification. See
[`skills/janitor/SKILL.md`](skills/janitor/SKILL.md) for the full skill.

Detection scripts (stdlib Python, `--json` on each):

- `skills/janitor/scripts/find_oversized.py`
- `skills/janitor/scripts/find_unused.py`
- `skills/janitor/scripts/find_duplicates.py`

## Install

### Claude Code

Install as a plugin:

```
/plugin marketplace add Swellshinider/janitor
/plugin install janitor@janitor
```

### Codex, Cursor, Copilot

Pre-built bundles live in [`integrations/`](integrations). Copy the matching
files for your tool.

### Codex

```bash
cp -R integrations/codex/skills/janitor ~/.agents/skills/janitor
```

### Cursor

```bash
mkdir -p .cursor/rules
cp integrations/cursor/rules/janitor.mdc .cursor/rules/
```

### GitHub Copilot

```bash
cp integrations/copilot/copilot-instructions.md .github/copilot-instructions.md
```

## Regenerate integrations

The `integrations/` directory is generated from the single source
`skills/janitor/SKILL.md`.

```bash
python3 scripts/convert.py            # all tools
python3 scripts/convert.py --tool cursor --json
```

## Verify

```bash
python3 examples/sample_cleanup.py    # self-check: behavior + detection
```
