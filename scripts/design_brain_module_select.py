#!/usr/bin/env python
"""Select Design Brain modules for a design-anything task."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from design_brain_modules import build_selection, bullet, repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select craft, seed, direction, and validators.")
    parser.add_argument("--task", required=True, help="Natural-language task.")
    parser.add_argument("--template-type", default="", help="Optional template/product type.")
    parser.add_argument("--niche", default="", help="Optional niche.")
    parser.add_argument("--target-buyer", default="", help="Optional target buyer.")
    parser.add_argument("--visual-mood", default="", help="Optional visual mood.")
    parser.add_argument("--output", default="", help="Optional output markdown path.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    return parser.parse_args()


def slugify(value: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-") or "module-selection"


def build_report(args: argparse.Namespace, selection: dict) -> str:
    direction = selection.get("direction") or {}
    palette = direction.get("palette") or {}
    return f"""# Design Brain Module Selection

- Date/time: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}
- Task: {args.task}
- Template type: {args.template_type or 'Not specified'}
- Niche: {args.niche or 'Not specified'}
- Target buyer: {args.target_buyer or 'Not specified'}
- Visual mood: {args.visual_mood or 'Not specified'}
- Selected module: {selection['moduleId']}
- Seed pack: {selection.get('seedPack') or 'None'}
- Direction pack: {selection.get('directionPack') or 'None'}

## Product Types

{bullet(selection.get('productTypes', []))}

## Craft Modules

{bullet(selection.get('requiredCraft', []))}

## Seed Files

{bullet(selection.get('seedFiles', []))}

## Direction Rules

- Label: {direction.get('label', 'Not found')}
- Font pairing: {direction.get('fontPairing', 'Not specified')}
- Spacing posture: {direction.get('spacingPosture', 'Not specified')}
- Surface rules: {direction.get('surfaceRules', 'Not specified')}
- Motif budget: {direction.get('motifBudget', 'Not specified')}
- Imagery rules: {direction.get('imageryRules', 'Not specified')}
- Palette: {json.dumps(palette, ensure_ascii=False)}

## Validators

{bullet(selection.get('validators', []))}

## Source Files To Load

{bullet(selection.get('sourceFiles', []))}

## Source Inspiration

{bullet(selection.get('sourceInspiration', []))}
"""


def default_output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "context-packets" / f"{stamp}-{slugify(args.task)}-module-selection.md"


def main() -> int:
    args = parse_args()
    selection = build_selection(
        task=args.task,
        template_type=args.template_type,
        niche=args.niche,
        target_buyer=args.target_buyer,
        visual_mood=args.visual_mood,
    )
    if args.json:
        text = json.dumps(selection, indent=2, ensure_ascii=False)
    else:
        text = build_report(args, selection)
    if args.dry_run:
        print(text)
        return 0
    path = default_output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"Module selection written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
