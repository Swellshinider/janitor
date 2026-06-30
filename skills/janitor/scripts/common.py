"""Shared helpers for janitor detector scripts."""
import os

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


def iter_files(roots, skip_dirs=SKIP_DIRS):
    for root in roots:
        if os.path.isfile(root):
            if is_probably_text(root):
                yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(
                d for d in dirnames if d not in skip_dirs and not d.startswith(".")
            )
            for name in sorted(filenames):
                p = os.path.join(dirpath, name)
                if is_probably_text(p):
                    yield p
