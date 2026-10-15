#!/usr/bin/env python
"""Generate a controlled Codex Design Brain memory promotion proposal.

This utility reviews REFLECTION_LOG.md and writes a proposal report. It does
not edit DESIGN_MEMORY.md, DESIGN_PREFERENCES.json, or preference weights.
Promotion remains a manual decision that requires explicit user approval.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "also",
    "because",
    "before",
    "between",
    "clear",
    "codex",
    "design",
    "does",
    "each",
    "entry",
    "feedback",
    "from",
    "have",
    "into",
    "more",
    "next",
    "only",
    "reuse",
    "rule",
    "section",
    "should",
    "that",
    "their",
    "there",
    "this",
    "when",
    "where",
    "with",
    "without",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Codex Design Brain promotion proposal report."
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=2,
        help="Minimum repeated keyword/theme count required for a candidate. Default: 2.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output markdown path. Relative paths resolve from the current directory.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the proposal without saving a file.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path, warnings: list[str]) -> str:
    if not path.exists():
        warnings.append(f"Missing Design Brain file: {path}")
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        warnings.append(f"Could not read {path}: {exc}")
        return ""


def read_preferences(path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        warnings.append(f"Missing Design Brain file: {path}")
        return {}
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid DESIGN_PREFERENCES.json at {path}: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Could not read {path}: {exc}") from exc


def extract_section(block: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)}\s*\n(?P<body>.*?)(?=^### |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(block)
    if not match:
        return ""
    return match.group("body").strip().strip("-").strip()


def parse_reflection_entries(markdown: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    heading_pattern = re.compile(r"^## (?P<title>.+?)\s*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(markdown))

    for index, match in enumerate(matches):
        title = match.group("title").strip()
        if title.lower() == "entry format":
            continue

        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        block = markdown[start:end].strip()
        lesson = extract_section(block, "Design Lesson")
        rule = extract_section(block, "Rule To Reuse Next Time")

        if not lesson and not rule:
            continue

        entries.append(
            {
                "title": title,
                "feedback": extract_section(block, "User Feedback"),
                "went_wrong": extract_section(block, "What Went Wrong"),
                "lesson": lesson,
                "rule": rule,
                "source_report": extract_section(block, "Source Report") or "None",
            }
        )

    return entries


def tokenize_theme_text(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z-]{3,}", text.lower())
    cleaned: set[str] = set()
    for token in tokens:
        token = token.strip("-")
        if token and token not in STOPWORDS:
            cleaned.add(token)
    return cleaned


def theme_counts(entries: list[dict[str, str]]) -> tuple[Counter[str], dict[str, list[int]]]:
    counts: Counter[str] = Counter()
    evidence_indexes: dict[str, list[int]] = defaultdict(list)

    for index, entry in enumerate(entries):
        combined = f"{entry.get('lesson', '')} {entry.get('rule', '')}"
        for token in tokenize_theme_text(combined):
            counts[token] += 1
            evidence_indexes[token].append(index)

    return counts, evidence_indexes


def bullet_summary(markdown: str, max_items: int = 10) -> list[str]:
    items: list[str] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped)
        if len(items) >= max_items:
            break
    return items


def preference_summary(preferences: dict[str, Any]) -> list[str]:
    weights = preferences.get("weights", {})
    if not isinstance(weights, dict):
        return ["- No valid preference weights found."]
    return [f"- {key}: {value}" for key, value in sorted(weights.items())] or [
        "- No preference weights configured."
    ]


def resolve_output_path(root: Path, output: str) -> Path:
    if output:
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        return output_path

    proposals_dir = root / ".design-brain" / "promotion-proposals"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return proposals_dir / f"{timestamp}-promotion-proposal.md"


def recommendation(entries_count: int, min_count: int, repeated_counts: list[int]) -> str:
    if entries_count < min_count or not repeated_counts:
        return "Do not promote yet"
    if max(repeated_counts) >= max(min_count + 1, 3):
        return "Strong repeated pattern, safe to promote manually"
    return "Consider promoting manually"


def build_candidate_sections(
    entries: list[dict[str, str]],
    counts: Counter[str],
    evidence_indexes: dict[str, list[int]],
    min_count: int,
) -> tuple[str, str, str, str, list[int]]:
    repeated = [(token, count) for token, count in counts.most_common() if count >= min_count]
    repeated_counts = [count for _, count in repeated]

    if not repeated:
        empty = "- No repeated lesson themes met the minimum count yet."
        return empty, empty, "- No repeated evidence yet.", "- No manual patch suggested yet.", []

    lesson_lines: list[str] = []
    rule_lines: list[str] = []
    evidence_lines: list[str] = []
    patch_lines: list[str] = ["## Candidate Lessons From Reflection Patterns", ""]

    for token, count in repeated[:10]:
        indexes = evidence_indexes[token]
        lesson_lines.append(f"- Theme `{token}` appeared in {count} reflection entries.")

        strongest_rules = [entries[i]["rule"] for i in indexes if entries[i].get("rule")]
        strongest_lessons = [entries[i]["lesson"] for i in indexes if entries[i].get("lesson")]
        if strongest_rules:
            rule_lines.append(f"- {strongest_rules[0]}")
            patch_lines.append(f"- {strongest_rules[0]}")
        elif strongest_lessons:
            rule_lines.append(f"- {strongest_lessons[0]}")
            patch_lines.append(f"- {strongest_lessons[0]}")

        evidence_lines.append(f"### Theme `{token}`")
        for i in indexes[:5]:
            entry = entries[i]
            evidence_lines.append(f"- Entry: {entry['title']}")
            if entry.get("lesson"):
                evidence_lines.append(f"  - Lesson: {entry['lesson']}")
            if entry.get("rule"):
                evidence_lines.append(f"  - Rule: {entry['rule']}")
        evidence_lines.append("")

    return (
        "\n".join(lesson_lines),
        "\n".join(rule_lines) or "- No candidate rules extracted.",
        "\n".join(evidence_lines).strip(),
        "\n".join(patch_lines).strip(),
        repeated_counts,
    )


def markdown_list(items: list[str], fallback: str) -> str:
    return "\n".join(items) if items else fallback


def build_report(
    reflection_log: str,
    design_memory: str,
    preferences: dict[str, Any],
    min_count: int,
    warnings: list[str],
) -> str:
    entries = parse_reflection_entries(reflection_log)
    counts, evidence_indexes = theme_counts(entries)
    candidate_lessons, candidate_rules, evidence, patch, repeated_counts = build_candidate_sections(
        entries, counts, evidence_indexes, min_count
    )
    rec = recommendation(len(entries), min_count, repeated_counts)
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")

    warning_section = ""
    if warnings:
        warning_section = "\n## Warnings\n\n" + "\n".join(f"- {warning}" for warning in warnings) + "\n"

    evidence_status = ""
    if len(entries) < min_count:
        evidence_status = (
            "\n## Evidence Status\n\n"
            f"- Not enough reflections yet. Found {len(entries)} reflection entries, "
            f"but the minimum repetition count is {min_count}.\n\n"
        )

    return f"""# Design Brain Memory Promotion Proposal

