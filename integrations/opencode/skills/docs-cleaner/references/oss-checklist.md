# Open-source documentation checklist

Use this checklist to assess repository readiness. Mark each item as present,
stale, incomplete, redundant, or intentionally out of scope. Verify claims
against the repository before proposing edits.

## Core project documentation

- `README.md` explains what the project does, who it is for, how to install it,
  the shortest useful usage example, supported environments, and where to get
  help.
- A `LICENSE` or equivalent legal notice exists and matches the repository
  metadata.
- A changelog or release-history document records meaningful user-facing
  changes without rewriting historical entries.
- Examples and commands in the README still exist and can be run or verified.
- Links resolve locally, headings are discoverable, and each topic has one
  canonical explanation.

## Community health files

Add these only when the project owner selects them or the repository already
promises them:

- `CONTRIBUTING.md`: prerequisites, development checks, contribution flow, and
  expectations for generated files or tests.
- `CODE_OF_CONDUCT.md`: behavior expectations and a private reporting route.
- `SECURITY.md`: supported versions and a private vulnerability-reporting
  route; never direct vulnerability reports to public issues.
- `SUPPORT.md`: the correct route for usage questions, bugs, and security
  reports.
- `.github/ISSUE_TEMPLATE/`: actionable bug and feature templates, with a
  configuration file only when it improves routing.
- `.github/pull_request_template.md`: concise context, validation, and review
  checklist.

Do not invent an email address, chat channel, support promise, security SLA,
supported version, label, or maintainer. Use a real repository contact or
state the limitation plainly.

## Safe consolidation and removal

- Preserve `LICENSE`, security policy, conduct policy, and changelog history
  unless the owner explicitly directs otherwise.
- Before deleting a file, search the whole repository for its path, title,
  headings, and distinctive commands.
- Merge duplicated material into the most discoverable canonical location, then
  replace old references with links before removing the duplicate.
- Keep files required by a hosting platform, package manager, or integration,
  even when their content resembles another document.
- Treat generated files as outputs: change their source and regenerate them.
- Never remove a document solely because it has no static inbound link.
