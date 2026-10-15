#!/usr/bin/env python
"""Build product-purpose reference rotation groups for the local website corpus."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_website_reference_select import (
    DEFAULT_GROUP_SIZE,
    MIN_REFERENCE_GROUP_SIZE,
    candidates,
    format_path,
    reference_group_fingerprint,
    row_reference_id,
    select_references,
    select_source,
)
from design_brain_website_types import load_taxonomy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create website reference rotation groups per product family.")
    parser.add_argument("--source", default="Template Website", help="Reference corpus folder.")
    parser.add_argument("--group-size", type=int, default=DEFAULT_GROUP_SIZE, help="Preferred max references per group.")
    parser.add_argument("--min-group-size", type=int, default=MIN_REFERENCE_GROUP_SIZE, help="Minimum desired references per group when enough references exist.")
    parser.add_argument("--output", default=".design-brain/WEBSITE_REFERENCE_PRODUCT_GROUPS.json", help="Output JSON path.")
    parser.add_argument("--report-output", default="", help="Optional markdown report path.")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON without writing files.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def product_query(record: dict[str, Any]) -> str:
    return " ".join(
        [
            str(record.get("name", "")),
            str(record.get("id", "")),
            str(record.get("category", "")),
            " ".join(str(item) for item in record.get("routingTriggers", [])),
            " ".join(str(item) for item in record.get("requiredSignals", [])),
        ]
    )


def row_to_json(row: dict[str, Any], root: Path) -> dict[str, Any]:
    return {
        "path": format_path(row["path"], root),
        "referenceId": row_reference_id(row),
        "score": int(row.get("score", 0)),
        "reasons": row.get("reasons", []),
        "diversityTags": row.get("diversityTags", []),
    }


def group_to_json(group: list[dict[str, Any]], index: int, root: Path) -> dict[str, Any]:
    return {
        "groupIndex": index + 1,
        "groupSize": len(group),
        "groupFingerprint": reference_group_fingerprint(group),
        "references": [row_to_json(row, root) for row in group],
    }


def build_inventory(root: Path, source: Path, checked_sources: list[Path], group_size: int, min_group_size: int) -> dict[str, Any]:
    taxonomy = load_taxonomy(root)
    product_groups: list[dict[str, Any]] = []

    for record in taxonomy.get("productTypes", []):
        if not isinstance(record, dict):
            continue
        selection = select_references(
            source,
            record,
            product_query(record),
            9999,
            3,
            group_size,
            min_group_size,
        )
        groups = selection.get("referenceGroups", [])
        product_groups.append(
            {
                "productType": {
                    "id": record.get("id", ""),
                    "name": record.get("name", ""),
                    "category": record.get("category", ""),
                    "standardRange": record.get("standardRange", ""),
                },
                "counts": {
                    "broadMatches": selection.get("matchedCount", 0),
                    "dedupedMatches": selection.get("dedupedMatchedCount", 0),
                    "groupEligible": selection.get("groupEligibleCount", 0),
                    "supplementalForSmallPools": selection.get("groupSupplementalCount", 0),
                    "groupReady": selection.get("groupReadyCount", 0),
                    "referenceGroups": len(groups),
                },
                "rotation": {
                    "preferredGroupSize": group_size,
                    "minimumDesiredGroupSize": min_group_size,
                    "resetAfterGroup": len(groups),
                },
                "groups": [group_to_json(group, index, root) for index, group in enumerate(groups)],
            }
        )

    product_groups.sort(
        key=lambda item: (
            -int(item["counts"]["groupReady"]),
            -int(item["counts"]["broadMatches"]),
            str(item["productType"]["name"]),
        )
    )
    return {
        "generated": datetime.now().astimezone().isoformat(),
        "source": format_path(source, root),
        "checkedSources": [format_path(path, root) for path in checked_sources],
        "rawFiles": sum(1 for path in source.rglob("*") if path.is_file()) if source.exists() else 0,
        "selectorCandidates": len(candidates(source)),
        "preferredGroupSize": group_size,
        "minimumDesiredGroupSize": min_group_size,
        "products": product_groups,
    }


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Website Reference Product Groups",
        "",
        f"- Generated: {data['generated']}",
        f"- Source: `{data['source']}`",
        f"- Raw files: {data['rawFiles']}",
        f"- Selector candidates: {data['selectorCandidates']}",
        f"- Preferred group size: {data['preferredGroupSize']}",
        f"- Minimum desired group size: {data['minimumDesiredGroupSize']}",
        "",
        "## Product Summary",
        "",
        "| Product family | Broad | Eligible | Supplemental | Group-ready | Groups | Group sizes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for product in data["products"]:
        counts = product["counts"]
        group_sizes = ", ".join(str(group["groupSize"]) for group in product["groups"]) or "0"
        lines.append(
            f"| {product['productType']['name']} | {counts['broadMatches']} | {counts['groupEligible']} | "
            f"{counts['supplementalForSmallPools']} | {counts['groupReady']} | {counts['referenceGroups']} | {group_sizes} |"
        )

    lines.extend(["", "## Rotation Groups", ""])
    for product in data["products"]:
        lines.extend(
            [
                f"### {product['productType']['name']}",
                "",
                f"- Product ID: `{product['productType']['id']}`",
                f"- Groups: {product['counts']['referenceGroups']}",
                f"- Reset after group: {product['rotation']['resetAfterGroup']}",
                "",
            ]
        )
        if not product["groups"]:
            lines.append("- No safe product-purpose group available from current local references.")
            lines.append("")
            continue
        for group in product["groups"]:
            refs = "; ".join(ref["path"] for ref in group["references"])
            lines.append(f"- Group {group['groupIndex']} ({group['groupSize']} refs): `{group['groupFingerprint']}`")
            lines.append(f"  - {refs}")
        lines.append("")
    return "\n".join(lines)


def resolve_output(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def main() -> int:
    args = parse_args()
    root = repo_root()
    source, checked_sources = select_source(root, args.source)
    group_size = max(2, int(args.group_size or DEFAULT_GROUP_SIZE))
    min_group_size = max(1, int(args.min_group_size or MIN_REFERENCE_GROUP_SIZE))
    data = build_inventory(root, source, checked_sources, group_size, min_group_size)
    text = json.dumps(data, indent=2, ensure_ascii=False)

    if args.dry_run:
        print(text)
        return 0

    output = resolve_output(root, args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8", newline="\n")

    report_output = (
        resolve_output(root, args.report_output)
        if args.report_output
        else root / ".design-brain" / "reviews" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-website-reference-product-groups.md"
    )
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(build_report(data), encoding="utf-8", newline="\n")
    print(f"Website reference product groups written: {output}")
    print(f"Website reference product group report written: {report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
