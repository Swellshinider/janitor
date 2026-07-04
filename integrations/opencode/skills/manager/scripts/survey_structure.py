#!/usr/bin/env python3
"""Survey directory structure for refactor planning.

Usage:
    survey_structure.py [PATH...] [--files N] [--wide N] [--depth N] [--json]

Reports the structural signals the manager skill uses to propose a layout:
oversized files (split candidates), wide directories (regroup candidates), deep
nesting, and empty directories. Use it to assess before the "split oversized
files" and "regroup directories" operations.

# ponytail: self-contained walker instead of importing common.py. Each skill
# bundle ships independently (cursor/copilot/gemini only get SKILL.md bodies),
# and the manager ships only this one script, so a shared module would not be
# reachable. SKIP_DIRS and is_probably_text mirror skills/cleaner/scripts/common.py;
# keep them in sync. If a second manager script appears, lift this walker into a
# local common.py.
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


def count_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError:
        return None


def survey(roots, files_thresh, wide_thresh, depth_thresh):
    """Return structural signals across the scanned roots plus a warning count."""
    oversized, wide, deep, empty = [], [], [], []
    max_depth = 0
    warnings = 0

    for root in roots:
        if os.path.isfile(root):
            n = count_lines(root)
            if n is None:
                warnings += 1
            elif n >= files_thresh:
                oversized.append({"path": root, "lines": n})
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            # Count entries before pruning: a dir whose only children are
            # hidden/vendored must not be reported as empty (removable).
            raw_subdirs = len(dirnames)
            raw_files = len(filenames)
            dirnames[:] = sorted(
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            )
            rel = os.path.relpath(dirpath, root)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            max_depth = max(max_depth, depth)
            # Report the shallowest over-nested dir per branch (depth == threshold);
            # deeper descendants share the same problem and only add noise.
            if depth == depth_thresh:
                deep.append({"path": dirpath, "depth": depth})

            text_count = 0
            for name in sorted(filenames):
                p = os.path.join(dirpath, name)
                if not is_probably_text(p):
                    continue
                text_count += 1
                n = count_lines(p)
                if n is None:
                    warnings += 1
                elif n >= files_thresh:
                    oversized.append({"path": p, "lines": n})

            if text_count >= wide_thresh:
                wide.append({"path": dirpath, "files": text_count})
            # Truly empty (no files, no subdirs of any kind): a removal candidate.
            if raw_files == 0 and raw_subdirs == 0:
                empty.append(dirpath)

    oversized.sort(key=lambda x: x["lines"], reverse=True)
    wide.sort(key=lambda x: x["files"], reverse=True)
    deep.sort(key=lambda x: x["depth"], reverse=True)
    report = {
        "max_depth": max_depth,
        "oversized_files": oversized,
        "wide_dirs": wide,
        "deep_dirs": deep,
        "empty_dirs": empty,
    }
    return report, warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or dirs to scan (default: .)")
    ap.add_argument("--files", type=int, default=400, help="line threshold for oversized files (default: 400)")
    ap.add_argument("--wide", type=int, default=20, help="file count for a directory to count as wide (default: 20)")
    ap.add_argument("--depth", type=int, default=5, help="depth threshold for over-nested dirs (default: 5)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    report, warnings = survey(args.paths, args.files, args.wide, args.depth)

    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("# structure survey")
        print("max depth: {}".format(report["max_depth"]))
        print("# oversized files (>= {} lines): {}".format(args.files, len(report["oversized_files"])))
        for f in report["oversized_files"]:
            print("{:>7}  {}".format(f["lines"], f["path"]))
        print("# wide directories (>= {} files): {}".format(args.wide, len(report["wide_dirs"])))
        for d in report["wide_dirs"]:
            print("{:>7}  {}".format(d["files"], d["path"]))
        print("# deep directories (>= depth {}): {}".format(args.depth, len(report["deep_dirs"])))
        for d in report["deep_dirs"]:
            print("{:>7}  {}".format(d["depth"], d["path"]))
        print("# empty directories: {}".format(len(report["empty_dirs"])))
        for d in report["empty_dirs"]:
            print(d)

    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
