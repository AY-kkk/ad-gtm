#!/usr/bin/env python3
"""List, validate, install and package the Ad GTM skill collection."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def catalog(root=ROOT):
    data = json.loads((root / "registry/skills.json").read_text(encoding="utf-8"))
    require(re.fullmatch(r"\d+\.\d+\.\d+", data["version"]), "Invalid version")
    names = [item["name"] for item in data["skills"]]
    require(names and len(names) == len(set(names)), "Duplicate or empty skill catalog")
    require(all(NAME.fullmatch(n) for n in names), "Invalid skill name")
    for pack, members in data["packs"].items():
        require(NAME.fullmatch(pack), "Invalid pack name")
        require(members and len(members) == len(set(members)), f"Invalid pack: {pack}")
        require(set(members) <= set(names), f"Unknown skill in pack: {pack}")
    require(set(data["packs"]["all"]) == set(names), "all pack must include every skill")
    return data


def frontmatter(path):
    """Read the collection's two single-line frontmatter fields (not a YAML parser)."""
    text = path.read_text(encoding="utf-8")
    require(text.startswith("---\n") and "\n---\n" in text[4:], f"Missing frontmatter: {path}")
    header = text.split("---", 2)[1]
    result = {}
    for line in header.strip().splitlines():
        key, sep, value = line.partition(":")
        require(sep and key in {"name", "description"} and key not in result,
                f"Use unique name/description single-line fields: {path}")
        result[key] = value.strip()
    require(set(result) == {"name", "description"} and all(result.values()),
            f"Incomplete frontmatter: {path}")
    return result


def skill_files(root, name):
    folder = root / "skills" / name
    require(folder.is_dir() and not folder.is_symlink(), f"Invalid skill directory: {name}")
    files = []
    for path in sorted(folder.rglob("*")):
        require(not path.is_symlink(), f"Symlinks cannot be packaged: {path}")
        if path.is_file():
            require(path.suffix in {".md", ".yaml", ".json"}, f"Unexpected skill file: {path}")
            files.append(path)
    return files


def check_links(path, boundary):
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        if target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        link = target.split("#", 1)[0]
        resolved = (path.parent / link).resolve()
        require(resolved.is_relative_to(boundary.resolve()), f"Link leaves package: {path}: {target}")
        require(resolved.exists(), f"Broken link: {path}: {target}")


def validate(root=ROOT):
    data = catalog(root)
    names = {item["name"] for item in data["skills"]}
    discovered = {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}
    require(names == discovered, "Catalog and skill directories differ")
    for name in names:
        folder = root / "skills" / name
        meta = frontmatter(folder / "SKILL.md")
        require(meta["name"] == name, f"Frontmatter name mismatch: {name}")
        for path in skill_files(root, name):
            if path.suffix == ".md":
                check_links(path, folder)
        ui = (folder / "agents/openai.yaml").read_text(encoding="utf-8")
        fields = dict(re.findall(r'^  ([a-z_]+): (".*")$', ui, re.MULTILINE))
        values = {key: json.loads(value) for key, value in fields.items()}
        require({"display_name", "short_description", "default_prompt"} <= values.keys(),
                f"Missing UI metadata: {name}")
        require(25 <= len(values["short_description"]) <= 64, f"UI description length: {name}")
        require(f"${name}" in values["default_prompt"], f"UI invocation mismatch: {name}")
    docs = list(root.glob("*.md"))
    for subdir in ["docs", "examples", "evals"]:
        docs.extend((root / subdir).rglob("*.md"))
    for path in docs:
        check_links(path, root)
    cases = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
    require(len({c["id"] for c in cases}) == len(cases), "Duplicate evaluation case ID")
    require(names <= {n for c in cases for n in c["skills"]}, "Skills missing evaluation cases")
    for case in cases:
        require(set(case["skills"]) <= names, f"Unknown evaluation skill: {case['id']}")
        require(case["prompt"] and case["must"] and case["must_not"], "Incomplete evaluation case")
    return data


