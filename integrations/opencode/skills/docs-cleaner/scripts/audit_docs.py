#!/usr/bin/env python3
"""Inventory project documentation and report broken local Markdown links."""

import argparse
import json
import os
import re
import sys
from urllib.parse import unquote


DOCUMENT_EXTENSIONS = {".adoc", ".md", ".mdc", ".mdx", ".rst"}
SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".next",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
}
STANDARD_FILES = {
    "readme": ("README", "README.md", "README.rst"),
    "license": ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"),
    "changelog": (
        "CHANGELOG.md",
        "HISTORY.md",
        "docs/CHANGELOG.md",
        "docs/HISTORY.md",
    ),
    "contributing": ("CONTRIBUTING.md", ".github/CONTRIBUTING.md"),
    "code_of_conduct": ("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
    "security": ("SECURITY.md", ".github/SECURITY.md"),
    "support": ("SUPPORT.md", ".github/SUPPORT.md"),
}
LINK_RE = re.compile(r"(?<!!)(?:\[[^\]]*\])\(([^)\s]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$")


def relative(path, root):
    return os.path.relpath(path, root).replace(os.sep, "/")


def walk_files(root):
    files = []
    for current, directories, names in os.walk(root):
        directories[:] = sorted(
            name for name in directories if name not in SKIP_DIRECTORIES
        )
        for name in sorted(names):
            files.append(os.path.join(current, name))
    return files


def document_paths(files, root):
    return sorted(
        relative(path, root)
        for path in files
        if os.path.splitext(path)[1].lower() in DOCUMENT_EXTENSIONS
    )


def normalize_paths(files, root):
    return {relative(path, root).lower(): relative(path, root) for path in files}


def standard_report(files, root):
    paths = normalize_paths(files, root)
    report = {}
    for name, candidates in STANDARD_FILES.items():
        matches = [paths[candidate.lower()] for candidate in candidates if candidate.lower() in paths]
        report[name] = {"present": bool(matches), "paths": sorted(matches)}

    issue_paths = sorted(
        path
        for path in paths.values()
        if path.lower().startswith(".github/issue_template/")
        or path.lower().startswith(".github/issue_templates/")
    )
    issue_paths = [
        path for path in issue_paths if os.path.basename(path).lower() != "config.yml"
    ]
    report["issue_templates"] = {
        "present": bool(issue_paths),
        "paths": issue_paths,
    }

    pull_request_candidates = (
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "PULL_REQUEST_TEMPLATE.md",
    )
    pull_request_paths = [
        paths[candidate.lower()]
        for candidate in pull_request_candidates
        if candidate.lower() in paths
    ]
    report["pull_request_template"] = {
        "present": bool(pull_request_paths),
        "paths": sorted(set(pull_request_paths)),
    }
    return report


def readme_path(files, root):
    paths = normalize_paths(files, root)
    for candidate in STANDARD_FILES["readme"]:
        if candidate.lower() in paths:
            return os.path.join(root, paths[candidate.lower()].replace("/", os.sep))
    return None


def readme_headings(files, root):
    path = readme_path(files, root)
    if not path:
        return []
    headings = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            match = HEADING_RE.match(line.rstrip("\n"))
            if match:
                headings.append(match.group(1).strip())
    return headings


def local_target(source, target, root):
    target = unquote(target.strip().strip("<>"))
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "tel:", "data:")):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    source_directory = os.path.dirname(source)
    return os.path.normpath(os.path.join(source_directory, target.replace("/", os.sep)))


def broken_links(files, root):
    broken = []
    checked = 0
    for path in files:
        if os.path.splitext(path)[1].lower() not in DOCUMENT_EXTENSIONS:
            continue
        in_fence = False
        with open(path, "r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if line.lstrip().startswith(("```", "~~~")):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                for match in LINK_RE.finditer(line):
                    target = match.group(1)
                    resolved = local_target(path, target, root)
                    if resolved is None:
                        continue
                    checked += 1
                    if not os.path.exists(resolved):
                        broken.append(
                            {
                                "source": relative(path, root),
                                "line": line_number,
                                "target": target,
                            }
                        )
    return checked, broken


def audit(root):
    root = os.path.abspath(root)
    files = walk_files(root)
    checked, broken = broken_links(files, root)
    return {
        "documents": document_paths(files, root),
        "standards": standard_report(files, root),
        "readme_headings": readme_headings(files, root),
        "links": {"checked": checked, "broken": broken},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="emit JSON findings")
    parser.add_argument("root", nargs="?", default=".", help="project root")
    args = parser.parse_args(argv)
    report = audit(args.root)
    if args.json:
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("Documentation files: {}".format(len(report["documents"])))
        for name, finding in report["standards"].items():
            status = "present" if finding["present"] else "missing"
            print("{}: {}".format(name.replace("_", " "), status))
        print("Local links checked: {}".format(report["links"]["checked"]))
        print("Broken local links: {}".format(len(report["links"]["broken"])))
        for item in report["links"]["broken"]:
            print("- {}:{} -> {}".format(item["source"], item["line"], item["target"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
