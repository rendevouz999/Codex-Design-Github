#!/usr/bin/env python
"""Lint generated design artifacts for generic AI patterns and handoff risks."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_AI_COLORS = {
    "#6366f1",
    "#4f46e5",
    "#4338ca",
    "#3730a3",
    "#8b5cf6",
    "#7c3aed",
    "#a855f7",
    "#06b6d4",
    "#ec4899",
}
FILLER_PATTERNS = (
    r"\blorem ipsum\b",
    r"\bfeature one\b",
    r"\bfeature two\b",
    r"\bfeature three\b",
    r"\bsection title\b",
    r"\bget started today\b",
)
FIGMA_AUTO_LAYOUT_TERMS = (
    "auto-layout",
    "auto layout",
    "layoutmode",
    "layout mode",
    "layout sizing",
    "layoutSizingHorizontal".lower(),
    "layoutSizingVertical".lower(),
    "auto-layout receipt",
    "auto layout receipt",
)
FIGMA_REFERENCE_SCHEMA_TERMS = (
    "figma reference schema receipt",
    "reference schema receipt",
    "figma schema receipt",
    "figma reference receipt",
    "schema receipt",
)
FIGMA_OBSERVED_SCHEME_TERMS = (
    "observed pages",
    "page/frame",
    "page map",
    "frame map",
    "component groups",
    "component sets",
    "variants",
    "states",
    "state map",
    "design-system panels",
    "design system panels",
    "node/frame",
)
FIGMA_STANDARD_INFERENCE_TERMS = (
    "product-family standard",
    "product family standard",
    "category standard",
    "marketplace standard",
    "standard inference",
    "normal standard",
    "section/page/screen",
    "page/screen/state",
    "standard structure",
)
FIGMA_PROFESSIONAL_READING_TERMS = (
    "product purpose",
    "niche",
    "visual direction",
    "section structure",
    "section map",
    "grid",
    "layout system",
    "typography hierarchy",
    "color-role",
    "color role",
    "image direction",
    "component style",
    "spacing rhythm",
    "visual signature",
    "visual uniqueness",
    "content logic",
    "responsive behavior",
    "figma source hygiene",
    "layer naming",
    "auto-layout",
    "default-template syndrome",
    "professional reading",
)
FIGMA_MINIMALIST_FALLBACK_TERMS = (
    "minimalist",
    "minimal",
    "simple",
    "basic",
    "thin",
    "5-section",
    "5 section",
    "five-section",
    "safe layout",
)
COMPETITIVE_UNDERBUILD_TERMS = (
    "minimalist",
    "minimal",
    "simple",
    "basic",
    "thin",
    "sparse",
    "safe",
    "safety",
    "fallback",
    "clean",
    "restrained",
)
FIGMA_EVIDENCE_TERMS = (
    "figma evidence",
    "observed",
    "metadata",
    "screenshot",
    "reference schema",
    "schema receipt",
    "category evidence",
    "corpus evidence",
    "standard inference",
)
FIGMA_INVALID_ALIGNMENT_ENUM_PATTERN = re.compile(
    r"\b(?:primaryaxisalignitems|counteraxisalignitems)\b\s*(?:=|:)\s*['\"]?end['\"]?",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint an artifact's text/CSS/HTML output.")
    parser.add_argument("--artifact", default="", help="Path to artifact text/HTML/CSS.")
    parser.add_argument("--artifact-text", default="", help="Inline artifact text.")
    parser.add_argument("--medium", default="", help="Optional medium label.")
    parser.add_argument("--output", default="", help="Optional report path.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_text(args: argparse.Namespace) -> tuple[str, str]:
    if args.artifact_text:
        return args.artifact_text, "inline"
    if args.artifact:
        path = Path(args.artifact).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.read_text(encoding="utf-8", errors="replace"), str(path.resolve())
    return "", "empty"


def add(findings: list[dict[str, str]], severity: str, area: str, message: str, fix: str) -> None:
    findings.append({"severity": severity, "area": area, "message": message, "requiredFix": fix})


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def strip_root_blocks(text: str) -> str:
    return re.sub(r":root\s*\{.*?\}", "", text, flags=re.IGNORECASE | re.DOTALL)


def lint_text(text: str, source: str, medium: str) -> dict[str, Any]:
    lowered = text.lower()
    findings: list[dict[str, str]] = []

    if not text.strip():
        add(
            findings,
            "FAIL",
            "input",
            "No artifact text was provided.",
            "Pass --artifact or --artifact-text so the artifact can be checked.",
        )

    colors = {match.lower() for match in re.findall(r"#[0-9a-fA-F]{3,8}\b", text)}
    default_hits = sorted(colors & DEFAULT_AI_COLORS)
    if default_hits:
        add(
            findings,
            "WARN",
            "default-palette",
            f"Default AI/Tailwind accent colors detected: {', '.join(default_hits)}.",
            "Replace with tokenized, medium-specific palette roles tied to the product direction.",
        )

    gradient_count = len(re.findall(r"linear-gradient|radial-gradient|conic-gradient", lowered))
    gradient_mood_hits = re.findall(r"\b(purple|indigo|violet|cyan|blue|pink)\b", lowered)
    if gradient_count and len(set(gradient_mood_hits)) >= 2:
        add(
            findings,
            "WARN",
            "gradient-genericness",
            "Gradient styling uses common purple/blue/cyan/pink vocabulary.",
            "Keep gradients purposeful, reduce hue pileups, and anchor color in the direction pack.",
        )

    for pattern in FILLER_PATTERNS:
        if re.search(pattern, lowered):
            add(
                findings,
                "FAIL",
                "filler-copy",
                f"Filler copy pattern detected: {pattern}.",
                "Replace generic placeholders with buyer-specific content and realistic labels.",
            )
            break

    invented_metric_hits = re.findall(r"\b(?:10x|99\.9%|3x|2x|100\+|500\+|1m\+)\b", text, re.IGNORECASE)
    if invented_metric_hits and not re.search(r"placeholder|example|sample|replace", lowered):
        add(
            findings,
            "WARN",
            "metrics",
            f"Unqualified metric claims detected: {', '.join(sorted(set(invented_metric_hits)))}.",
            "Mark metrics as placeholders or replace them with truthful buyer/category-specific data.",
        )

    source_template_like = any(token in (medium + " " + lowered) for token in ["template", "website", "landing", "figma"])
    figma_like = "figma" in (medium + " " + lowered)
    figma_reference_like = figma_like and bool(
        re.search(r"(figma\.com|\.fig\b|figma\s+(reference|referensi|link|frame|source)|reference\s+figma|referensi\s+figma)", lowered)
    )
    if figma_like and source_template_like and FIGMA_INVALID_ALIGNMENT_ENUM_PATTERN.search(lowered):
        add(
            findings,
            "FAIL",
            "figma-api-alignment-enum",
            "Figma artifact/code uses END for auto-layout alignment, but the Figma Plugin API requires MAX for end alignment.",
            "Replace END with MAX for primaryAxisAlignItems/counterAxisAlignItems before calling use_figma. Use MIN for start, CENTER for center, SPACE_BETWEEN only on the primary axis, and child sizing FILL for stretch behavior.",
        )
    if figma_like and source_template_like and not any(term in lowered for term in FIGMA_AUTO_LAYOUT_TERMS):
        add(
            findings,
            "FAIL",
            "figma-auto-layout-required",
            "Figma source-template artifact does not show auto-layout implementation or receipt language.",
            "Use real Figma auto-layout for editable sections, nav, cards, CTAs, repeated rows, forms, dashboards, and design-system panels; add an auto-layout receipt.",
        )
    if figma_like and source_template_like and re.search(
        r"\b(manual x/y|manual coordinate|manual positioning|absolute positioning as primary|freeform positioning|without auto-layout|without auto layout|no auto-layout|no auto layout)\b",
        lowered,
    ) and not re.search(r"\b(decorative exception|documented exception|overlay exception|auto-layout receipt|auto layout receipt)\b", lowered):
        add(
            findings,
            "FAIL",
            "figma-manual-layout-risk",
            "Figma artifact appears to rely on manual or absolute positioning without documented exceptions.",
            "Reserve absolute positioning for decorative backgrounds, overlays, mockup callouts, or preview-only effects; keep editable structure in auto-layout frames.",
        )
    if figma_reference_like and source_template_like:
        professional_reading_hits = sum(1 for term in FIGMA_PROFESSIONAL_READING_TERMS if term in lowered)
        if professional_reading_hits < 8:
            add(
                findings,
                "FAIL",
                "figma-professional-template-reading",
                f"Figma-reference-led artifact does not show enough professional template reading ({professional_reading_hits}/8 minimum signals found).",
                "Document product purpose/niche, visual direction, section structure, grid/layout, typography hierarchy, color roles, image direction, component style, spacing rhythm, visual signature, content logic, responsive behavior, and Figma source hygiene.",
            )
        if not has_any(lowered, FIGMA_REFERENCE_SCHEMA_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-schema-receipt",
                "Figma-reference-led artifact does not include a Figma reference schema receipt.",
                "Add a receipt naming file/page/node/frame scope, observed pages/frames/sections/components/states/variants, standard inference, do-not-copy boundary, and reconstruction plan.",
            )
        if not has_any(lowered, FIGMA_OBSERVED_SCHEME_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-observed-scheme",
                "Figma reference artifact does not show pages, frames, components, variants, states, or design-system panels were studied.",
                "Document the observed Figma scheme before claiming reference-led reconstruction.",
            )
        if not has_any(lowered, FIGMA_STANDARD_INFERENCE_TERMS):
            add(
                findings,
                "FAIL",
                "figma-reference-standard-inference",
                "Figma reference artifact does not infer the product-family or marketplace standard.",
                "Name the product family and normal section/page/screen/state depth before structure approval.",
            )
        if has_any(lowered, FIGMA_MINIMALIST_FALLBACK_TERMS) and not has_any(lowered, FIGMA_EVIDENCE_TERMS):
            add(
                findings,
                "FAIL",
                "figma-minimalist-fallback",
                "Artifact uses minimalist/simple/thin structure language around a Figma reference without evidence.",
                "Prove short scope from Figma evidence or revise with product-family standard depth.",
            )
    if source_template_like and re.search(
        r"\b(generated image|ai generated|ai-generated|generate image|generated photo|generated[-_][a-z0-9_-]*(?:image|photo|portrait|founder)?|stock photo|fake portrait)\b",
        lowered,
    ):
        add(
            findings,
            "FAIL",
            "source-template-image-generation",
            "Artifact appears to include generated/final imagery language for an editable source template.",
            "Use text clue placeholders instead: `image placeholder: [purpose]`, or `profile photo placeholder: [role]` for human/profile slots.",
        )

    if source_template_like and re.search(r"<img\b|background-image\s*:|url\(", lowered) and not re.search(
        r"image placeholder|profile photo placeholder|placeholder",
        lowered,
    ):
        add(
            findings,
            "WARN",
            "missing-source-image-placeholder",
            "Artifact uses image-like output without visible replacement clue text.",
            "For source templates, label image zones with clue text such as `image placeholder: hero product image`.",
        )

    outside_root = strip_root_blocks(text)
    outside_hex_count = len(re.findall(r"#[0-9a-fA-F]{3,8}\b", outside_root))
    if outside_hex_count > 8:
        add(
            findings,
            "WARN",
            "tokens",
            f"{outside_hex_count} raw hex values appear outside :root/token blocks.",
            "Move repeated colors into named tokens and use semantic roles instead of scattered raw values.",
        )

    accent_var_count = len(re.findall(r"var\(--accent", lowered))
    if accent_var_count > 6:
        add(
            findings,
            "WARN",
            "overused-accent",
            f"Accent variable appears {accent_var_count} times.",
            "Reduce accent dependency and add hierarchy through type, spacing, imagery, and semantic state colors.",
        )

    website_like = any(token in (medium + " " + lowered) for token in ["website", "landing", "dashboard", "html", "css"])
    section_counts = [int(match) for match in re.findall(r"\b([1-7])\s+(?:meaningful\s+)?(?:sections?|blocks?)\b", lowered)]
    if website_like and section_counts and has_any(lowered, COMPETITIVE_UNDERBUILD_TERMS):
        add(
            findings,
            "FAIL",
            "minimalist-under-8",
            f"Artifact combines minimalist/safe/simple/clean language with under-8 website structure ({min(section_counts)} sections/blocks found).",
            "Use at least 8 meaningful sections for standard website or landing-page templates. Under-8 structure is only for explicitly small-scope products, and minimalist language cannot be the justification.",
        )
    if website_like and "@media" not in lowered and "container-type" not in lowered:
        add(
            findings,
            "WARN",
            "responsive",
            "Artifact does not show explicit responsive CSS logic.",
            "Add breakpoint or container-query rules and check text overflow across mobile/desktop.",
        )

    if re.search(r"\b(card inside card|nested card|card-wrapper card)\b", lowered):
        add(
            findings,
            "WARN",
            "composition",
            "Nested-card language detected.",
            "Flatten page sections and reserve cards for repeated items, modals, or framed tools.",
        )

    fail_count = sum(1 for item in findings if item["severity"] == "FAIL")
    warn_count = sum(1 for item in findings if item["severity"] == "WARN")
    return {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "source": source,
        "medium": medium or "not specified",
        "verdict": "FAIL" if fail_count else "PASS",
        "failCount": fail_count,
        "warnCount": warn_count,
        "findings": findings,
    }


def markdown_report(result: dict[str, Any]) -> str:
    finding_lines = []
    for finding in result["findings"]:
        finding_lines.extend(
            [
                f"### {finding['severity']} - {finding['area']}",
                "",
                f"- Issue: {finding['message']}",
                f"- Required fix: {finding['requiredFix']}",
                "",
            ]
        )
    if not finding_lines:
        finding_lines = ["- No blocking artifact findings.", ""]
    return "\n".join(
        [
            "# Design Brain Artifact Lint",
            "",
            f"- Generated: {result['generatedAt']}",
            f"- Source: {result['source']}",
            f"- Medium: {result['medium']}",
            f"- Verdict: {result['verdict']}",
            f"- Failures: {result['failCount']}",
            f"- Warnings: {result['warnCount']}",
            "",
            "## Findings",
            "",
            *finding_lines,
        ]
    )


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "reviews" / f"{stamp}-artifact-lint.md"


def main() -> int:
    args = parse_args()
    text, source = load_text(args)
    result = lint_text(text, source, args.medium.lower())
    output = json.dumps(result, indent=2, ensure_ascii=False) if args.json else markdown_report(result)
    if args.dry_run:
        print(output)
        return 0
    path = output_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(output, encoding="utf-8", newline="\n")
    print(f"Artifact lint report written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