def select(data, pack=None, skill=None):
    if skill:
        require(skill in {s["name"] for s in data["skills"]}, f"Unknown skill: {skill}")
        return [skill]
    require(pack in data["packs"], f"Unknown pack: {pack}")
    return data["packs"][pack]


def install(root, names, target, replace=False):
    target = target.expanduser().resolve()
    source = root.resolve()
    for name in names:
        dest = target / name
        require(not dest.is_symlink(), f"Refusing symlink destination: {dest}")
        require(not source.is_relative_to(dest) and not dest.is_relative_to(source),
                "Installation overlaps the repository; clone to a separate working directory")
        require(not dest.exists() or replace, f"Already installed: {dest}; use --replace to back it up")
        require(not dest.exists() or dest.is_dir(), f"Destination is not a directory: {dest}")
    backup_parent = target.parent / ".ad-gtm-backups"
    require(not backup_parent.is_symlink(), "Refusing symlink backup directory")
    target.mkdir(parents=True, exist_ok=True)
    backup = backup_parent / uuid.uuid4().hex
    placed, moved = [], []
    with tempfile.TemporaryDirectory(prefix=".ad-gtm-stage-", dir=target) as staging:
        stage = Path(staging)
        for name in names:
            shutil.copytree(root / "skills" / name, stage / name)
        try:
            for name in names:
                dest = target / name
                if dest.exists():
                    backup.mkdir(parents=True, exist_ok=True)
                    os.replace(dest, backup / name)
                    moved.append(name)
                os.replace(stage / name, dest)
                placed.append(name)
        except Exception:
            for name in reversed(placed):
                shutil.rmtree(target / name)
            for name in reversed(moved):
                os.replace(backup / name, target / name)
            raise
    return {"installed": names, "target": str(target), "backup": str(backup) if moved else None}


def build(root, data, names, label, output):
    content = {}
    for name in names:
        for path in skill_files(root, name):
            content[path.relative_to(root).as_posix()] = path.read_bytes()
    content["LICENSE"] = (root / "LICENSE").read_bytes()
    content["INSTALL.md"] = (
        "# Ad GTM Skills\n\nCopy the required complete directories under skills/ to your Agent's skill directory.\n"
        "Back up existing same-name directories first. Restart the Agent session after installation.\n"
        "The collection has no built-in video generation or ad buying client.\n"
        "Guide: https://github.com/AY-kkk/ad-gtm\n"
    ).encode()
    manifest = {"version": data["version"], "pack": label, "skills": names,
                "sha256": {p: hashlib.sha256(b).hexdigest() for p, b in sorted(content.items())}}
    content["manifest.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / f"ad-gtm-{label}-{data['version']}.zip"
    with tempfile.TemporaryDirectory(prefix=".build-", dir=output) as work:
        archive = Path(work) / "bundle.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path, blob in sorted(content.items()):
                info = zipfile.ZipInfo(path, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, blob)
        os.replace(archive, destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(".zip.sha256").write_text(f"{digest}  {destination.name}\n", encoding="utf-8")
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("validate")
    for command in ["install", "build"]:
        p = sub.add_parser(command)
        choice = p.add_mutually_exclusive_group(required=True)
        choice.add_argument("--pack")
        choice.add_argument("--skill")
        if command == "install":
            p.add_argument("--target", type=Path, required=True)
            p.add_argument("--replace", action="store_true")
        else:
            p.add_argument("--output", type=Path, default=Path("dist"))
    args = parser.parse_args(argv)
    try:
        data = validate()
        if args.command == "list":
            for item in data["skills"]:
                print(f"{item['name']:18} {item['group']} | {item['outcome']}")
            print("\nPacks: " + ", ".join(f"{k} ({len(v)})" for k, v in data["packs"].items()))
        elif args.command == "validate":
            print(f"Valid: {len(data['skills'])} skills; {len(data['packs'])} packs; local links and evaluation coverage")
        else:
            names = select(data, args.pack, args.skill)
            if args.command == "install":
                print(json.dumps(install(ROOT, names, args.target, args.replace), ensure_ascii=False, indent=2))
            else:
                print(build(ROOT, data, names, args.pack or args.skill, args.output))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