## Metadata

- Date/time: {now}
- Reflection entries found: {len(entries)}
- Minimum repetition count: {min_count}
- Recommendation: {rec}

{warning_section}{evidence_status}## Existing Design Memory Summary

{markdown_list(bullet_summary(design_memory), "- No design memory bullets found.")}

## Existing Preference Weights Summary

{markdown_list(preference_summary(preferences), "- No preference weights available.")}

## Candidate Lessons For Promotion

{candidate_lessons}

## Candidate Rules For DESIGN_MEMORY.md

{candidate_rules}

## Evidence From Reflection Entries

{evidence}

## Risk Of Overfitting

- Do not promote one-off feedback into stable memory.
- Prefer repeated patterns across multiple tasks or explicit user instruction.
- Keep `DESIGN_MEMORY.md` stable and conservative.
- Do not change `DESIGN_PREFERENCES.json` or preference weights from this proposal.

## Manual Patch Suggestion

Add the following to `.design-brain/DESIGN_MEMORY.md` only after explicit approval:

```markdown
{patch}
```
"""


def main() -> int:
    args = parse_args()
    if args.min_count < 1:
        print("ERROR: --min-count must be 1 or greater.", file=sys.stderr)
        return 2

    root = repo_root()
    design_brain = root / ".design-brain"
    warnings: list[str] = []

    reflection_log = read_text(design_brain / "REFLECTION_LOG.md", warnings)
    design_memory = read_text(design_brain / "DESIGN_MEMORY.md", warnings)
    try:
        preferences = read_preferences(design_brain / "DESIGN_PREFERENCES.json", warnings)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    proposal = build_report(
        reflection_log=reflection_log,
        design_memory=design_memory,
        preferences=preferences,
        min_count=args.min_count,
        warnings=warnings,
    )

    if args.dry_run:
        print(proposal, end="")
        return 0

    output_path = resolve_output_path(root, args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(proposal, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write promotion proposal to {output_path}: {exc}", file=sys.stderr)
        return 1

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    print(f"Promotion proposal created: {output_path}")
    print("DESIGN_MEMORY.md and DESIGN_PREFERENCES.json were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
