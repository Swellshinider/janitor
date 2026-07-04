---
name: cleaner
description: "Behavior-preserving cleanup: dead code removal, file splitting, and deduplication without public API changes."
homepage: https://github.com/Swellshinider/janitor
license: MIT
---
# Cleaner

Behavior-preserving cleanup. Smaller files, no dead code, no duplication, same
behavior. The test suite ends green and the public surface is unchanged. If a
change would alter behavior, do not make it.

## The Contract (non-negotiable)

1. **Tests first.** Run the project's tests before touching anything. Record
   green or red. If there is no test suite, say so and ask before proceeding.
2. **One change at a time.** Apply one logical edit, re-run the tests, then
   commit or revert. On the first failure you did not cause, stop and revert.
3. **Public surface frozen.** Exported names, function signatures, types, and
   module paths stay identical. Internal moves only.
4. **No dynamic guesses.** Never delete code that may be reached by reflection,
   string dispatch, `eval`, dependency injection, or `__all__`-gated exports.
   When unsure, keep it and flag it for the human.
5. **Every change gets a diff and a one-line reason.** Group changes into a
   reviewable set; nothing lands silently.

## How it works

Assess, propose, execute. Use the detection scripts to find candidates, rank
them by safety, then apply one at a time with verification.

- **Assess.** Run `scripts/find_oversized.py`, `find_unused.py`, and
  `find_duplicates.py`, each with `--json`. Build a findings list.
- **Propose.** Rank by blast radius: pure-internal dead code first, then
  duplication, then file or class splits last. State the order out loud.
- **Execute.** Apply one change, run the tests, commit or revert, repeat.

## Operations

### Dead code

Remove unused functions, imports, variables, types, and whole files. Confirm
zero references with a whole-repo grep, including inside strings and comments
(dynamic dispatch hides there). See `references/cleanup-safety.md` for the
per-language patterns that defeat a naive grep.

### Split oversized files or classes

When a file or class is too large, extract cohesive units into new modules.
Re-exports keep the public surface stable: the old path re-exports from the new
location so callers and imports do not change. Run the tests after every move.

### Deduplicate

When two or more blocks do the same thing, merge them into one shared helper.
The helper keeps the most general signature that preserves every existing call
site. Replace each duplicate with a call to the helper. Run the tests.

## Red flags, STOP

You are about to violate the contract if any of these is true. Stop, do not
proceed.

- The thing has no static references, but the codebase uses reflection, DI, or
  string dispatch. **Keep it, flag it.**
- Tests are red before you started and you moved on anyway. **Stop, report.**
- "It's obviously unused" without a whole-repo grep. **Stop, grep first.**
- You would touch an exported name or signature to make a split fit. **Stop,
  replan around a re-export.**
- You are about to skip the post-change test run. **Stop, run it.**

## Verification

Done means: tests green before and after, `git diff` scoped to internals only,
public names unchanged, and a one-line behavior-identical summary per change.
Run the type checker or linter if the project has one.

## Tools

- `references/cleanup-safety.md` - dynamic-reference and public-API detection
  per language, test and rollback patterns.
- `scripts/find_oversized.py` - files and units over a line threshold.
- `scripts/find_unused.py` - definitions with no static references.
- `scripts/find_duplicates.py` - repeated or near-repeated code blocks.

## Boundaries

Out of scope. Route these elsewhere:

- New features and bug fixes. Behavior must change, the cleaner does not.
- Structural reorganization across files and directories. Use the manager skill.
- Performance work.
- Over-engineering review (ponytail's lane).
- Formatting and style. Use the project's linter or formatter.
