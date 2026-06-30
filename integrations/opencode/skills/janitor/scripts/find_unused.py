#!/usr/bin/env python3
"""Heuristic dead-code finder.

Usage:
    find_unused.py [PATH...] [--json]

Lists definitions (functions, classes, modules, constants) whose name appears
nowhere else in the scanned tree, making them removal candidates for the "dead
code" operation.

# ponytail: heuristic static scan. It builds an identifier histogram over raw
# text, so string and comment mentions count as references (conservative), but
# it still misses reflection, DI containers, eval, and generated/macro call
# sites. Every candidate MUST be confirmed with a whole-repo grep before
# deletion. See references/cleanup-safety.md.
"""
import argparse
import collections
import json
import os
import re
import sys

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".env",
    "dist", "build", ".tox", ".eggs", "vendor", "target", ".next", ".cache",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage", ".gradle",
    ".idea", ".vscode", "tests", "test", "__tests__",
}

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Names called by the language, runtime, or a framework rather than by code.
RUNTIME_NAMES = {
    "__init__", "__new__", "__del__", "__main__", "__name__", "__enter__",
    "__exit__", "__str__", "__repr__", "__call__", "__iter__", "__next__",
    "__len__", "__getitem__", "__setitem__", "__delitem__", "__contains__",
    "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__", "__hash__",
    "__bool__", "__class__", "__dict__", "__getattr__", "__setattr__",
    "main", "setUp", "tearDown", "setup", "teardown",
}

# Definition syntaxes across common languages. The "name" group is the symbol.
DEF_REGEXES = [
    re.compile(r"^\s*(?:async\s+)?def\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),          # Python
    re.compile(r"^\s*class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),                      # Python/Ruby/JS/TS
    re.compile(r"^\s*module\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),                     # Ruby
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+\*?\s*(?P<name>[A-Za-z_$][\w$]*)"),  # JS/TS/PHP
    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*="),  # JS/TS
    re.compile(r"^\s*(?:public\s+)?(?:private\s+)?func\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),  # Go/Swift
    re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),  # Rust
    re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait|mod)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"),  # Rust
]


def is_probably_text(path):
    try:
        with open(path, "rb") as f:
            chunk = f.read(2048)
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def iter_files(roots):
    for root in roots:
        if os.path.isfile(root):
            if is_probably_text(root):
                yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            )
            for name in sorted(filenames):
                p = os.path.join(dirpath, name)
                if is_probably_text(p):
                    yield p


def read_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or dirs to scan (default: .)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    files = list(iter_files(args.paths))

    # One identifier histogram over raw text. String/comment mentions count.
    histogram = collections.Counter()
    contents = {}
    warnings = 0
    for p in files:
        text = read_lines(p)
        if text is None:
            warnings += 1
            continue
        contents[p] = text
        histogram.update(IDENT.findall(text))

    findings = []
    for p in files:
        text = contents.get(p)
        if text is None:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for rx in DEF_REGEXES:
                m = rx.match(line)
                if not m:
                    continue
                name = m.group("name")
                if name in RUNTIME_NAMES:
                    continue
                # Only the definition itself appears: no other reference.
                if histogram[name] <= 1:
                    findings.append({"name": name, "file": p, "line": i})
                break

    findings.sort(key=lambda x: (x["file"], x["line"]))

    if args.json:
        json.dump({"count": len(findings), "unused": findings}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("# unused definition candidates: {}".format(len(findings)))
        for f in findings:
            print("{}:{}: unused {}".format(f["file"], f["line"], f["name"]))
        if findings:
            print("# confirm each with a whole-repo grep before deleting.")

    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
