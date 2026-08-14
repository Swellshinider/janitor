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

# Docs Cleaner

Audit project documentation, keep one useful source for each topic, and make
the repository easier for users and contributors to understand. Do not change
application behavior or invent project facts.

## Contract

1. Inspect the repository and run its available checks before editing.
2. Establish documentation facts from source code, manifests, scripts, CI, and
   existing docs. Treat unverified claims as findings, not facts.
3. Produce a findings list with evidence, severity, and one action: update,
   merge, remove, add, or ask.
4. Ask before creating optional community files. For an explicit project
   request, apply the selected baseline directly.
5. Remove a document only when it is obsolete, duplicated, or replaced; update
   every reference and preserve the useful information first.
6. Keep legal notices, security instructions, historical changelog entries,
   and platform-required files unless the owner explicitly approves removal.
7. Apply one logical documentation change at a time, then rerun the relevant
   checks. Stop on the first unexplained failure.

## Workflow

### Assess

- Run `scripts/audit_docs.py --json PROJECT_ROOT` to inventory documentation,
  check standard files, inspect README headings, and find broken local links.
- Read the README, license, changelog, and contributor-facing files in full.
- Search the repository for documentation paths, commands, install instructions,
  feature names, URLs, and claims that may be stale.
- Identify canonical sources and generated copies. Do not treat generated
  platform bundles as redundant files; update their source and regenerate them.

### Propose

Rank findings by user or maintainer impact:

1. Incorrect commands, broken links, and security or legal gaps.
2. Missing onboarding and contribution information.
3. Contradictory or stale descriptions and examples.
4. Duplicated, overly verbose, or low-value documentation.

For each finding, state the path, evidence, proposed change, and whether it
needs owner approval. Read `references/oss-checklist.md` for the detailed
community-file rubric.

### Apply

- Update claims from repository evidence; never guess versions, support
  channels, contacts, or deployment behavior.
- Prefer concise sections and links to one canonical document over repetition.
- Add standard community files only after the requested baseline is confirmed.
- When removing or merging docs, update inbound links, navigation, templates,
  and references before deleting the obsolete copy.
- Keep generated integration outputs synchronized through the repository's
  converter instead of hand-editing them.

### Verify

- Rerun the narrowest relevant project checks after each logical edit.
- Rerun the audit and confirm local links resolve.
- Check that commands, file paths, skill names, and install instructions match
  the repository.
- Run the full project checks before reporting completion.
- Summarize every change and any findings intentionally left for the owner.

## Boundaries

Do not refactor production code, alter package or CI behavior, rewrite legal
terms, remove security guidance, or create documentation merely to increase
file count. Route code cleanup to `cleaner` and structural code or directory
changes to `manager`.

# Manager

Behavior-preserving structural refactor. Split oversized files into cohesive
modules and move files into a cleaner directory layout. Tests stay green and the
public surface is frozen: every move rewrites imports and leaves a re-export
shim at the old path so callers keep resolving. If a move would change
behavior, do not make it.

## The Contract (non-negotiable)

1. **Tests first.** Run the project's tests before touching anything. Record
   green or red. If there is no test suite, say so and ask before proceeding.
2. **One move at a time.** Apply one structural edit, one split or one
   relocation, re-run the tests, then commit or revert. On the first failure
   you did not cause, stop and revert.
3. **Public surface frozen.** Exported names, function signatures, types, and
   module paths stay identical. Every moved module leaves a re-export shim at
   its old path so existing imports keep resolving.
4. **No dynamic guesses.** Never move or split code that may be reached by
   reflection, string dispatch, `eval`, dependency injection, or `__all__`-gated
   exports. When unsure, keep it and flag it for the human.
5. **Every move gets a diff and a one-line reason.** Group moves into a
   reviewable plan; nothing lands silently.

## How it works

Assess, propose, execute. Survey the structure, design a target layout, then
apply one move at a time with verification.

- **Assess.** Run `scripts/survey_structure.py --json`. Build a map of
  oversized files, wide directories, and nesting depth.
- **Propose.** State the target layout before touching code: which files split
  into which new modules, which files move to which directories. Rank by safety.
- **Execute.** Apply one move, rewrite imports, add the re-export shim, run the
  tests, commit or revert, repeat.

## Operations

### Split oversized files or classes

When a file or class is too large, extract cohesive units into new modules. The
old path re-exports the moved names so callers and imports do not change. Run
the tests after every move.

### Regroup directories

Move files into a layout grouped by feature or responsibility. Rewrite every
import to the new path, and leave a re-export shim at each old path so existing
imports keep resolving. Prefer few, well-named directories over deep nesting.
Run the tests after every move.

## Red flags, STOP

You are about to violate the contract if any of these is true. Stop, do not
proceed.

- A move would change an import path and you left no re-export shim at the old
  path. **Stop, add the shim.**
- You would rename an exported name or signature to make a split fit. **Stop,
  replan around a re-export.**
- The thing has no static references, but the codebase uses reflection, DI, or
  string dispatch. **Keep it, flag it.**
- Tests are red before you started and you moved on anyway. **Stop, report.**
- You are about to skip the post-move test run. **Stop, run it.**

## Verification

Done means: tests green before and after, `git diff` scoped to internal moves,
re-export shims, and import rewrites only, public names and import paths
unchanged, and a one-line behavior-identical summary per move. Run the type
checker or linter if the project has one.

## Tools

- `references/cleanup-safety.md` - dynamic-reference and public-API detection
  per language, test and rollback patterns.
- `scripts/survey_structure.py` - directory tree shape and oversized-file
  report to inform layout proposals.

## Boundaries

Out of scope. Route these elsewhere:

- New features and bug fixes. Behavior must change, the manager does not.
- In-place dead-code removal or deduplication. Use the cleaner skill.
- Performance work.
- Over-engineering review (ponytail's lane).
- Formatting and style. Use the project's linter or formatter.
