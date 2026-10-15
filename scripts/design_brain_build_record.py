#!/usr/bin/env python
"""Append template build records and update the naming ledger."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record a template product build in Design Brain journals.")
    parser.add_argument("--template-name", required=True, help="Template product name.")
    parser.add_argument("--template-type", default="", help="Template type.")
    parser.add_argument("--niche", default="", help="Template niche.")
    parser.add_argument("--target-buyer", default="", help="Target buyer.")
    parser.add_argument("--marketplace", default="", help="Marketplace category or channel.")
    parser.add_argument("--style-packs", default="", help="Selected style packs or TypeUI skills.")
    parser.add_argument("--section-structure", default="", help="Section structure summary.")
    parser.add_argument("--preview-direction", default="", help="Preview or cover direction.")
    parser.add_argument("--editable-areas", default="", help="Editable areas in the template.")
    parser.add_argument("--originality-note", default="", help="What made the result original.")
    parser.add_argument("--avoid-next-time", default="", help="What not to repeat next time.")
    parser.add_argument("--related-report", default="", help="Related report path.")
    parser.add_argument("--reference-mode", default="", help="single, pair, or triple reference usage mode.")
    parser.add_argument("--references-used", default="", help="Reference IDs or names used by the template.")
    parser.add_argument("--reference-group-key", default="", help="Reference usage registry group key.")
    parser.add_argument("--style-dna-summary", default="", help="Abstract Style DNA learned from the allowed reference group.")
    parser.add_argument("--brand-reference-usage-receipt", default="", help="Brand/reference usage gate or registry record path.")
    parser.add_argument("--dry-run", action="store_true", help="Print records without writing files.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def now_label() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z%z")


def value_or_placeholder(value: str) -> str:
    return value.strip() or "Not specified"


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", value.lower())


def naming_pattern(name: str) -> str:
    parts = tokens(name)
    if len(parts) >= 2:
        return "two-word compound / phrase"
    if len(parts) == 1:
        return "single coined or brand word"
    return "unknown"


def metaphor_category(name: str, niche: str) -> str:
    text = f"{name} {niche}".lower()
    if any(word in text for word in ["vow", "atelier", "studio", "bridal", "wedding"]):
        return "wedding / craft / studio"
    if any(word in text for word in ["care", "fix", "home", "repair"]):
        return "service / home / repair"
    if any(word in text for word in ["index", "journal", "press", "letter", "daily"]):
        return "editorial / publishing"
    if any(word in text for word in ["pilot", "spring", "network", "flow", "hub"]):
        return "platform / system"
    return "general marketplace brand"


def prefix_suffix(name: str) -> str:
    parts = tokens(name)
    if not parts:
        return "Not specified"
    if len(parts) == 1:
        return f"prefix/suffix: {parts[0]}"
    return f"prefix: {parts[0]}, suffix: {parts[-1]}"


def words_used(name: str) -> str:
    parts = tokens(name)
    return ", ".join(parts) if parts else "Not specified"


def reference_insight_record(args: argparse.Namespace) -> str:
    values = [
        f"- Reference mode: {value_or_placeholder(args.reference_mode)}",
        f"- References used: {value_or_placeholder(args.references_used)}",
        f"- Reference group key: {value_or_placeholder(args.reference_group_key)}",
        f"- Style DNA summary: {value_or_placeholder(args.style_dna_summary)}",
    ]
    return "\n".join(values)


def build_record(args: argparse.Namespace) -> str:
    date = now_label()
    return f"""## {date} - [{args.template_name}]

### Template Name

{value_or_placeholder(args.template_name)}

### Template Type

{value_or_placeholder(args.template_type)}

### Niche

{value_or_placeholder(args.niche)}

### Target Buyer

{value_or_placeholder(args.target_buyer)}

### Marketplace Category

{value_or_placeholder(args.marketplace)}

### Selected Style Packs

{value_or_placeholder(args.style_packs)}

### Used Reference Insights

{reference_insight_record(args)}

### Brand Reference Usage Receipt

{value_or_placeholder(args.brand_reference_usage_receipt)}

### Section Structure

{value_or_placeholder(args.section_structure)}

### Preview / Cover Direction

{value_or_placeholder(args.preview_direction)}

### Editable Areas

{value_or_placeholder(args.editable_areas)}

### What Made It Original

{value_or_placeholder(args.originality_note)}

### What To Avoid Repeating Next Time

{value_or_placeholder(args.avoid_next_time)}

### Related Reports

{value_or_placeholder(args.related_report)}

---
"""


def ledger_record(args: argparse.Namespace) -> str:
    date = now_label()
    return f"""## {date} - [{args.template_name}]

### Niche

{value_or_placeholder(args.niche)}

### Template Type

{value_or_placeholder(args.template_type)}

### Naming Pattern

{naming_pattern(args.template_name)}

### Words Used

{words_used(args.template_name)}

### Prefix / Suffix Used

{prefix_suffix(args.template_name)}

### Metaphor Category

{metaphor_category(args.template_name, args.niche)}

### Similarity Risk

Not scored here. Run `scripts/design_brain_name_check.py` before final naming decisions.

### Avoid List For Future Names

{value_or_placeholder(args.avoid_next_time)}

---
"""


def ensure_file(path: Path, title: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n", encoding="utf-8", newline="\n")


def append(path: Path, title: str, content: str) -> None:
    ensure_file(path, title)
    existing = path.read_text(encoding="utf-8")
    separator = "" if existing.endswith("\n") else "\n"
    path.write_text(existing + separator + "\n" + content, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    root = design_brain_root()
    record = build_record(args)
    ledger = ledger_record(args)

    if args.dry_run:
        print("# Build Journal Entry")
        print("")
        print(record)
        print("# Naming Ledger Entry")
        print("")
        print(ledger)
        return 0

    build_path = root / ".design-brain" / "TEMPLATE_BUILD_JOURNAL.md"
    ledger_path = root / ".design-brain" / "TEMPLATE_NAMING_LEDGER.md"
    append(build_path, "Template Build Journal", record)
    append(ledger_path, "Template Naming Ledger", ledger)

    print(f"Template build record appended: {build_path}")
    print(f"Template naming ledger updated: {ledger_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
