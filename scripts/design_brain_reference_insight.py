#!/usr/bin/env python
"""Store reference insights without copying the reference."""

from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a reference insight entry from human/Codex-described observations."
    )
    parser.add_argument("--reference-name", required=True, help="Reference name or source label.")
    parser.add_argument("--reference-type", default="", help="Reference type, such as screenshot or website.")
    parser.add_argument("--template-category", default="", help="Template category this reference informs.")
    parser.add_argument("--observed-intent", default="", help="What the reference is trying to achieve.")
    parser.add_argument("--buyer-decision-model", default="", help="Who buys the template, what it must prove, and what would make it commercially useful or rejectable.")
    parser.add_argument("--cognition-evidence", default="", help="Evidence-backed designer cognition claims with confidence levels.")
    parser.add_argument("--attention-strategy", default="", help="Where attention goes first, second, and third, and why.")
    parser.add_argument("--emotional-rhythm", default="", help="Where the reference is calm, dense, loud, quiet, persuasive, or premium, and why.")
    parser.add_argument("--trust-strategy", default="", help="How the reference builds credibility.")
    parser.add_argument("--density-strategy", default="", help="Where detail is added or removed, and why.")
    parser.add_argument("--conversion-logic", default="", help="How the reference moves the viewer toward action.")
    parser.add_argument("--component-reasoning", default="", help="Why specific components are used, not only what components appear.")
    parser.add_argument("--repeated-designer-pattern", default="", help="Repeated decision pattern seen across related references.")
    parser.add_argument("--visual-mood", default="", help="Observed visual mood.")
    parser.add_argument("--color-role-insight", default="", help="What the reference colors do for mood, hierarchy, CTA, proof, surfaces, and buyer effect.")
    parser.add_argument("--palette-reconstruction", default="", help="How the new template should reconstruct color roles without copying the reference palette.")
    parser.add_argument("--structural-insight", default="", help="Reusable structural insight.")
    parser.add_argument("--section-count-judgment", default="", help="How to infer a normal product-standard section count without blindly matching the reference or forcing minimal/long structure.")
    parser.add_argument("--hierarchy-insight", default="", help="Reusable hierarchy insight.")
    parser.add_argument("--section-flow-insight", default="", help="Reusable section/content flow insight.")
    parser.add_argument("--marketplace-insight", default="", help="Marketplace value insight.")
    parser.add_argument("--lesson", default="", help="Reusable design lesson.")
    parser.add_argument("--do-not-copy", default="", help="Specific details that must not be copied.")
    parser.add_argument("--reinterpretation", default="", help="How to reinterpret the insight later.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--dry-run", action="store_true", help="Print entry without writing files.")
    return parser.parse_args()


def design_brain_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "reference-insight"


def value_or_placeholder(value: str) -> str:
    return value.strip() or "Not specified"


def now_label() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z%z")


def build_entry(args: argparse.Namespace) -> str:
    date = now_label()
    return f"""## {date} - [{args.reference_name}]

### Reference Name Or Source

{value_or_placeholder(args.reference_name)}

### Reference Type

{value_or_placeholder(args.reference_type)}

### Template Category

{value_or_placeholder(args.template_category)}

### Observed Design Intent

{value_or_placeholder(args.observed_intent)}

### Buyer Decision Model

{value_or_placeholder(args.buyer_decision_model)}

### Designer Cognition Evidence

{value_or_placeholder(args.cognition_evidence)}

### Attention Strategy

{value_or_placeholder(args.attention_strategy)}

### Emotional Rhythm

{value_or_placeholder(args.emotional_rhythm)}

### Trust Strategy

{value_or_placeholder(args.trust_strategy)}

### Density Strategy

{value_or_placeholder(args.density_strategy)}

### Conversion / Action Logic

{value_or_placeholder(args.conversion_logic)}

### Component Reasoning

{value_or_placeholder(args.component_reasoning)}

### Repeated Designer Pattern

{value_or_placeholder(args.repeated_designer_pattern)}

### Visual Mood

{value_or_placeholder(args.visual_mood)}

### Color Role Insight

{value_or_placeholder(args.color_role_insight)}

### Palette Reconstruction Plan

{value_or_placeholder(args.palette_reconstruction)}

### Structural Insight

{value_or_placeholder(args.structural_insight)}

### Section Count Judgment

{value_or_placeholder(args.section_count_judgment)}

### Hierarchy Insight

{value_or_placeholder(args.hierarchy_insight)}

### Section Flow Insight

{value_or_placeholder(args.section_flow_insight)}

### Marketplace Insight

{value_or_placeholder(args.marketplace_insight)}

### Reusable Lesson

{value_or_placeholder(args.lesson)}

### Do-Not-Copy Notes

{value_or_placeholder(args.do_not_copy)}

### How To Reinterpret In Future Template Products

{value_or_placeholder(args.reinterpretation)}

### Provenance Note

This entry stores described insight only. The script does not analyze images, open URLs, or copy reference layouts.

---
"""


def output_path(args: argparse.Namespace, root: Path) -> Path:
    if args.output:
        return Path(args.output).expanduser().resolve()
    filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.reference_name)}.md"
    return root / ".design-brain" / "reference-insights" / filename


def ensure_journal(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Reference Insight Journal\n\nStore accumulated lessons from user-provided references here.\n\n",
        encoding="utf-8",
        newline="\n",
    )


def append_entry(path: Path, entry: str) -> None:
    ensure_journal(path)
    existing = path.read_text(encoding="utf-8")
    separator = "" if existing.endswith("\n") else "\n"
    path.write_text(existing + separator + "\n" + entry, encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    root = design_brain_root()
    entry = build_entry(args)

    if args.dry_run:
        print(entry)
        return 0

    path = output_path(args, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(entry, encoding="utf-8", newline="\n")

    journal_path = root / ".design-brain" / "REFERENCE_INSIGHT_JOURNAL.md"
    append_entry(journal_path, entry)

    print(f"Reference insight written: {path}")
    print(f"Reference insight appended to journal: {journal_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
