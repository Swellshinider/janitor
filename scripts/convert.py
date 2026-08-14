#!/usr/bin/env python3
"""Convert the janitor skills into per-tool integration bundles.

Usage:
    convert.py [--tool {codex,cursor,copilot,gemini,openclaw,opencode,all}] [--out DIR] [--json]

Single source: every skills/<name>/SKILL.md under skills/. Output (committed)
lets each tool install by copy only. Claude Code is not listed here: it installs
janitor as a plugin via .claude-plugin/, which bundles skills/ directly.

- codex: full skill bundle per skill (SKILL.md + references + scripts), native
  SKILL.md reader. Install by marketplace or copy to ~/.agents/skills/<name>.
- cursor: a .cursor/rules/<name>.mdc rule per skill, generated from the source.
- copilot: a single .github/copilot-instructions.md with every skill body.
- gemini: a single context file with every skill body.
- openclaw: a SKILL.md package per skill with OpenClaw-friendly frontmatter.
- opencode: a command file plus a full skill bundle per skill.

# ponytail: frontmatter is parsed with a tiny regex, not a YAML library. That is
# fine because we own the sources and they only ever have name + description.
# Switch to PyYAML if arbitrary frontmatter must be supported.
"""
import argparse
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
HOMEPAGE = "https://github.com/Swellshinider/janitor"

# OpenClaw requires a description under 160 chars; the full parsed description is
# used everywhere else. This is the only per-skill metadata not derivable from
# skills/<name>/SKILL.md. Skills are discovered by scanning SKILLS_DIR, so keys
# here must match each skill's directory name.
OPENCLAW_DESCRIPTIONS = {
    "cleaner": (
        "Behavior-preserving cleanup: dead code removal, file splitting, and "
        "deduplication without public API changes."
    ),
    "docs-cleaner": (
        "Documentation audit and cleanup for README, community files, and "
        "links without changing code behavior."
    ),
    "manager": (
        "Behavior-preserving structural refactor: split oversized files and "
        "regroup directories, with re-exports keeping the public surface stable."
    ),
}

TOOLS = ("codex", "cursor", "copilot", "gemini", "openclaw", "opencode")


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


def load_skills():
    """Discover and parse every skills/<name>/SKILL.md."""
    out = []
    for name in sorted(
        d for d in os.listdir(SKILLS_DIR)
        if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith(".")
    ):
        source_dir = os.path.join(SKILLS_DIR, name)
        skill_path = os.path.join(source_dir, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue
        with open(skill_path, "r", encoding="utf-8") as f:
            text = f.read()
        parsed_name, description, body = parse_skill(text)
        if not parsed_name or not description:
            sys.stderr.write("could not parse name/description from {}\n".format(skill_path))
            sys.exit(2)
        if parsed_name != name:
            sys.stderr.write(
                "skill dir {} has frontmatter name {!r}; names must match\n".format(name, parsed_name)
            )
            sys.exit(2)
        if name not in OPENCLAW_DESCRIPTIONS:
            sys.stderr.write(
                "no openclaw_description for skill {}; add it to OPENCLAW_DESCRIPTIONS\n".format(name)
            )
            sys.exit(2)
        out.append({
            "name": name,
            "source_dir": source_dir,
            "description": description,
            "body": body,
            "openclaw_description": OPENCLAW_DESCRIPTIONS[name],
        })
    return out


def copy_bundle(source_dir, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(
        source_dir, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )


def write_cursor(out_dir, skill):
    rules = os.path.join(out_dir, "cursor", "rules")
    os.makedirs(rules, exist_ok=True)
    content = (
        "---\n"
        "description: " + yaml_quote(skill["description"]) + "\n"
        "globs:\n"
        "alwaysApply: false\n"
        "---\n"
        + skill["body"] + "\n"
    )
    with open(os.path.join(rules, skill["name"] + ".mdc"), "w", encoding="utf-8") as f:
        f.write(content)


def write_copilot(out_dir, skills):
    copilot = os.path.join(out_dir, "copilot")
    os.makedirs(copilot, exist_ok=True)
    # Single instructions file: concatenate every skill body (each starts with its H1).
    body = "\n\n".join(s["body"] for s in skills)
    with open(os.path.join(copilot, "copilot-instructions.md"), "w", encoding="utf-8") as f:
        f.write(body + "\n")


def write_gemini(out_dir, skills):
    gemini = os.path.join(out_dir, "gemini")
    os.makedirs(gemini, exist_ok=True)
    parts = ["# Janitor"]
    for s in skills:
        parts.append("Activation: {}\n\n{}".format(s["description"], s["body"]))
    with open(os.path.join(gemini, "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts) + "\n")


def write_openclaw(out_dir, skill):
    desc = skill["openclaw_description"]
    if len(desc) > 160:
        raise ValueError(
            "OpenClaw description for {} must stay under 160 chars".format(skill["name"])
        )
    target = os.path.join(out_dir, "openclaw", "skills", skill["name"])
    os.makedirs(target, exist_ok=True)
    content = (
        "---\n"
        "name: {name}\n"
        "description: {description}\n"
        "homepage: {homepage}\n"
        "license: MIT\n"
        "---\n"
        "{body}\n"
    ).format(
        name=skill["name"],
        description=yaml_quote(desc),
        homepage=HOMEPAGE,
        body=skill["body"],
    )
    with open(os.path.join(target, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(content)


def write_opencode(out_dir, skill):
    root = os.path.join(out_dir, "opencode")
    commands = os.path.join(root, "command")
    os.makedirs(commands, exist_ok=True)
    with open(os.path.join(commands, skill["name"] + ".md"), "w", encoding="utf-8") as f:
        f.write("---\ndescription: {}\n---\n\n{}\n".format(
            yaml_quote(skill["description"]), skill["body"]))
    copy_bundle(skill["source_dir"], os.path.join(root, "skills", skill["name"]))


def convert(tool, out_dir, skills):
    if tool == "codex":
        for s in skills:
            copy_bundle(s["source_dir"], os.path.join(out_dir, tool, "skills", s["name"]))
    elif tool == "cursor":
        for s in skills:
            write_cursor(out_dir, s)
    elif tool == "copilot":
        write_copilot(out_dir, skills)
    elif tool == "gemini":
        write_gemini(out_dir, skills)
    elif tool == "openclaw":
        for s in skills:
            write_openclaw(out_dir, s)
    elif tool == "opencode":
        for s in skills:
            write_opencode(out_dir, s)
    else:
        raise ValueError("unknown tool: " + tool)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tool", default="all", choices=TOOLS + ("all",), help="target tool (default: all)")
    ap.add_argument("--out", default=os.path.join(REPO_ROOT, "integrations"), help="output dir")
    ap.add_argument("--json", action="store_true", help="emit JSON summary")
    args = ap.parse_args(argv)

    skills = load_skills()

    targets = TOOLS if args.tool == "all" else (args.tool,)
    # A full run regenerates a clean tree so retired tools or skills do not
    # linger. A single-tool run wipes just that tool's output, so a retired
    # skill does not linger in the regenerated bundle.
    if args.tool == "all" and os.path.isdir(args.out):
        shutil.rmtree(args.out)
    elif args.tool != "all":
        shutil.rmtree(os.path.join(args.out, args.tool), ignore_errors=True)
    os.makedirs(args.out, exist_ok=True)
    summary = {}
    for tool in targets:
        convert(tool, args.out, skills)
        summary[tool] = "ok"

    if args.json:
        json.dump({"skills": [s["name"] for s in skills], "tools": summary}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print("converted {} skills -> {}".format(len(skills), ", ".join(targets)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
