#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Search - BM25 search engine for UI/UX style guides
Usage: python search.py "<query>" [--domain <domain>] [--stack <stack>] [--max-results 3]
       python search.py "<query>" --design-system [-p "Project Name"]
       python search.py "<query>" --design-system --persist [-p "Project Name"] [--page "dashboard"]

Domains: style, color, chart, landing, product, ux, typography, icons, react, web, typeui
Stacks: html-tailwind, react, nextjs

Persistence (Master + Overrides pattern):
  --persist    Save design system to design-system/MASTER.md
  --page       Also create a page-specific override file in design-system/pages/
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Allow both `python search.py ...` and `python -m ...` execution.
try:
    from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
    from design_system import generate_design_system, persist_design_system
except ImportError:  # pragma: no cover
    from .core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
    from .design_system import generate_design_system, persist_design_system

ROOT = Path(__file__).resolve().parents[1]
SAFETY_FILE = ROOT / "data" / "legacy_pattern_safety.json"

ACTION_RISK_TERMS = [
    "Contact Sales",
    "Contact Sales + Login",
    "logo carousel",
    "tab switching",
    "CTA Placement",
    "Conversion Strategy",
    "conversion funnel",
    "Bottom section",
    "86% higher engagement with video",
    "full website",
]


def _load_safety_metadata() -> dict:
    if not SAFETY_FILE.exists():
        return {}
    try:
        with SAFETY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _safety_meta_for_row(row: dict) -> dict:
    row_text = " ".join(str(value) for value in row.values()).lower()
    action_terms = [term for term in ACTION_RISK_TERMS if term.lower() in row_text]
    for name, meta in _load_safety_metadata().items():
        if name.lower() in row_text:
            return {
                "mode": "",
                "product_family": "",
                "safety_scope": meta.get("scope", "restricted"),
                "risk_level": meta.get("risk_level", "high"),
                "allowed_when": meta.get("allowed_when", []),
                "forbidden_when": meta.get("forbidden_when", []),
                "recommended_replacement": meta.get("recommended_replacement", meta.get("replacement_style", "")),
                "is_restricted": True,
                "brain_design_note": "Do not use as full template scaffold.",
                "offending_terms": [name] + [term for term in action_terms if term != name],
                "mode_compatibility": ["hero_header", "small_scope_landing", "explicit_reference_only"],
                "safety_metadata": {
                    "requires_sanitization": True,
                    "reason": "Restricted legacy pattern or raw landing payload should be sanitized before design-system output."
                },
                "action_model": {},
                "forbidden_payload_terms": action_terms,
                "sanitized_fields": [],
                "requires_sanitization": True,
            }
    requires_sanitization = bool(action_terms)
    return {
        "mode": "",
        "product_family": "",
        "safety_scope": "",
        "risk_level": "",
        "allowed_when": [],
        "forbidden_when": [],
        "recommended_replacement": "",
        "is_restricted": False,
        "brain_design_note": "",
        "offending_terms": action_terms,
        "mode_compatibility": [],
        "safety_metadata": {
            "requires_sanitization": requires_sanitization,
            "reason": "Raw action metadata is risky outside compatible modes." if requires_sanitization else ""
        },
        "action_model": {},
        "forbidden_payload_terms": action_terms,
        "sanitized_fields": [],
        "requires_sanitization": requires_sanitization,
    }


def _safety_note_for_row(row: dict) -> str:
    meta = _safety_meta_for_row(row)
    if not meta.get("is_restricted"):
        return ""
    return f"{meta.get('safety_scope', 'restricted')} / not recommended for full marketplace template"


def enrich_result_safety(result: dict) -> dict:
    enriched = dict(result)
    enriched_results = []
    for row in result.get("results", []):
        enriched_row = dict(row)
        enriched_row.update(_safety_meta_for_row(row))
        enriched_results.append(enriched_row)
    enriched["results"] = enriched_results
    return enriched


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    if result.get("stack"):
        output.append(f"## UI Pro Max Stack Guidelines")
        output.append(f"**Stack:** {result['stack']} | **Query:** {result['query']}")
    else:
        output.append(f"## UI Pro Max Search Results")
        output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

    for i, row in enumerate(result['results'], 1):
        output.append(f"### Result {i}")
        safety_note = _safety_note_for_row(row)
        if safety_note:
            output.append(f"- **Safety:** {safety_note}")
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > 300:
                value_str = value_str[:300] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI Pro Max Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--stack", "-s", choices=AVAILABLE_STACKS, help="Stack-specific search (html-tailwind, react, nextjs)")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    # Design system generation
    parser.add_argument("--design-system", "-ds", action="store_true", help="Generate complete design system recommendation")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for design system output")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="ascii", help="Output format for design system")
    # Persistence (Master + Overrides pattern)
    parser.add_argument("--persist", action="store_true", help="Save design system to design-system/MASTER.md (creates hierarchical structure)")
    parser.add_argument("--page", type=str, default=None, help="Create page-specific override file in design-system/pages/")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Output directory for persisted files (default: current directory)")
    parser.add_argument("--allow-failed-output", action="store_true", help="Debug only: print anti-scaffold failed output as unsafe")
    parser.add_argument("--allow-failed-persist", action="store_true", help="Debug only: allow persisting anti-scaffold failed output")

    args = parser.parse_args()

    # Design system takes priority
    if args.design_system:
        result = generate_design_system(
            args.query, 
            args.project_name, 
            args.format,
            persist=args.persist,
            page=args.page,
            output_dir=args.output_dir,
            allow_failed_output=args.allow_failed_output,
            allow_failed_persist=args.allow_failed_persist,
        )
        print(result)
        if "Output blocked: anti-scaffold gate failed." in result:
            raise SystemExit(1)
        
        # Print persistence confirmation
        if args.persist:
            project_slug = args.project_name.lower().replace(' ', '-') if args.project_name else "default"
            print("\n" + "=" * 60)
            print(f"OK: Design system persisted to design-system/{project_slug}/")
            print(f"   design-system/{project_slug}/MASTER.md (Global Source of Truth)")
            if args.page:
                page_filename = args.page.lower().replace(' ', '-')
                print(f"   design-system/{project_slug}/pages/{page_filename}.md (Page Overrides)")
            print("")
            print(f"Usage: When building a page, check design-system/{project_slug}/pages/[page].md first.")
            print(f"   If exists, its rules override MASTER.md. Otherwise, use MASTER.md.")
            print("=" * 60)
    # Stack search
    elif args.stack:
        result = search_stack(args.query, args.stack, args.max_results)
        if args.json:
            import json
            print(json.dumps(enrich_result_safety(result), indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
    # Domain search
    else:
        result = search(args.query, args.domain, args.max_results)
        if args.json:
            import json
            print(json.dumps(enrich_result_safety(result), indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
