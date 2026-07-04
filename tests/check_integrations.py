#!/usr/bin/env python3
"""Smoke-check committed integration files."""
import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_json(path):
    with open(os.path.join(ROOT, path), "r", encoding="utf-8") as f:
        return json.load(f)


def assert_same_dir(left, right):
    cmp = filecmp.dircmp(left, right)
    assert not cmp.left_only, "extra generated files: {}".format(cmp.left_only)
    assert not cmp.right_only, "missing generated files: {}".format(cmp.right_only)
    assert not cmp.diff_files, "stale generated files: {}".format(cmp.diff_files)
    for name in cmp.common_dirs:
        assert_same_dir(os.path.join(left, name), os.path.join(right, name))


def main():
    tmp = tempfile.mkdtemp(prefix="janitor-integrations-")
    try:
        subprocess.check_call(
            [sys.executable, os.path.join(ROOT, "scripts", "convert.py"), "--out", tmp]
        )
        assert_same_dir(tmp, os.path.join(ROOT, "integrations"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    codex = read_json(".codex-plugin/plugin.json")
    assert codex["name"] == "janitor"
    assert codex["skills"] == "./skills/"

    copilot = read_json(".github/plugin/plugin.json")
    assert copilot["name"] == "janitor"
    assert copilot["skills"] == "skills/"

    gemini = read_json("gemini-extension.json")
    assert gemini["contextFileName"] == "integrations/gemini/AGENTS.md"

    # cleanup-safety.md is duplicated across the skill bundles (each ships
    # independently); keep the two byte-identical so they cannot drift.
    assert filecmp.cmp(
        os.path.join(ROOT, "skills", "cleaner", "references", "cleanup-safety.md"),
        os.path.join(ROOT, "skills", "manager", "references", "cleanup-safety.md"),
        shallow=False,
    ), "cleanup-safety.md differs between skills/cleaner and skills/manager"

    print("PASS: integrations and marketplace manifests are wired.")


if __name__ == "__main__":
    main()
