#!/usr/bin/env python3
"""Find duplicate and near-duplicate code blocks.

Usage:
    find_duplicates.py [PATH...] [--min-lines N] [--json]

Hashes normalized line windows and reports blocks that repeat, so they are
merge candidates for the "deduplicate" operation.

# ponytail: line-hash heuristic, not semantic. Normalizes whitespace and drops
# blank and comment lines, so formatting-only differences count as duplicates
# and semantic clones with renamed variables do not. Confirm before merging.
"""
import argparse
import hashlib
import json
import os
import sys

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env", ".env",
    "dist", "build", ".tox", ".eggs", "vendor", "target", ".next", ".cache",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", "coverage", ".gradle",
    ".idea", ".vscode",
}

COMMENT_PREFIXES = ("//", "#", "*", "--", ";", "%")  # best-effort, cross-language


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


def keep_line(line):
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith(COMMENT_PREFIXES):
        return None
    # Collapse internal whitespace so indentation/spacing diffs do not split runs.
    return " ".join(stripped.split())


def normalized_lines(path):
    """Return [(orig_line_no, norm_text)] for lines worth comparing."""
    out = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, start=1):
                norm = keep_line(line)
                if norm is not None:
                    out.append((lineno, norm))
    except OSError:
        return None
    return out


def find_segments(files, window):
    """Return duplicate segments as dicts with base/other ranges and length."""
    by_hash = {}
    file_lines = {}
    warnings = 0

    for p in files:
        lines = normalized_lines(p)
        if lines is None:
            warnings += 1
            continue
        file_lines[p] = lines
        for i in range(len(lines) - window + 1):
            block = "\n".join(norm for _, norm in lines[i:i + window])
            h = hashlib.sha1(block.encode("utf-8")).hexdigest()
            by_hash.setdefault(h, []).append((p, i))

    segments = []
    for occurrences in by_hash.values():
        if len(occurrences) < 2:
            continue
        base_file, base_idx = occurrences[0]
        base_lines = file_lines[base_file]
        for other_file, other_idx in occurrences[1:]:
            if (base_file, base_idx) == (other_file, other_idx):
                continue
            other_lines = file_lines[other_file]
            # Extend the matching run forward from the shared window start.
            k = 0
            while (
                base_idx + k < len(base_lines)
                and other_idx + k < len(other_lines)
                and base_lines[base_idx + k][1] == other_lines[other_idx + k][1]
            ):
                k += 1
            if k < window:
                continue
            segments.append({
                "base_file": base_file,
                "base_start": base_lines[base_idx][0],
                "base_end": base_lines[base_idx + k - 1][0],
                "other_file": other_file,
                "other_start": other_lines[other_idx][0],
                "other_end": other_lines[other_idx + k - 1][0],
                "length": k,
            })

    segments = drop_contained(segments)
    segments.sort(key=lambda s: -s["length"])
    return segments, warnings


def drop_contained(segments):
    """Drop a segment fully covered by a longer segment with the same pair."""
    kept = []
    # Group by unordered file pair so mirrors and repeats collapse together.
    segments.sort(key=lambda s: (s["length"]), reverse=True)
    for s in segments:
        contained = False
        for k in kept:
            same_pair = {k["base_file"], k["other_file"]} == {s["base_file"], s["other_file"]}
            if not same_pair:
                continue
            if _covers(k, s):
                contained = True
                break
        if not contained:
            kept.append(s)
    return kept


def _covers(big, small):
    """True if segment big spans small in both files (either orientation)."""
    pairs = [
        (big["base_file"], big["base_start"], big["base_end"]),
        (big["other_file"], big["other_start"], big["other_end"]),
    ]
    small_pts = [
        (small["base_file"], small["base_start"], small["base_end"]),
        (small["other_file"], small["other_start"], small["other_end"]),
    ]
    for bf, bs, be in pairs:
        for sf, ss, se in small_pts:
            if bf == sf and ss >= bs and se <= be:
                # Found one end covered; check the other end against the other big point.
                other_big = next(p for p in pairs if p != (bf, bs, be))
                other_small = next(p for p in small_pts if p != (sf, ss, se))
                if other_big[0] == other_small[0] and other_small[1] >= other_big[1] and other_small[2] <= other_big[2]:
                    return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", default=["."], help="files or dirs to scan (default: .)")
    ap.add_argument("--min-lines", type=int, default=6, help="minimum duplicate block length (default: 6)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args(argv)

    if args.min_lines < 2:
        ap.error("--min-lines must be >= 2")

    files = list(iter_files(args.paths))
    segments, warnings = find_segments(files, args.min_lines)

    if args.json:
        json.dump({"count": len(segments), "duplicates": segments}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("# duplicate blocks (>= {} lines): {}".format(args.min_lines, len(segments)))
        for s in segments:
            print("{len} lines: {bf}:{bs}-{be}  ==  {of}:{os}-{oe}".format(
                len=s["length"], bf=s["base_file"], bs=s["base_start"], be=s["base_end"],
                of=s["other_file"], os=s["other_start"], oe=s["other_end"]))

    return 1 if warnings else 0


if __name__ == "__main__":
    sys.exit(main())
