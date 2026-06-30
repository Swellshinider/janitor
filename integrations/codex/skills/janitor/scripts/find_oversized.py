#!/usr/bin/env python3
"""List source files over a line threshold.

Usage:
    find_oversized.py [PATH...] [--files N] [--json]

Reports files whose line count meets or exceeds --files (default 400), largest
first. Use it to find cleanup candidates for the "split oversized files"
operation.

# ponytail: file-level only; the AI pinpoints oversized functions and classes
# within each flagged file. Cross-language unit sizing is too fragile to guess.
"""
import argparse
import json
import os
import sys

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".env",
    "dist", "build", ".tox", ".eggs", "vendor", "target", ".next", ".cache",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage", ".gradle",
    ".idea", ".vscode",
}


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


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or dirs to scan (default: .)")
    ap.add_argument("--files", type=int, default=400, help="line threshold (default: 400)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    findings = []
    warnings = 0
    for p in iter_files(args.paths):
        n = count_lines(p)
        if n is None:
            warnings += 1
            continue
        if n >= args.files:
            findings.append({"path": p, "lines": n})
    findings.sort(key=lambda x: x["lines"], reverse=True)

    if args.json:
        json.dump(
            {"threshold": args.files, "count": len(findings), "files": findings},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        print("# files >= {} lines: {}".format(args.files, len(findings)))
        for f in findings:
            print("{:>7}  {}".format(f["lines"], f["path"]))

    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
