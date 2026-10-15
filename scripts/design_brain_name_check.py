#!/usr/bin/env python
"""Check template name originality against the local naming ledger."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


STOPWORDS = {
    "the",
    "and",
    "for",
    "template",
    "landing",
    "page",
    "site",
    "website",
    "figma",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a template name against the naming ledger.")
    parser.add_argument("--candidate-name", required=True, help="Candidate template name.")
    parser.add_argument("--niche", default="", help="Template niche.")
    parser.add_argument("--template-type", default="", help="Template type.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print report without saving.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def normalize_tokens(value: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9]+", value.lower())
    return [token for token in tokens if token not in STOPWORDS]


def compact(value: str) -> str:
    return " ".join(normalize_tokens(value))


def ledger_entries(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    chunks = re.split(r"(?m)^##\s+", text)
    entries: list[dict[str, str]] = []
    for chunk in chunks:
        if not chunk.strip() or chunk.lower().startswith("template naming ledger"):
            continue
        heading = chunk.splitlines()[0].strip()
        if not re.match(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}", heading):
            continue
        name = heading
        if " - [" in heading and heading.endswith("]"):
            name = heading.rsplit(" - [", 1)[1][:-1]
        niche = extract_section(chunk, "Niche")
        template_type = extract_section(chunk, "Template Type")
        entries.append({"name": name.strip(), "niche": niche.strip(), "template_type": template_type.strip()})
    return entries


def extract_section(text: str, title: str) -> str:
    pattern = rf"(?ms)^###\s+{re.escape(title)}\s*\n\n(.*?)(?=\n###\s+|\n---|\Z)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def similarity_report(candidate: str, niche: str, template_type: str, entries: list[dict[str, str]]) -> dict[str, object]:
    candidate_tokens = normalize_tokens(candidate)
    candidate_set = set(candidate_tokens)
    candidate_compact = compact(candidate)
    candidate_prefix = candidate_tokens[0] if candidate_tokens else ""
    candidate_suffix = candidate_tokens[-1] if candidate_tokens else ""
    niche_compact = compact(niche)

    similar: list[str] = []
    exact_matches: list[str] = []
    shared_word_matches: list[str] = []
    prefix_suffix_matches: list[str] = []
    niche_matches: list[str] = []
    max_shared = 0

    for entry in entries:
        existing_name = entry["name"]
        existing_tokens = normalize_tokens(existing_name)
        existing_set = set(existing_tokens)
        existing_compact = compact(existing_name)
        shared = sorted(candidate_set & existing_set)
        max_shared = max(max_shared, len(shared))

        if candidate_compact and candidate_compact == existing_compact:
            exact_matches.append(existing_name)
        if shared:
            shared_word_matches.append(f"{existing_name} ({', '.join(shared)})")
        if existing_tokens and (
            candidate_prefix == existing_tokens[0] or candidate_suffix == existing_tokens[-1]
        ):
            prefix_suffix_matches.append(existing_name)
        if niche_compact and niche_compact == compact(entry.get("niche", "")):
            niche_matches.append(existing_name)
        if shared or existing_name in exact_matches or existing_name in prefix_suffix_matches:
            similar.append(existing_name)

    score = 10
    if exact_matches:
        score -= 8
    score -= min(max_shared * 2, 4)
    if prefix_suffix_matches:
        score -= 2
    if niche_matches:
        score -= 1
    score = max(score, 1)

    if exact_matches or score <= 4:
        recommendation = "reject"
    elif score <= 7:
        recommendation = "revise"
    else:
        recommendation = "safe"

    return {
        "similar": sorted(set(similar)),
        "exact_matches": exact_matches,
        "shared_word_matches": shared_word_matches,
        "prefix_suffix_matches": prefix_suffix_matches,
        "niche_matches": niche_matches,
        "score": score,
        "recommendation": recommendation,
        "alternative_direction": alternative_direction(candidate_tokens, niche, template_type),
    }


def alternative_direction(tokens: list[str], niche: str, template_type: str) -> str:
    used_shape = " ".join(tokens[:1] + tokens[-1:]) if tokens else "the current pattern"
    niche_text = niche or "the niche"
    type_text = template_type or "the template type"
    return (
        f"Explore a different metaphor and word shape than {used_shape}. "
        f"Anchor the name in {niche_text} and make the {type_text} category clear without reusing the same prefix or suffix."
    )


def list_or_none(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


def build_report(args: argparse.Namespace, entries: list[dict[str, str]]) -> str:
    report = similarity_report(args.candidate_name, args.niche, args.template_type, entries)
    return f"""# Template Name Check

Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}

## Candidate Name

{args.candidate_name}

## Context

- Niche: {args.niche or 'Not specified'}
- Template type: {args.template_type or 'Not specified'}
- Existing ledger entries checked: {len(entries)}

## Existing Similar Names

{list_or_none(report['similar'])}

## Similarity Risks

- Exact match risk: {'high' if report['exact_matches'] else 'low'}
- Shared word risk: {'high' if report['shared_word_matches'] else 'low'}
- Same prefix/suffix risk: {'high' if report['prefix_suffix_matches'] else 'low'}
- Same niche repetition risk: {'high' if report['niche_matches'] else 'low'}

## Risk Evidence

### Exact Matches

{list_or_none(report['exact_matches'])}

### Shared Word Matches

{list_or_none(report['shared_word_matches'])}

### Prefix / Suffix Matches

{list_or_none(report['prefix_suffix_matches'])}

### Same Niche Matches

{list_or_none(report['niche_matches'])}

## Originality Score

{report['score']}/10

## Recommendation

{report['recommendation']}

## Alternative Direction

{report['alternative_direction']}
"""


def main() -> int:
    args = parse_args()
    root = design_brain_root()
    entries = ledger_entries(root / ".design-brain" / "TEMPLATE_NAMING_LEDGER.md")
    report = build_report(args, entries)

    if args.dry_run or not args.output:
        print(report)
        if not args.dry_run and not args.output:
            print("No --output provided; report was not saved.")
        return 0

    path = Path(args.output).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Template name check written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
