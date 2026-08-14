#!/usr/bin/env python3
"""Smoke-test the documentation audit script against a small fixture."""

import json
import os
import sys
import tempfile


HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = os.path.abspath(os.path.join(HERE, "..", "skills", "docs-cleaner", "scripts"))
sys.path.insert(0, SCRIPT_DIR)
import audit_docs  # noqa: E402


def write(path, contents):
    full_path = os.path.join(path, *contents[0].split("/"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as handle:
        handle.write(contents[1])


def main():
    with tempfile.TemporaryDirectory(prefix="janitor_docs_fixture_") as root:
        write(root, ("README.md", "# Example\n\n[Guide](docs/guide.md)\n[Missing](docs/missing.md)\n"))
        write(root, ("docs/guide.md", "# Guide\n"))
        write(root, ("LICENSE", "license\n"))

        report = audit_docs.audit(root)
        assert report["standards"]["readme"]["present"]
        assert report["standards"]["license"]["present"]
        assert report["standards"]["contributing"]["present"] is False
        assert report["links"]["checked"] == 2
        assert report["links"]["broken"] == [
            {"source": "README.md", "line": 4, "target": "docs/missing.md"}
        ]

        encoded = json.dumps(report)
        assert "readme_headings" in encoded

    print("PASS: documentation inventory and broken local links detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
