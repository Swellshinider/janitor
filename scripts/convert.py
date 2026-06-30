#!/usr/bin/env python3
"""Convert the janitor skill into per-tool integration bundles.

Usage:
    convert.py [--tool {codex,cursor,copilot,all}] [--out DIR] [--json]

Single source: skills/janitor/SKILL.md. Output (committed) lets each tool
install by copy only. Claude Code is not listed here: it installs janitor as a
plugin via .claude-plugin/, which bundles skills/ directly.

- codex: full skill bundle (SKILL.md + references + scripts), native SKILL.md
  reader. Install to ~/.agents/skills/janitor.
- cursor: a .cursor/rules/ .mdc rule generated from the source.
- copilot: a .github/copilot-instructions.md generated from the source body.

# ponytail: frontmatter is parsed with a tiny regex, not a YAML library. That is
# fine because we own the source and it only ever has name + description. Switch
# to PyYAML if arbitrary frontmatter must be supported.
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
SOURCE_DIR = os.path.join(REPO_ROOT, "skills", "janitor")
SOURCE_SKILL = os.path.join(SOURCE_DIR, "SKILL.md")
SKILL_NAME = "janitor"

TOOLS = ("codex", "cursor", "copilot")


def unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
        return value[1:-1]
    return value


def parse_skill(text):
    """Return (name, description, body) from a SKILL.md with two-field frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None, text.strip()
    i = 1
    name = desc = None
    body_start = None
    while i < len(lines):
        line = lines[i]
        if line.strip() == "---":
            body_start = i + 1
            break
        m = re.match(r"^name:\s*(.*)$", line)
        if m and name is None:
            name = unquote(m.group(1))
            i += 1
            continue
        m = re.match(r"^description:\s*(.*)$", line)
        if m and desc is None:
            rest = m.group(1).strip()
            if rest in (">", ">-", "|", "|-"):
                i += 1
                block = []
                while i < len(lines) and lines[i][:1] in " \t" and lines[i].strip():
                    block.append(lines[i].strip())
                    i += 1
                sep = " " if rest.startswith(">") else "\n"
                desc = sep.join(block).strip()
                continue
            desc = unquote(rest)
            i += 1
            continue
        i += 1
    body = "\n".join(lines[body_start:]).strip() if body_start is not None else ""
    return name, desc, body


def yaml_quote(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def copy_bundle(dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(
        SOURCE_DIR, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )


def write_cursor(out_dir, description, body):
    rules = os.path.join(out_dir, "cursor", "rules")
    os.makedirs(rules, exist_ok=True)
    content = (
        "---\n"
        "description: " + yaml_quote(description) + "\n"
        "globs:\n"
        "alwaysApply: false\n"
        "---\n"
        + body + "\n"
    )
    with open(os.path.join(rules, SKILL_NAME + ".mdc"), "w", encoding="utf-8") as f:
        f.write(content)


def write_copilot(out_dir, body):
    copilot = os.path.join(out_dir, "copilot")
    os.makedirs(copilot, exist_ok=True)
    with open(os.path.join(copilot, "copilot-instructions.md"), "w", encoding="utf-8") as f:
        f.write(body + "\n")


def convert(tool, out_dir, name, description, body):
    if tool == "codex":
        copy_bundle(os.path.join(out_dir, tool, "skills", SKILL_NAME))
    elif tool == "cursor":
        write_cursor(out_dir, description, body)
    elif tool == "copilot":
        write_copilot(out_dir, body)
    else:
        raise ValueError("unknown tool: " + tool)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", default="all", choices=TOOLS + ("all",), help="target tool (default: all)")
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "integrations"), help="output dir")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    args = ap.parse_args(argv)

    if not os.path.isfile(SOURCE_SKILL):
        sys.stderr.write("source not found: {}\n".format(SOURCE_SKILL))
        return 2
    with open(SOURCE_SKILL, "r", encoding="utf-8") as f:
        text = f.read()
    name, description, body = parse_skill(text)
    if not name or not description:
        sys.stderr.write("could not parse name/description from {}\n".format(SOURCE_SKILL))
        return 2

    targets = TOOLS if args.tool == "all" else (args.tool,)
    # A full run regenerates a clean tree so retired tools do not linger.
    if args.tool == "all" and os.path.isdir(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out, exist_ok=True)
    summary = {}
    for tool in targets:
        convert(tool, args.out, name, description, body)
        summary[tool] = "ok"

    if args.json:
        json.dump({"skill": name, "tools": summary}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("converted {} -> {}".format(name, ", ".join(targets)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
