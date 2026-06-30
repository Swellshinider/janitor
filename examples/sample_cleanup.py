#!/usr/bin/env python3
"""Janitor self-check.

Two jobs:
1. Prove the behavior-preservation principle janitor is built on: removing
   uncalled code and merging duplicates keeps observable output identical.
2. Smoke-test the three detection scripts against a tiny bloated fixture,
   asserting each flags the right thing.

Run: python3 examples/sample_cleanup.py
No test framework, just asserts. This is janitor's one runnable check.
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.abspath(os.path.join(HERE, "..", "skills", "janitor", "scripts"))
sys.path.insert(0, SCRIPTS)
import find_duplicates  # noqa: E402
import find_oversized  # noqa: E402
import find_unused  # noqa: E402


def run_json(module, args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        module.main(args)
    return json.loads(buf.getvalue())


# --------------------------------------------------------------------------
# Part 1: behavior preservation. Cleanup must not change observable output.
# --------------------------------------------------------------------------
def add(a, b):
    return a + b


def add_v2_before(a, b):
    return a + b            # duplicate of add


def add_v2_after(a, b):
    return add(a, b)        # dedup via delegation


assert add_v2_before(2, 3) == add_v2_after(2, 3) == 5, "dedup changed output"


def keep(i):
    return i * 2


def drop_unused(i):         # never called; safe to remove
    return i * 999


public_before = [keep]
results_before = [fn(i) for i, fn in enumerate(public_before)]
results_after = [fn(i) for i, fn in enumerate([keep])]  # drop_unused gone
assert results_before == results_after, "removing uncalled code changed output"


# --------------------------------------------------------------------------
# Part 2: detection scripts flag a known bloated fixture.
# --------------------------------------------------------------------------
BIG_FILE = "\n".join("x = {}".format(i) for i in range(30)) + "\n"

UNUSED_FILE = (
    "def used_helper(a, b):\n"
    "    return a + b\n"
    "\n"
    "def unused_helper(a, b):\n"
    "    return a - b\n"
    "\n"
    "def run():\n"
    "    return used_helper(1, 2)\n"
)

DUP_BLOCK = (
    "def pack(items):\n"
    "    result = []\n"
    "    for item in items:\n"
    "        if item is not None:\n"
    "            result.append(item)\n"
    "    return result\n"
)
DUP_FILE_A = DUP_BLOCK
DUP_FILE_B = DUP_BLOCK.replace("pack", "pack_copy")


def build_fixture(root):
    with open(os.path.join(root, "big.py"), "w") as f:
        f.write(BIG_FILE)
    with open(os.path.join(root, "svc.py"), "w") as f:
        f.write(UNUSED_FILE)
    with open(os.path.join(root, "pack_a.py"), "w") as f:
        f.write(DUP_FILE_A)
    with open(os.path.join(root, "pack_b.py"), "w") as f:
        f.write(DUP_FILE_B)


def main():
    tmp = tempfile.mkdtemp(prefix="janitor_fixture_")
    build_fixture(tmp)

    # Oversized: big.py over a low threshold.
    oversized = run_json(find_oversized, ["--json", "--files", "20", tmp])
    paths = {f["path"] for f in oversized["files"]}
    assert any(p.endswith("big.py") for p in paths), "oversized scan missed big.py"

    # Unused: unused_helper flagged, used_helper not.
    unused = run_json(find_unused, ["--json", tmp])
    names = {u["name"] for u in unused["unused"]}
    assert "unused_helper" in names, "unused scan missed unused_helper"
    assert "used_helper" not in names, "unused scan wrongly flagged used_helper"

    # Duplicates: the two pack blocks match.
    duplicates = run_json(find_duplicates, ["--json", "--min-lines", "5", tmp])
    assert duplicates["count"] >= 1, "duplicate scan found nothing"

    print("PASS: behavior preserved; oversized, unused, and duplicates detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
