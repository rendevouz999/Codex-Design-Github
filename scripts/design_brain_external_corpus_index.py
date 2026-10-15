#!/usr/bin/env python
"""Create a selective external-corpus index for Design Brain."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_modules import repo_root, slugify


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index an external design/skill corpus.")
    parser.add_argument("--root", required=True, help="External repo root.")
    parser.add_argument("--kind", required=True, choices=["open-design", "awesome-claude-skills", "generic"], help="Corpus kind.")
    parser.add_argument("--output", default="", help="Optional output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON without writing.")
    return parser.parse_args()


def parse_frontmatter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, Any] = {}
    current_key = ""
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if re.match(r"^[A-Za-z0-9_-]+:", line):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip().strip('"').strip("'")
        elif current_key and line.strip().startswith("-"):
            existing = data.get(current_key)
            if not isinstance(existing, list):
                existing = [] if not existing else [existing]
            existing.append(line.strip()[1:].strip().strip('"').strip("'"))
            data[current_key] = existing
    return data


def file_summary(root: Path) -> dict[str, Any]:
    files = [path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts]
    return {
        "fileCount": len(files),
        "topDirs": dict(Counter(path.relative_to(root).parts[0] for path in files if path.relative_to(root).parts).most_common(20)),
        "topExtensions": dict(Counter(path.suffix.lower() or "[none]" for path in files).most_common(20)),
    }


def skill_summary(root: Path, limit: int = 160) -> dict[str, Any]:
    skill_paths = sorted(path for path in root.rglob("SKILL.md") if ".git" not in path.parts)
    skills: list[dict[str, Any]] = []
    mode_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    for path in skill_paths[:limit]:
        data = parse_frontmatter(path)
        od_mode = ""
        od_category = ""
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        mode_match = re.search(r"^\s*mode:\s*([A-Za-z0-9_-]+)", text, re.MULTILINE)
        category_match = re.search(r"^\s*category:\s*([A-Za-z0-9_-]+)", text, re.MULTILINE)
        if mode_match:
            od_mode = mode_match.group(1)
            mode_counts[od_mode] += 1
        if category_match:
            od_category = category_match.group(1)
            category_counts[od_category] += 1
        skills.append(
            {
                "path": str(path.relative_to(root)),
                "name": data.get("name") or path.parent.name,
                "description": data.get("description", ""),
                "mode": od_mode,
                "category": od_category,
            }
        )
    return {
        "skillCount": len(skill_paths),
        "sampledSkillCount": len(skills),
        "modeCounts": dict(mode_counts.most_common()),
        "categoryCounts": dict(category_counts.most_common()),
        "skills": skills,
    }


def open_design_details(root: Path) -> dict[str, Any]:
    return {
        "craftModules": sorted(path.stem for path in (root / "craft").glob("*.md") if path.name.lower() != "readme.md") if (root / "craft").exists() else [],
        "designSystemCount": len([path for path in (root / "design-systems").iterdir() if path.is_dir()]) if (root / "design-systems").exists() else 0,
        "designTemplateCount": len([path for path in (root / "design-templates").iterdir() if path.is_dir()]) if (root / "design-templates").exists() else 0,
        "notableLessons": [
            "Separate artifact shape, brand design system, and universal craft.",
            "Use seed templates, layout references, and P0/P1/P2 checklists per skill.",
            "Use deterministic direction packs instead of vague style adjectives.",
            "Lint obvious AI-default patterns before final output.",
        ],
    }


def awesome_details(root: Path) -> dict[str, Any]:
    document_skills = root / "document-skills"
    return {
        "documentSkillDirs": sorted(path.name for path in document_skills.iterdir() if path.is_dir()) if document_skills.exists() else [],
        "topLevelDesignRelevant": [
            name
            for name in ["canvas-design", "theme-factory", "webapp-testing", "brand-guidelines", "skill-creator", "document-skills"]
            if (root / name).exists()
        ],
        "notableLessons": [
            "Keep SKILL.md lean and move repeated details into scripts, references, and assets.",
            "Treat helper scripts as black boxes when possible.",
            "Use PPTX inventory, thumbnail, and OOXML validation helpers for slide work.",
            "Use skill creation and packaging checks to preserve reusable capability quality.",
        ],
    }


def build_index(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).expanduser().resolve()
    data: dict[str, Any] = {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "kind": args.kind,
        "root": str(root),
        "mode": "generated selective index; not stable memory",
        "summary": file_summary(root),
        "skills": skill_summary(root),
    }
    if args.kind == "open-design":
        data["openDesign"] = open_design_details(root)
    elif args.kind == "awesome-claude-skills":
        data["awesomeClaudeSkills"] = awesome_details(root)
    return data


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "external-indexes" / f"{stamp}-{slugify(args.kind)}.json"


def main() -> int:
    configure_stdout()
    args = parse_args()
    data = build_index(args)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if args.dry_run:
        print(text)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"External corpus index written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
