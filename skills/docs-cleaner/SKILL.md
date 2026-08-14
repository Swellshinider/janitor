---
name: docs-cleaner
description: >
  Audit and improve project documentation and open-source repository readiness:
  README files, guides, contribution policies, security and conduct
  files, support guidance, and GitHub issue or pull-request templates. Use when
  documentation is stale, redundant, incomplete, inconsistent, or needs a
  conservative open-source standards review. Documentation-only changes.
---

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
6. Keep legal notices, security instructions, and historical release information,
   and platform-required files unless the owner explicitly approves removal.
7. Apply one logical documentation change at a time, then rerun the relevant
   checks. Stop on the first unexplained failure.

## Workflow

### Assess

- Run `scripts/audit_docs.py --json PROJECT_ROOT` to inventory documentation,
  check standard files, inspect README headings, and find broken local links.
- Read the README, license, and contributor-facing files in full.
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
