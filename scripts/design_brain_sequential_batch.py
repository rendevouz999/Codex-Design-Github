#!/usr/bin/env python
"""Create a sequential reference-led batch plan for Design Brain.

The script is deterministic and dependency-free. It does not modify memory,
journals, preferences, or generated design files. It creates a working report
that forces batch template work to happen one template at a time.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path

from design_brain_website_reference_select import select_references
from design_brain_website_types import select_website_product_type


EXCLUDED_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".next",
    "dist",
    "build",
}

EXCLUDED_REFERENCE_KEYWORDS = (
    "documentation",
    "document",
    "font used",
    "font link",
    "fonts info",
    "link font",
    "license",
    "readme",
    "read me",
    "changelog",
    "how to",
    "support",
    "help",
    "info",
)

GENERIC_REFERENCE_NAMES = {
    "01 main files",
    "adobe xd",
    "ai",
    "buyer-file",
    "dist",
    "eps 10",
    "figma",
    "figma_file",
    "jpeg",
    "jpgs",
    "main",
    "main file",
    "main files",
    "main-file",
    "main-files",
    "mainfiles",
    "package",
    "photoshop",
    "png",
    "preview_images",
    "psd",
    "raw",
    "sketch",
    "svg",
    "xd",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a sequential reference-led batch workflow report."
    )
    parser.add_argument("--task", required=True, help="Natural-language design task.")
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of templates/items requested. Defaults to 1.",
    )
    parser.add_argument(
        "--reference-root",
        default="Template Website",
        help="Reference corpus folder. Relative paths resolve from the repo root.",
    )
    parser.add_argument(
        "--refs-per-cycle",
        type=int,
        default=10,
        help="Reference count per cycle. Use up to 10 product-purpose references. Defaults to 10.",
    )
    parser.add_argument("--output", default="", help="Optional markdown output path.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_reference_root(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def is_reference_candidate(path: Path) -> bool:
    if path.name in EXCLUDED_NAMES or path.name.startswith("."):
        return False
    lowered_name = path.name.lower()
    stem_name = path.stem.lower()
    if lowered_name in GENERIC_REFERENCE_NAMES or stem_name in GENERIC_REFERENCE_NAMES:
        return False
    if path.is_file() and re.fullmatch(r"\d+(\(\d+\))?", stem_name):
        return False
    if any(keyword in lowered_name for keyword in EXCLUDED_REFERENCE_KEYWORDS):
        return False
    if path.is_dir():
        return True
    return path.suffix.lower() in {
        ".html",
        ".htm",
        ".php",
        ".fig",
        ".sketch",
        ".xd",
        ".zip",
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".pdf",
    }


def reference_candidates(reference_root: Path) -> list[Path]:
    if not reference_root.exists():
        return []

    shallow = [
        path
        for path in reference_root.iterdir()
        if is_reference_candidate(path)
    ]
    if shallow:
        return dedupe_candidates(sorted(shallow, key=lambda path: path.name.lower()))

    recursive: list[Path] = []
    for path in reference_root.rglob("*"):
        if any(part in EXCLUDED_NAMES for part in path.parts):
            continue
        if is_reference_candidate(path):
            recursive.append(path)
    return dedupe_candidates(sorted(recursive, key=lambda path: str(path).lower()))


def canonical_reference_key(path: Path) -> str:
    name = path.stem if path.is_file() else path.name
    key = name.lower()
    key = key.replace("_", " ").replace("-", " ")
    key = re.sub(r"\s+", " ", key).strip()
    key = re.sub(r"\b(fig|sketch|xd|psd|jpg|jpeg|png|ai|eps|svg|file|files)\b", "", key)
    return re.sub(r"\s+", " ", key).strip() or path.name.lower()


def candidate_priority(path: Path) -> tuple[int, str]:
    if path.is_dir():
        return (0, path.name.lower())
    suffix_priority = {
        ".fig": 1,
        ".sketch": 2,
        ".xd": 3,
        ".html": 4,
        ".php": 5,
        ".jpg": 6,
        ".jpeg": 6,
        ".png": 7,
        ".webp": 8,
        ".psd": 9,
        ".zip": 10,
    }
    return (suffix_priority.get(path.suffix.lower(), 50), path.name.lower())


def dedupe_candidates(candidates: list[Path]) -> list[Path]:
    grouped: dict[str, Path] = {}
    for path in candidates:
        key = canonical_reference_key(path)
        current = grouped.get(key)
        if current is None or candidate_priority(path) < candidate_priority(current):
            grouped[key] = path
    return sorted(grouped.values(), key=lambda path: path.name.lower())


def stable_offset(task: str, candidate_count: int) -> int:
    if candidate_count <= 0:
        return 0
    digest = hashlib.sha1(task.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % candidate_count


def select_cycle_refs(
    candidates: list[Path],
    cycle_index: int,
    refs_per_cycle: int,
    task: str,
    use_stable_offset: bool = True,
) -> list[Path]:
    if not candidates:
        return []
    count = max(2, min(10, refs_per_cycle))
    offset = stable_offset(task, len(candidates)) if use_stable_offset else 0
    start = (offset + cycle_index * count) % len(candidates)
    return [candidates[(start + i) % len(candidates)] for i in range(min(count, len(candidates)))]


def slugify(text: str, limit: int = 72) -> str:
    chars: list[str] = []
    last_dash = False
    for char in text.lower():
        if char.isalnum():
            chars.append(char)
            last_dash = False
        elif not last_dash:
            chars.append("-")
            last_dash = True
    slug = "".join(chars).strip("-")
    return (slug[:limit].strip("-") or "sequential-batch")


def format_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def cycle_block(
    cycle_number: int,
    selected: list[Path],
    root: Path,
) -> list[str]:
    lines = [
        f"## Cycle {cycle_number}",
        "",
        "### Active Product-Purpose Reference Group",
        "",
    ]
    if selected:
        for index, path in enumerate(selected, start=1):
            lines.extend(
                [
                    f"{index}. `{format_path(path, root)}`",
                    "   - Why selected:",
                    "   - Inferred purpose:",
                    "   - Likely buyer:",
                    "   - Likely end audience:",
                    "   - Designer cognition evidence:",
                    "   - Structure insight:",
                    "   - Visual insight:",
                    "   - Do-not-copy boundary:",
                ]
            )
    else:
        lines.append("- No local references found. Ask for references or use another corpus.")

    lines.extend(
        [
            "",
            "### Hard-Gate Reminder",
            "",
            "- This cycle must follow `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`.",
            "- The output must be closer to this cycle's selected reference insight than to any accepted previous template.",
            "- Similarity root cause must be diagnosed before revision: structure, composition, effects, color-only, or copy/naming-only.",
            "- Structure similarity requires rebuild. Color-only similarity requires recolor. Copy-only similarity requires rewrite.",
            "- Effect/gradient/surface-depth judgment is automatic; do not wait for the user to ask for it.",
            "- Clean but flat, under-art-directed, or invisible-effect output fails this cycle.",
            "- If a cycle uses a Figma reference/link/source, complete the professional Figma template reading order and a Figma reference schema receipt before structure planning.",
            "- Unknown Figma product standard must be resolved through evidence, corpus/category lookup, or one targeted question; never through minimalist fallback.",
            "- Figma outputs require real auto-layout for editable structure and an auto-layout receipt.",
            "",
            "### Build One Template From This Cycle",
            "",
            "- New template concept:",
            "- Product type:",
            "- Niche:",
            "- Target buyer:",
            "- Marketplace category:",
            "- Buyer decision model:",
            "- Designer intent:",
            "- Attention strategy:",
            "- Emotional rhythm:",
            "- Trust strategy:",
            "- Density strategy:",
            "- Conversion / action logic:",
            "- Component reasoning:",
            "- Reusable thinking pattern:",
            "- Original execution plan:",
            "- Figma professional template reading and reference schema receipt when relevant: product purpose, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, Figma source hygiene, observed pages, frames, components, states, variants, design-system panels, standard inference, do-not-copy boundary, and reconstruction plan:",
            "- Standard/full structure map:",
            "- Visual system:",
            "- Effect language:",
            "- Gradient logic:",
            "- Surface-depth grammar:",
            "- Shadow/glow/blur/border/overlay rules:",
            "- Color-role system:",
            "- CTA behavior:",
            "- Focal-object emphasis:",
            "- Media placeholder treatment:",
            "- Editable modules:",
            "- Figma auto-layout plan: major auto-layout groups, responsive assumptions, and decorative absolute-position exceptions:",
            "- Image placeholder policy: use `image placeholder: [purpose]`; use `profile photo placeholder: [role]` for human/profile zones unless generated images were explicitly requested.",
            "- Difference from previous cycles:",
            "- Why this moves toward the selected references:",
            "",
            "### Pre-Build Structure Fingerprint",
            "",
            "- Opening strategy:",
            "- Hero grammar:",
            "- Navigation model:",
            "- Section order:",
            "- Mid-page cadence:",
            "- Dominant module types:",
            "- Proof/trust placement:",
            "- Conversion or CTA closure:",
            "- Footer closure:",
            "- Visual motif:",
            "- Effect language:",
            "- Gradient logic:",
            "- Surface-depth grammar:",
            "- Color-role system:",
            "- CTA behavior:",
            "- Media placeholder treatment:",
            "- Density rhythm:",
            "- Design-system panel logic:",
            "- Previous accepted template patterns this avoids:",
            "- Build may start: yes / no:",
            "",
            "### Visual-Language Fingerprint",
            "",
            "- Palette role map:",
            "- Gradient purpose and placement:",
            "- Semantic effects or deliberate restraint:",
            "- Surface-depth grammar:",
            "- Focal object / CTA emphasis:",
            "- Media placeholder treatment:",
            "- How this differs from all accepted previous templates:",
            "- Applied effect/gradient pass required before completion: yes / no / deliberate restraint with reason:",
            "",
            "### Single-Use Scaffold Before Build",
            "",
            "- Scaffold ID or working name:",
            "- Scaffold scope:",
            "- Hero grammar this scaffold controls:",
            "- Section sequence this scaffold controls:",
            "- Module/card/grid cadence this scaffold controls:",
            "- CTA/proof/footer closure this scaffold controls:",
            "- Design-system panel order this scaffold controls:",
            "- Temporary scaffold artifacts created:",
            "- Primitive helpers allowed to survive:",
            "- Explicit expiration point:",
            "",
            "### Pattern Lock After Build",
            "",
            "- Opening strategy used:",
            "- Hero grammar used:",
            "- Trust strategy used:",
            "- Density rhythm used:",
            "- Component system used:",
            "- CTA logic used:",
            "- Visual motif used:",
            "- Storytelling arc used:",
            "- Effect language used:",
            "- Gradient logic used:",
            "- Surface-depth grammar used:",
            "- Color-role system used:",
            "- CTA behavior used:",
            "- Media placeholder treatment used:",
            "- Figma auto-layout receipt used:",
            "- Design-system panel order used:",
            "- Design-system board built and visually checked:",
            "- Design-system receipt path:",
            "- Design-system check status:",
            "- Reference group used:",
            "- Must not repeat in later cycles:",
            "",
            "### Atomic Pair Completion Gate",
            "",
            "- Main template source built: yes / no",
            "- Design-system board/frame/source section built for this template: yes / no",
            "- Design-system board is physically separate or clearly named for this template: yes / no",
            "- Design-system coverage includes foundations, component anatomy, variants/states, section modules, usage logic, placeholder rules, and effect/surface tokens: yes / no",
            "- Design-system receipt exists and passes validation: yes / no",
            "- Template screenshot/render/visual inspection completed when possible: yes / no",
            "- Design-system board screenshot/render/visual inspection completed when possible: yes / no",
            "- Post-build audit for this template pair passes: yes / no",
            "- Fingerprint locked after design-system completion: yes / no",
            "- Next template may start: yes / no",
            "",
            "### Scaffold Disposal Receipt",
            "",
            "- Page-level scaffold used for this template:",
            "- Disposal status: permanently disposed from active context / not disposed:",
            "- Temporary scaffold files or scratch builders deleted:",
            "- Previous scaffold will not be reread, copied, mutated, or data-swapped:",
            "- Primitive helpers retained only:",
            "- Blank structure fingerprint prepared for next cycle:",
            "",
            "### Pairwise Similarity Audit",
            "",
            "| Compared against accepted template | Structure similarity | Composition similarity | Effect similarity | Gradient/surface similarity | Color similarity | CTA/media similarity | Copy/naming similarity | Root cause | Required action | Pass/fail |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            "|  |  |  |  |  |  |  |  |  |  |  |",
            "",
            "### Applied Effect / Gradient Review",
            "",
            "- Screenshot or render inspected:",
            "- Effects/gradients visible on focal modules:",
            "- Effects support hierarchy, mood, depth, proof, or conversion:",
            "- Effects are not copied from reference or previous batch item:",
            "- If restraint was chosen, hierarchy is carried by:",
            "- Required visual-language revision before next cycle:",
            "",
            "",
            "### Stop Gate Before Next Cycle",
            "",
            "- The current template is complete.",
            "- The current template's own design-system board is complete and checked.",
            "- Major cognition claims are backed by visible evidence and confidence levels.",
            "- The current template has been checked against selected references.",
            "- The current template stays below 10 percent similarity against accepted earlier fingerprints.",
            "- Similarity root cause has been diagnosed; structure defects were rebuilt, color-only defects were recolored, and copy-only defects were rewritten.",
            "- Effect/gradient/surface-depth quality was applied or deliberate restraint was evidenced.",
            "- Figma auto-layout receipt is complete when the output is Figma.",
            "- Design-system receipt/check is PASS before pattern lock.",
            "- The current template's scaffold disposal receipt is complete.",
            "- Only after this passes may Codex start the next cycle.",
            "",
        ]
    )
    return lines


def build_report(args: argparse.Namespace, root: Path) -> str:
    reference_root = resolve_reference_root(root, args.reference_root)
    raw_candidates = reference_candidates(reference_root)
    refs_per_cycle = max(2, min(10, args.refs_per_cycle))
    count = max(1, args.count)
    product_type = select_website_product_type(args.task, root)
    product_reference_selection = select_references(
        reference_root,
        product_type,
        args.task,
        max(count * refs_per_cycle * 3, refs_per_cycle),
        refs_per_cycle,
    )
    product_matched_candidates = [row["path"] for row in product_reference_selection.get("patternPool", [])]
    product_reference_groups = [
        [row["path"] for row in group]
        for group in product_reference_selection.get("referenceGroups", [])
    ]
    candidates = product_matched_candidates or raw_candidates

    lines = [
        "# Sequential Reference-Led Batch Plan",
        "",
        "## Task",
        "",
        args.task,
        "",
        "## Workflow Rule",
        "",
        "Build the batch one complete template pair at a time. For each template, select the next active product-purpose reference group with up to 10 eligible varied references when enough local matches exist, infer buyer decision model and evidence-backed designer cognition, extract structure and visual logic, build one complete template plus its own design-system board, validate and inspect that pair, lock the used pattern memory, permanently dispose of the spent scaffold from active context, then restart the cycle for the next template.",
        "",
        "## Inputs",
        "",
        f"- Template count: {count}",
        f"- References per cycle: {refs_per_cycle}",
        f"- Reference root: `{format_path(reference_root, root)}`",
        f"- Website product type: {product_type.get('name', 'Not classified')}",
        f"- Raw reference candidates found: {len(raw_candidates)}",
        f"- Product-type reference matches used: {len(product_matched_candidates)}",
        f"- Product-purpose reference groups found: {len(product_reference_groups)}",
        "",
        "## Source-Of-Truth Files To Load",
        "",
        "- `.design-brain/DESIGNER_COGNITION_LAYER.md`",
        "- `.design-brain/BATCH_TEMPLATE_HARD_GATES.md`",
        "- `.design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md`",
        "- `.design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md`",
        "- `.design-brain/FIGMA_REFERENCE_DEEP_STUDY.md` when any cycle uses a Figma reference/link/source",
        "- `.design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md` when any cycle uses a Figma reference/link/source",
        "- `.design-brain/FIGMA_REFERENCE_LEARNING_CORPUS.md` when using the user-provided Figma material links",
        "- `.design-brain/templates/FIGMA_REFERENCE_SCHEMA_RECEIPT.md` when any cycle uses a Figma reference/link/source",
        "- `.design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md` when any output is Figma",
        "- `.design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md`",
        "- `.design-brain/templates/SEQUENTIAL_REFERENCE_BATCH_CYCLE.md`",
        "- `.design-brain/AUTOLOAD_POLICY.md`",
        "- `.design-brain/CONTEXT_PRIORITY.md`",
        "- `.design-brain/REFERENCE_INSIGHT_SYSTEM.md`",
        "- `.design-brain/ORIGINALITY_GUARD.md`",
        "- `.design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md`",
        "- medium-specific seed pack or playbook for the requested platform",
        "",
        "## Product-Type Corpus Selection",
        "",
        "Use `scripts/design_brain_website_reference_select.py` to refresh or inspect the selected Pattern Learning Pool from `Template Website`.",
        "",
        "## What Codex Must Not Do",
        "",
        "- Do not create one global batch structure.",
        "- Do not study all references once and then generate many variants.",
        "- Do not reuse the same hero, section cadence, module grammar, or CTA/proof/pricing flow.",
        "- Do not reach 10 percent cross-template similarity against any accepted earlier template.",
        "- Do not repeat more than 10 percent of the previous cycle's recognizable opening strategy, hero grammar, trust strategy, density rhythm, component system, CTA logic, visual motif, and storytelling arc.",
        "- Do not repeat the same effect language, gradient logic, surface-depth grammar, CTA behavior, or media-placeholder treatment.",
        "- Do not wait for the user to request effects or gradients; infer the correct visual-language pass automatically.",
        "- Do not accept clean-but-flat output as complete when the product family benefits from visual depth or stronger art direction.",
        "- Do not treat color, niche, or copy changes as real diversity.",
        "- Do not recolor a structure defect.",
        "- Do not rebuild a strong structure when only the palette is too close; recolor and rerun the audit.",
        "- Do not let a template become closer to a previous Codex-built output than to its own selected references.",
        "- Do not generate final images for editable source templates unless the user explicitly asked for generated images.",
        "- Do not use a Figma reference as a flat mood board or default to minimalist without professional reading plus page/frame/component/state evidence.",
        "- Do not build Figma source templates primarily with manual x/y positioning or omit the auto-layout receipt.",
        "- Do not treat design systems as a final pack-level cleanup after all template pages are built.",
        "- Do not start the next template until the current template plus its own design-system board are complete and its pattern is locked.",
        "- Do not keep, reread, mutate, or data-swap a spent page-level scaffold after the current template is accepted.",
        "- Do not leave temporary scaffold files, scratch builders, page schemas, or data objects available as implementation source for the next template.",
        "",
    ]

    for cycle_index in range(count):
        if product_reference_groups:
            selected = product_reference_groups[cycle_index % len(product_reference_groups)]
        else:
            selected = select_cycle_refs(
                candidates,
                cycle_index,
                refs_per_cycle,
                args.task,
                use_stable_offset=not bool(product_matched_candidates),
            )
        lines.extend(cycle_block(cycle_index + 1, selected, root))

    lines.extend(
        [
            "## Final Batch Gate",
            "",
            "- Every template has its own reference study cycle.",
            "- Every template has its own inferred purpose and buyer.",
            "- Every template has its own complete design-system board/source section before the next template begins.",
            "- Every template has a visibly different structure and visual rhythm.",
            "- Every template has a distinct visual-language fingerprint.",
            "- Every template has an applied effect/gradient/surface-depth decision with screenshot or visual-inspection evidence when possible.",
            "- Every template has passed pairwise cross-template audit below 10 percent similarity.",
            "- Similarity root causes were diagnosed and fixed with the right action.",
            "- Previous cycle patterns are not reused as defaults.",
            "- The batch feels like a curated collection, not one template recolored several times.",
            "",
        ]
    )
    return "\n".join(lines)


def default_output_path(root: Path, task: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return root / ".design-brain" / "context-packets" / f"{stamp}-sequential-batch-{slugify(task)}.md"


def main() -> int:
    args = parse_args()
    root = repo_root()
    report = build_report(args, root)
    print(report)

    if args.dry_run:
        return 0

    output_path = Path(args.output).expanduser() if args.output else default_output_path(root, args.task)
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8", newline="\n")
    print(f"Saved sequential batch report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
