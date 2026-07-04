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
import sys

from common import iter_files


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
