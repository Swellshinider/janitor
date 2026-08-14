# Contributing

Thanks for helping improve Janitor. Contributions should keep the skills
conservative, focused, and useful to the projects that install them.

## Before you start

- Read the relevant skill in `skills/` before changing its behavior.
- Keep each change focused and avoid unrelated refactors.
- Do not include credentials, private values, or generated build artifacts.

## Development checks

This repository has no third-party runtime dependencies. Run the checks from
the repository root:

```bash
python3 examples/sample_cleanup.py
python3 examples/sample_docs_cleanup.py
python3 tests/check_integrations.py
```

When changing a source skill, regenerate the committed platform bundles:

```bash
python3 scripts/convert.py
```

Do not edit files under `integrations/` by hand; they are generated from
`skills/<name>/`.

## Pull requests

1. Explain the user-facing problem and the smallest useful solution.
2. Include tests or a clear validation note.
3. Update the README or changelog when the public skill set or behavior changes.
4. Confirm generated integrations are synchronized.

Open a pull request against the default branch with a concise title and enough
context for a reviewer to reproduce the checks.
