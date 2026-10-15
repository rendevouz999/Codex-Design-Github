#!/usr/bin/env python
"""Select website template references from the local Template Website corpus."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from design_brain_website_types import (
    load_taxonomy,
    normalize,
    normalize_for_routing,
    phrase_in_text,
    select_website_product_type,
)
from design_brain_reference_usage_gate import (
    DEFAULT_REGISTRY_PATH,
    find_group,
    find_reference,
    group_is_used,
    group_key,
    load_registry,
    reference_single_used,
)


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
REFERENCE_EXTENSIONS = IMAGE_EXTENSIONS | {".fig"}
DEFAULT_CORPUS_FOLDERS = [
    "Template Website",
    "references/Template Website",
    "references/template-website",
    ".design-brain/reference-corpus/template-website",
    ".design-brain/evidence/fig-extracts",
]
DEFAULT_ROTATION_REGISTRY = ".design-brain/TEMPLATE_REFERENCE_GROUP_ROTATION_REGISTRY.json"
DEFAULT_PRODUCT_GROUPS = ".design-brain/WEBSITE_REFERENCE_PRODUCT_GROUPS.json"
DEFAULT_GROUP_SIZE = 10
MIN_REFERENCE_GROUP_SIZE = 4
EXCLUDED_NAME_PARTS = {
    "captcha",
    "card-",
    "contact - icon",
    "contact-shape",
    "icon -",
    "license",
    "readme",
    "font",
    "documentation",
    "changelog",
    "support",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select product-type-specific references from Template Website."
    )
    parser.add_argument("--task", required=True, help="Natural-language task.")
    parser.add_argument("--template-type", default="", help="Template/product type.")
    parser.add_argument("--niche", default="", help="Niche or category.")
    parser.add_argument("--target-buyer", default="", help="Target buyer.")
    parser.add_argument("--product-type-id", default="", help="Optional taxonomy product type id.")
    parser.add_argument(
        "--source",
        default="Template Website",
        help="Reference corpus folder. Relative paths resolve from the repo root.",
    )
    parser.add_argument("--limit", type=int, default=50, help="Visible Pattern Learning Pool result limit.")
    parser.add_argument("--execution-count", type=int, default=3, help="Legacy execution pool count, used only with --legacy-execution-pool.")
    parser.add_argument("--group-size", type=int, default=DEFAULT_GROUP_SIZE, help="Reference group size for the active local selector group.")
    parser.add_argument("--min-group-size", type=int, default=MIN_REFERENCE_GROUP_SIZE, help="Minimum desired references per rotation group when enough same-purpose references exist.")
    parser.add_argument("--legacy-execution-pool", action="store_true", help="Use the old 2-3 reference execution pool instead of 10-reference group rotation.")
    parser.add_argument("--rotation-registry", default="", help="Optional reference group rotation registry path.")
    parser.add_argument("--no-record-rotation", action="store_true", help="Do not write reference group usage to the rotation registry.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    parser.add_argument("--output", default="", help="Optional output markdown/json path.")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing.")
    parser.add_argument("--respect-reference-usage-registry", action="store_true", help="Select execution references through Brand & Reference Usage Memory.")
    parser.add_argument("--allow-pair-when-singles-exhausted", action="store_true", help="Escalate to an unused pair after all singles are used.")
    parser.add_argument("--allow-triple-when-pairs-exhausted", action="store_true", help="Escalate to an unused triple after all pairs are used.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rotation_registry_path(root: Path, value: str = "") -> Path:
    if value:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = root / path
        return path.resolve()
    return (root / DEFAULT_ROTATION_REGISTRY).resolve()


def product_groups_path(root: Path) -> Path:
    return (root / DEFAULT_PRODUCT_GROUPS).resolve()


def resolve_source(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def source_candidates(root: Path, value: str) -> list[Path]:
    paths = [resolve_source(root, value)]
    if normalize(value) == "template website" or not paths[0].exists():
        paths.extend(resolve_source(root, item) for item in DEFAULT_CORPUS_FOLDERS)

    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path).lower()
        if key in seen:
            continue
        result.append(path)
        seen.add(key)
    return result


def select_source(root: Path, value: str) -> tuple[Path, list[Path]]:
    checked = source_candidates(root, value)
    for path in checked:
        if candidates(path):
            return path, checked
    for path in checked:
        if path.exists():
            return path, checked
    return checked[0], checked


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-") or "website-reference-select"


def file_text(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"[-_]+", " ", stem)
    stem = re.sub(r"\s+", " ", stem)
    return normalize(stem)


def is_candidate(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() not in REFERENCE_EXTENSIONS:
        return False
    name = path.name.lower()
    if any(part in name for part in EXCLUDED_NAME_PARTS):
        return False
    if re.fullmatch(r"\d+(\(\d+\))?", path.stem.lower()):
        return False
    return True


def candidates(source: Path) -> list[Path]:
    if not source.exists():
        return []
    return sorted(
        [path for path in source.rglob("*") if is_candidate(path)],
        key=lambda path: path.name.lower(),
    )


STOP_WORDS = {
    "buat",
    "bikin",
    "create",
    "desain",
    "design",
    "template",
    "website",
    "web",
    "figma",
    "page",
    "with",
    "from",
    "untuk",
    "yang",
    "dan",
    "dengan",
    "dari",
    "ke",
    "di",
    "ini",
    "itu",
    "seperti",
    "mirip",
    "referensi",
    "jangan",
    "bukan",
    "cukup",
    "bagian",
    "gambar",
    "halaman",
    "for",
    "the",
    "and",
    "new",
    "product",
}

SPECIAL_SHORT_WORDS = {"ai", "ui", "ux", "3d", "ar", "vr"}

SPECIFIC_QUERY_TERMS = {
    "agency",
    "agensi",
    "ai",
    "alat",
    "admin",
    "app",
    "blog",
    "booking",
    "cafe",
    "course",
    "dashboard",
    "ecommerce",
    "event",
    "fashion",
    "finance",
    "financial",
    "finansial",
    "fintech",
    "furniture",
    "furnitur",
    "hotel",
    "kafe",
    "kasir",
    "keuangan",
    "konsultan",
    "consultant",
    "consulting",
    "klinik",
    "kursus",
    "marketplace",
    "perhiasan",
    "platform",
    "portfolio",
    "portofolio",
    "pos",
    "properti",
    "rental",
    "restoran",
    "restaurant",
    "saas",
    "sekolah",
    "sewa",
    "shop",
    "software",
    "startup",
    "store",
    "storefront",
    "studio",
    "tech",
    "toko",
    "travel",
    "agency",
    "case",
    "study",
}

GENERIC_PRODUCT_TRIGGERS = {
    "app website",
    "platform website",
    "product website",
    "tech product",
}

GENERIC_SIGNALS = {"hero", "product", "feature", "footer", "contact", "page map"}
MIN_GROUP_ELIGIBLE_SCORE = 24


def words(value: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", normalize(value))
        if (len(word) >= 4 or word in SPECIAL_SHORT_WORDS) and word not in STOP_WORDS
    }


def canonical_reference_key(path: Path) -> str:
    raw = path.stem
    parts = [part.strip() for part in raw.split(" - ") if part.strip()]
    if len(parts) >= 3:
        title_parts = [
            part
            for part in parts[1:-1]
            if not re.fullmatch(r"[a-fA-F0-9]{8,}", part.strip())
        ]
        raw = " ".join(title_parts) or raw
    text = normalize(re.sub(r"[-_]+", " ", raw))
    text = re.sub(r"\b20\d{2}\b|\b\d{2}\b|\butc\b|\bimage\b", " ", text)
    text = re.sub(r"\b[a-z]\b", " ", text)
    text = re.sub(r"\b([a-f0-9]{8,})\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or path.name.lower()


def reference_diversity_tags(path: Path) -> list[str]:
    text = canonical_reference_key(path)
    tags: list[str] = []
    tag_patterns = [
        ("saas", r"\bsaas\b"),
        ("ai-platform", r"\b(platform|assistant|generate|tool|meeting)\b"),
        ("startup", r"\b(startup|startups|innovation)\b"),
        ("machine-learning", r"\b(machine learning|learning|neural)\b"),
        ("data-intelligence", r"\b(data|intelligence|search|analytics|analysis)\b"),
        ("cyber-security", r"\b(cyber|security|defense)\b"),
        ("robotics-integration", r"\b(robot|robotics|integration)\b"),
        ("business-management", r"\b(business|management|operations|workflow)\b"),
        ("technology", r"\b(tech|technology|software|solution|it)\b"),
        ("agency-creative", r"\b(agency|creative|studio|nft|digital)\b"),
        ("product-device", r"\b(product|gadget|laptop|phone|automotive)\b"),
        ("finance-blockchain", r"\b(finance|fintech|bank|crypto|blockchain)\b"),
        ("healthcare", r"\b(health|medical|clinic|healthcare)\b"),
    ]
    for tag, pattern in tag_patterns:
        if re.search(pattern, text):
            tags.append(tag)
    return tags or ["general"]


def primary_diversity_tag(path: Path) -> str:
    return reference_diversity_tags(path)[0]


def registry_reference_id(path: Path) -> str:
    return slugify(canonical_reference_key(path))


def row_reference_id(row: dict[str, Any]) -> str:
    return registry_reference_id(row["path"])


def row_group_key(rows: list[dict[str, Any]]) -> str:
    return group_key([row_reference_id(row) for row in rows])


def reference_group_fingerprint(rows: list[dict[str, Any]]) -> str:
    return row_group_key(rows)


def row_is_single_used(row: dict[str, Any], registry: dict[str, Any]) -> bool:
    ref_id = row_reference_id(row)
    if find_reference(registry, ref_id):
        return reference_single_used(registry, ref_id)
    canonical_name = canonical_reference_key(row["path"])
    for reference in registry.get("references", []):
        if normalize(str(reference.get("referenceBrandName", ""))) == normalize(canonical_name):
            return reference_single_used(registry, str(reference.get("referenceId", "")))
    return False


def apply_reference_usage_memory(
    selection: dict[str, Any],
    *,
    allow_pair: bool,
    allow_triple: bool,
) -> dict[str, Any]:
    registry = load_registry(DEFAULT_REGISTRY_PATH)
    pool = selection["patternPool"]
    rejected: list[dict[str, Any]] = []
    available_singles: list[dict[str, Any]] = []
    for row in pool:
        if row_is_single_used(row, registry):
            rejected.append(
                {
                    "path": row["path"],
                    "referenceId": row_reference_id(row),
                    "reason": "single reference already used",
                }
            )
        else:
            available_singles.append(row)

    if available_singles:
        selection["executionPool"] = available_singles[:1]
        selection["referenceUsageMode"] = "single"
        selection["referenceGroupKey"] = row_group_key(selection["executionPool"])
        selection["memoryGateStatus"] = "PASS"
        selection["nextReferenceUsageAction"] = "Use the next unused single reference before escalating."
    else:
        selection["executionPool"] = []
        selection["referenceUsageMode"] = ""
        selection["referenceGroupKey"] = ""
        selection["memoryGateStatus"] = "BLOCKED_REFERENCE_STOCK_EXHAUSTED"
        selection["nextReferenceUsageAction"] = "Add new references or enable pair/triple escalation."

    if not available_singles and allow_pair:
        for pair in itertools.combinations(pool, 2):
            key = row_group_key(list(pair))
            if not group_is_used(find_group(registry, key)):
                selection["executionPool"] = list(pair)
                selection["referenceUsageMode"] = "pair"
                selection["referenceGroupKey"] = key
                selection["memoryGateStatus"] = "PASS"
                selection["nextReferenceUsageAction"] = "Singles are exhausted; use this unused reference pair."
                break
        else:
            selection["memoryGateStatus"] = "BLOCKED_REFERENCE_STOCK_EXHAUSTED"
            selection["nextReferenceUsageAction"] = "No unused pair remains; enable triple escalation or add new references."

    if not selection["executionPool"] and allow_pair and allow_triple:
        for trio in itertools.combinations(pool, 3):
            key = row_group_key(list(trio))
            if not group_is_used(find_group(registry, key)):
                selection["executionPool"] = list(trio)
                selection["referenceUsageMode"] = "triple"
                selection["referenceGroupKey"] = key
                selection["memoryGateStatus"] = "PASS"
                selection["nextReferenceUsageAction"] = "Singles and pairs are exhausted; use this unused triple."
                break

    selection["rejectedDueToReferenceMemory"] = rejected
    return selection


def filter_reference_usage_memory(selection: dict[str, Any]) -> dict[str, Any]:
    registry = load_registry(DEFAULT_REGISTRY_PATH)
    rejected: list[dict[str, Any]] = []
    available: list[dict[str, Any]] = []
    for row in selection.get("allMatchedReferences", []):
        if row_is_single_used(row, registry):
            rejected.append(
                {
                    "path": row["path"],
                    "referenceId": row_reference_id(row),
                    "reason": "single reference already used",
                }
            )
        else:
            available.append(row)
    available_ids = {row_reference_id(row) for row in available}
    eligible_available = [
        row
        for row in selection.get("groupEligibleReferences", available)
        if row_reference_id(row) in available_ids
    ]
    supplemental_available = [
        row
        for row in selection.get("groupSupplementalReferences", [])
        if row_reference_id(row) in available_ids
    ]
    group_ready_available = eligible_available + [
        row for row in supplemental_available if row_reference_id(row) not in {row_reference_id(item) for item in eligible_available}
    ]
    selection["allMatchedReferences"] = available
    selection["patternPool"] = available[: max(1, int(selection.get("visiblePatternLimit", 50)))]
    selection["groupEligibleReferences"] = eligible_available
    selection["groupEligibleCount"] = len(eligible_available)
    selection["groupSupplementalReferences"] = supplemental_available
    selection["groupSupplementalCount"] = len(supplemental_available)
    selection["groupReadyReferences"] = group_ready_available
    selection["groupReadyCount"] = len(group_ready_available)
    selection["referenceGroups"] = build_reference_groups(
        group_ready_available,
        int(selection.get("groupSize", DEFAULT_GROUP_SIZE)),
        int(selection.get("minGroupSize", MIN_REFERENCE_GROUP_SIZE)),
    )
    selection["rejectedDueToReferenceMemory"] = rejected
    selection["memoryGateStatus"] = "PASS" if available else "BLOCKED_REFERENCE_STOCK_EXHAUSTED"
    selection["nextReferenceUsageAction"] = (
        "Used references were filtered before group rotation."
        if available
        else "No unused references remain for this product-purpose pool."
    )
    return selection


def product_record_by_id(root: Path, product_type_id: str) -> dict[str, Any]:
    if not product_type_id:
        return {}
    taxonomy = load_taxonomy(root)
    for record in taxonomy.get("productTypes", []):
        if isinstance(record, dict) and record.get("id") == product_type_id:
            return record
    return {}


def score_candidate(path: Path, record: dict[str, Any], query: str) -> tuple[int, list[str]]:
    text = file_text(path)
    score = 0
    semantic_score = 0
    reasons: list[str] = []
    query_words = words(normalize_for_routing(query))
    name_words = words(text)
    focus_words = query_words & SPECIFIC_QUERY_TERMS
    focus_overlap = sorted(focus_words & name_words)

    for trigger in record.get("routingTriggers", []):
        phrase = normalize(str(trigger))
        if phrase_in_text(phrase, text):
            is_generic = phrase in GENERIC_PRODUCT_TRIGGERS
            if is_generic and focus_words and not focus_overlap:
                value = 5
            else:
                value = 18 + min(len(phrase.split()), 4)
            score += value
            semantic_score += value
            reasons.append(f"product trigger: {trigger}")

    for signal in record.get("requiredSignals", []):
        phrase = normalize(str(signal))
        if phrase_in_text(phrase, text):
            value = 2 if phrase in GENERIC_SIGNALS and focus_words and not focus_overlap else 8
            score += value
            semantic_score += value
            reasons.append(f"signal: {signal}")

    for page in record.get("requiredPagesOrScreens", []):
        phrase = normalize(str(page))
        if phrase_in_text(phrase, text):
            score += 5
            semantic_score += 5
            reasons.append(f"page/flow: {page}")

    overlap = sorted(query_words & name_words)
    if overlap:
        value = min((len(overlap) * 4) + (len(focus_overlap) * 8), 36)
        score += value
        semantic_score += value
        reasons.append("query terms: " + ", ".join(overlap[:6]))

    if semantic_score > 0 and path.suffix.lower() in IMAGE_EXTENSIONS:
        score += 3
    if semantic_score > 0 and re.search(r"\b(home|homepage|landing|website|template)\b", text):
        score += 2

    return score, reasons


def product_purpose_group_eligible(row: dict[str, Any], query: str) -> bool:
    reasons = [str(reason).lower() for reason in row.get("reasons", [])]
    if not reasons:
        return False

    score = int(row.get("score", 0))
    tags = set(row.get("diversityTags", reference_diversity_tags(row["path"]))) - {"general"}
    text_words = words(file_text(row["path"]))
    query_focus = words(normalize_for_routing(query)) & SPECIFIC_QUERY_TERMS
    focus_overlap = bool(query_focus & text_words)
    has_product_trigger = any(reason.startswith("product trigger:") for reason in reasons)
    has_query_terms = any(reason.startswith("query terms:") for reason in reasons)
    weak_only = all(reason.startswith(("signal:", "page/flow:")) for reason in reasons)

    if weak_only:
        return False
    if has_product_trigger and focus_overlap:
        return True
    if has_product_trigger and has_query_terms and score >= MIN_GROUP_ELIGIBLE_SCORE:
        return True
    if has_product_trigger and tags and score >= MIN_GROUP_ELIGIBLE_SCORE:
        return True
    if has_query_terms and tags and score >= MIN_GROUP_ELIGIBLE_SCORE:
        return True
    return False


def product_purpose_support_eligible(row: dict[str, Any], query: str) -> bool:
    reasons = [str(reason).lower() for reason in row.get("reasons", [])]
    if not reasons:
        return False

    score = int(row.get("score", 0))
    tags = set(row.get("diversityTags", reference_diversity_tags(row["path"]))) - {"general"}
    text_words = words(file_text(row["path"]))
    query_focus = words(normalize_for_routing(query)) & SPECIFIC_QUERY_TERMS
    focus_overlap = bool(query_focus & text_words)
    has_product_trigger = any(reason.startswith("product trigger:") for reason in reasons)
    has_query_terms = any(reason.startswith("query terms:") for reason in reasons)
    weak_only = all(reason.startswith(("signal:", "page/flow:")) for reason in reasons)

    if weak_only:
        return False
    if has_product_trigger and (focus_overlap or tags or score >= 12):
        return True
    if has_query_terms and tags and score >= 12:
        return True
    return False


def group_eligible_references(rows: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    return [row for row in rows if product_purpose_group_eligible(row, query)]


def group_ready_references(
    rows: list[dict[str, Any]],
    query: str,
    min_group_size: int = MIN_REFERENCE_GROUP_SIZE,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible = group_eligible_references(rows, query)
    if len(eligible) >= min_group_size:
        return eligible, []

    seen = {row_reference_id(row) for row in eligible}
    supplements: list[dict[str, Any]] = []
    for row in rows:
        if row_reference_id(row) in seen:
            continue
        if not product_purpose_support_eligible(row, query):
            continue
        supplements.append(row)
        seen.add(row_reference_id(row))
        if len(eligible) + len(supplements) >= min_group_size:
            break
    if len(eligible) + len(supplements) < min_group_size:
        return [], supplements
    return eligible + supplements, supplements


def group_size_targets(total: int, preferred_size: int = DEFAULT_GROUP_SIZE, min_group_size: int = MIN_REFERENCE_GROUP_SIZE) -> list[int]:
    if total <= 0:
        return []
    preferred = max(min_group_size, preferred_size)
    minimum = max(1, min_group_size)
    if total <= preferred:
        return [total]

    group_count = (total + preferred - 1) // preferred
    while group_count > 1 and total // group_count < minimum:
        group_count -= 1

    base = total // group_count
    remainder = total % group_count
    return [base + (1 if index < remainder else 0) for index in range(group_count)]


def build_reference_groups(
    rows: list[dict[str, Any]],
    group_size: int = DEFAULT_GROUP_SIZE,
    min_group_size: int = MIN_REFERENCE_GROUP_SIZE,
) -> list[list[dict[str, Any]]]:
    targets = group_size_targets(len(rows), group_size, min_group_size)
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        tag = primary_diversity_tag(row["path"])
        buckets.setdefault(tag, []).append(row)

    for bucket in buckets.values():
        bucket.sort(key=lambda row: (-int(row["score"]), str(row["path"]).lower()))

    groups: list[list[dict[str, Any]]] = []
    for target_size in targets:
        group: list[dict[str, Any]] = []
        used_tags: set[str] = set()
        while len(group) < target_size and any(buckets.values()):
            available_tags = [tag for tag, bucket in buckets.items() if bucket]
            unused_tags = [tag for tag in available_tags if tag not in used_tags]
            candidate_tags = unused_tags or available_tags
            candidate_tags.sort(
                key=lambda tag: (
                    -int(buckets[tag][0]["score"]),
                    len(buckets[tag]),
                    tag,
                )
            )
            tag = candidate_tags[0]
            row = buckets[tag].pop(0)
            row = dict(row)
            row["diversityTags"] = reference_diversity_tags(row["path"])
            group.append(row)
            used_tags.add(tag)
        if group:
            groups.append(group)
    return groups


def purpose_key(record: dict[str, Any], query: str, source: Path, root: Path) -> str:
    query_words = words(normalize_for_routing(query))
    focus = sorted(query_words & SPECIFIC_QUERY_TERMS)
    product_id = str(record.get("id") or "website-template")
    try:
        source_key = str(source.relative_to(root))
    except ValueError:
        source_key = str(source)
    source_slug = slugify(source_key)
    focus_slug = "-".join(focus[:10]) or "general"
    return slugify(f"{source_slug}--{product_id}--{focus_slug}")[:160]


def load_rotation_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": "1.0", "purposes": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": "1.0", "purposes": {}}
    if not isinstance(payload, dict):
        return {"version": "1.0", "purposes": {}}
    payload.setdefault("version", "1.0")
    payload.setdefault("purposes", {})
    return payload


def save_rotation_registry(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def load_precomputed_product_groups(root: Path, record: dict[str, Any]) -> list[list[dict[str, Any]]]:
    path = product_groups_path(root)
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

    product_id = str(record.get("id") or "")
    for product in payload.get("products", []):
        if str(product.get("productType", {}).get("id", "")) != product_id:
            continue
        groups: list[list[dict[str, Any]]] = []
        for group in product.get("groups", []):
            rows: list[dict[str, Any]] = []
            for ref in group.get("references", []):
                ref_path = root / str(ref.get("path", ""))
                if not ref_path.exists():
                    continue
                rows.append(
                    {
                        "path": ref_path,
                        "score": int(ref.get("score", 0)),
                        "reasons": list(ref.get("reasons", [])),
                        "diversityTags": list(ref.get("diversityTags", [])),
                    }
                )
            if rows:
                groups.append(rows)
        return groups
    return []


def apply_precomputed_product_groups(selection: dict[str, Any], root: Path, record: dict[str, Any]) -> dict[str, Any]:
    if selection.get("referenceGroups"):
        selection["groupSource"] = selection.get("groupSource", "dynamic-selector")
        return selection

    groups = load_precomputed_product_groups(root, record)
    if not groups:
        selection["groupSource"] = "dynamic-selector-empty"
        return selection

    ready_count = sum(len(group) for group in groups)
    selection["referenceGroups"] = groups
    selection["groupReadyReferences"] = [row for group in groups for row in group]
    selection["groupReadyCount"] = ready_count
    selection["groupSource"] = "precomputed-product-family-groups"
    selection["nextReferenceUsageAction"] = (
        "Runtime query had no safe active group, so selector used the precomputed product-family group inventory."
    )
    return selection


def apply_group_rotation(
    selection: dict[str, Any],
    *,
    root: Path,
    source: Path,
    record: dict[str, Any],
    query: str,
    registry_path: Path,
    should_record: bool,
) -> dict[str, Any]:
    groups = selection.get("referenceGroups", [])
    key = purpose_key(record, query, source, root)
    selection["rotationPurposeKey"] = key
    selection["rotationRegistryPath"] = str(registry_path)
    selection["rotationRecorded"] = False
    selection["rotationWouldRecord"] = bool(should_record)

    if not groups:
        selection["executionPool"] = []
        selection["activeReferenceGroup"] = {}
        selection["rotationStatus"] = "NO_GROUPS"
        return selection

    registry = load_rotation_registry(registry_path)
    purposes = registry.setdefault("purposes", {})
    state = purposes.get(key, {})
    previous_index = int(state.get("lastGroupIndex", -1)) if isinstance(state, dict) else -1
    group_count = len(groups)
    active_index = (previous_index + 1) % group_count
    active_group = groups[active_index]
    selection["executionPool"] = active_group
    selection["activeReferenceGroup"] = {
        "purposeKey": key,
        "groupIndex": active_index + 1,
        "groupCount": group_count,
        "groupSize": len(active_group),
        "groupFingerprint": reference_group_fingerprint(active_group),
        "resetAfterGroup": group_count,
        "nextGroupIndex": ((active_index + 1) % group_count) + 1,
    }
    selection["rotationStatus"] = "PASS"

    if should_record:
        history = list(state.get("history", [])) if isinstance(state, dict) else []
        history.append(
            {
                "usedAt": datetime.now().astimezone().isoformat(),
                "groupIndex": active_index + 1,
                "groupCount": group_count,
                "groupFingerprint": reference_group_fingerprint(active_group),
                "references": [format_path(row["path"], root) for row in active_group],
            }
        )
        purposes[key] = {
            "productTypeId": record.get("id", ""),
            "productTypeName": record.get("name", ""),
            "source": format_path(source, root),
            "querySignature": " ".join(sorted(words(query)))[:240],
            "lastGroupIndex": active_index,
            "lastGroupFingerprint": reference_group_fingerprint(active_group),
            "groupCount": group_count,
            "groupSize": len(active_group),
            "useCount": int(state.get("useCount", 0)) + 1 if isinstance(state, dict) else 1,
            "updatedAt": datetime.now().astimezone().isoformat(),
            "history": history[-50:],
        }
        registry["updatedAt"] = datetime.now().astimezone().isoformat()
        save_rotation_registry(registry_path, registry)
        selection["rotationRecorded"] = True

    return selection


def select_references(
    source: Path,
    record: dict[str, Any],
    query: str,
    limit: int,
    execution_count: int,
    group_size: int = DEFAULT_GROUP_SIZE,
    min_group_size: int = MIN_REFERENCE_GROUP_SIZE,
) -> dict[str, Any]:
    rows = []
    for path in candidates(source):
        score, reasons = score_candidate(path, record, query)
        if score > 0 and reasons:
            rows.append(
                {
                    "path": path,
                    "score": score,
                    "reasons": reasons,
                }
            )

    rows.sort(key=lambda row: (-int(row["score"]), str(row["path"]).lower()))
    deduped: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for row in rows:
        key = canonical_reference_key(row["path"])
        if key in seen_keys:
            continue
        row = dict(row)
        row["diversityTags"] = reference_diversity_tags(row["path"])
        deduped.append(row)
        seen_keys.add(key)

    pattern_pool = deduped[: max(1, limit)]
    strict_group_pool = group_eligible_references(deduped, query)
    group_pool, supplemental_pool = group_ready_references(deduped, query, min_group_size)

    count = max(2, min(3, execution_count))
    execution_pool = pattern_pool[: min(count, len(pattern_pool))]
    reference_groups = build_reference_groups(group_pool, group_size, min_group_size)

    return {
        "allMatchedReferences": deduped,
        "patternPool": pattern_pool,
        "executionPool": execution_pool,
        "groupEligibleReferences": strict_group_pool,
        "groupSupplementalReferences": supplemental_pool,
        "groupReadyReferences": group_pool,
        "referenceGroups": reference_groups,
        "candidateCount": len(candidates(source)),
        "matchedCount": len(rows),
        "dedupedMatchedCount": len(deduped),
        "groupEligibleCount": len(strict_group_pool),
        "groupSupplementalCount": len(supplemental_pool),
        "groupReadyCount": len(group_pool),
        "visiblePatternLimit": limit,
        "groupSize": group_size,
        "minGroupSize": min_group_size,
    }


def format_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def serializable(selection: dict[str, Any], root: Path, source: Path, record: dict[str, Any]) -> dict[str, Any]:
    def row_to_json(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "path": format_path(row["path"], root),
            "referenceId": row_reference_id(row),
            "score": row["score"],
            "reasons": row["reasons"],
            "diversityTags": row.get("diversityTags", reference_diversity_tags(row["path"])),
        }
    def group_to_json(index: int, group: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "groupIndex": index + 1,
            "groupSize": len(group),
            "groupFingerprint": reference_group_fingerprint(group),
            "references": [row_to_json(row) for row in group],
        }

    return {
        "generated": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "source": format_path(source, root),
        "checkedSources": [format_path(path, root) for path in selection.get("checkedSources", [])],
        "corpusWarning": selection.get("corpusWarning", ""),
        "productType": {
            "id": record.get("id", ""),
            "name": record.get("name", ""),
            "standardRange": record.get("standardRange", ""),
        },
        "candidateCount": selection["candidateCount"],
        "matchedCount": selection["matchedCount"],
        "dedupedMatchedCount": selection.get("dedupedMatchedCount", selection["matchedCount"]),
        "groupEligibleCount": selection.get("groupEligibleCount", 0),
        "groupSupplementalCount": selection.get("groupSupplementalCount", 0),
        "groupReadyCount": selection.get("groupReadyCount", selection.get("groupEligibleCount", 0)),
        "groupSource": selection.get("groupSource", "dynamic-selector"),
        "groupSize": selection.get("groupSize", DEFAULT_GROUP_SIZE),
        "minGroupSize": selection.get("minGroupSize", MIN_REFERENCE_GROUP_SIZE),
        "referenceGroupCount": len(selection.get("referenceGroups", [])),
        "activeReferenceGroup": selection.get("activeReferenceGroup", {}),
        "rotationPurposeKey": selection.get("rotationPurposeKey", ""),
        "rotationStatus": selection.get("rotationStatus", "NOT_APPLIED"),
        "rotationRecorded": selection.get("rotationRecorded", False),
        "rotationWouldRecord": selection.get("rotationWouldRecord", False),
        "rotationRegistryPath": selection.get("rotationRegistryPath", ""),
        "referenceUsageMode": selection.get("referenceUsageMode", ""),
        "referenceGroupKey": selection.get("referenceGroupKey", ""),
        "memoryGateStatus": selection.get("memoryGateStatus", "NOT_APPLIED"),
        "rejectedDueToReferenceMemory": [
            {
                "path": format_path(row["path"], root),
                "referenceId": row.get("referenceId", ""),
                "reason": row.get("reason", ""),
            }
            for row in selection.get("rejectedDueToReferenceMemory", [])
        ],
        "nextReferenceUsageAction": selection.get("nextReferenceUsageAction", ""),
        "patternLearningPool": [row_to_json(row) for row in selection["patternPool"]],
        "executionInfluencePool": [row_to_json(row) for row in selection["executionPool"]],
        "referenceGroups": [
            group_to_json(index, group)
            for index, group in enumerate(selection.get("referenceGroups", []))
        ],
    }


def build_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Website Template Reference Selection",
        "",
        f"- Generated: {data['generated']}",
        f"- Source: `{data['source']}`",
        f"- Checked sources: {', '.join(f'`{item}`' for item in data.get('checkedSources', [])) or '`none`'}",
        f"- Product type: {data['productType']['name']} (`{data['productType']['id']}`)",
        f"- Standard: {data['productType']['standardRange']}",
        f"- Candidate files scanned: {data['candidateCount']}",
        f"- Product-type matches: {data['matchedCount']}",
        f"- Deduped matches: {data.get('dedupedMatchedCount', data['matchedCount'])}",
        f"- Product-purpose group eligible: {data.get('groupEligibleCount', 0)}",
        f"- Supplemental references for small pools: {data.get('groupSupplementalCount', 0)}",
        f"- Rotation group-ready references: {data.get('groupReadyCount', data.get('groupEligibleCount', 0))}",
        f"- Group source: {data.get('groupSource', 'dynamic-selector')}",
        f"- Reference groups: {data.get('referenceGroupCount', 0)} group(s) of up to {data.get('groupSize', DEFAULT_GROUP_SIZE)}",
        f"- Active reference group: {data.get('activeReferenceGroup', {}).get('groupIndex', 'not-applied')} / {data.get('activeReferenceGroup', {}).get('groupCount', 'not-applied')}",
        f"- Rotation status: {data.get('rotationStatus', 'NOT_APPLIED')}",
        f"- Rotation recorded: {data.get('rotationRecorded', False)}",
        f"- Reference memory gate: {data.get('memoryGateStatus', 'NOT_APPLIED')}",
        f"- Reference usage mode: {data.get('referenceUsageMode') or 'Not applied'}",
        f"- Reference group key: `{data.get('referenceGroupKey') or 'not-applied'}`",
        "",
    ]
    if data.get("nextReferenceUsageAction"):
        lines.extend(
            [
                "## Reference Memory Action",
                "",
                f"- {data['nextReferenceUsageAction']}",
                "",
            ]
        )
    if data.get("rejectedDueToReferenceMemory"):
        lines.extend(["## Rejected Due To Reference Memory", ""])
        for row in data["rejectedDueToReferenceMemory"]:
            lines.append(f"- `{row['path']}` (`{row['referenceId']}`): {row['reason']}")
        lines.append("")
    if data.get("corpusWarning"):
        lines.extend(
            [
                "## Corpus Warning",
                "",
                f"- {data['corpusWarning']}",
                "- Configure `.design-brain/REFERENCE_CORPUS_CONFIG.md`, pass `--source`, or provide a reference image/link before claiming local-reference-led selection.",
                "",
            ]
        )
    lines.extend(["## Pattern Learning Pool", ""])
    if data["patternLearningPool"]:
        for row in data["patternLearningPool"]:
            lines.extend(
                [
                    f"- `{row['path']}`",
                    f"  - Score: {row['score']}",
                    f"  - Match evidence: {', '.join(row['reasons'][:5]) or 'filename relevance'}",
                ]
            )
    else:
        if data.get("candidateCount", 0) == 0:
            lines.append("- No local reference candidates found. Do not claim local-reference-led selection happened.")
        else:
            lines.append("- No product-type-specific matches found. Re-check product type, niche terms, or source folder before designing.")

    lines.extend(["", "## Active Reference Group / Execution Influence Pool", ""])
    if data["executionInfluencePool"]:
        for row in data["executionInfluencePool"]:
            lines.extend(
                [
                    f"- `{row['path']}`",
                    f"  - Why selected: product-type match from local Template Website corpus.",
                    "  - Use for: evidence-backed Designer Cognition Extraction.",
                    "  - Do not copy: composition, image placement, motif, section treatment, or CTA staging.",
                ]
            )
    else:
        lines.append("- No execution references selected.")

    if data.get("referenceGroups"):
        lines.extend(["", "## Reference Group Rotation", ""])
        for group in data["referenceGroups"]:
            active_marker = " (active)" if group["groupIndex"] == data.get("activeReferenceGroup", {}).get("groupIndex") else ""
            refs = "; ".join(row["path"] for row in group["references"])
            lines.append(f"- Group {group['groupIndex']}{active_marker}: {group['groupSize']} refs; `{group['groupFingerprint']}`")
            lines.append(f"  - {refs}")

    lines.extend(
        [
            "",
            "## Next Step",
            "",
            "Use `.design-brain/DESIGNER_COGNITION_LAYER.md` on the Execution Influence Pool before planning structure.",
            "",
        ]
    )
    return "\n".join(lines)


def output_path(args: argparse.Namespace, root: Path) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = root / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "json" if args.json else "md"
    return root / ".design-brain" / "context-packets" / f"{stamp}-{slugify(args.task)}-website-reference-selection.{suffix}"


def main() -> int:
    args = parse_args()
    root = repo_root()
    source, checked_sources = select_source(root, args.source)
    query = " ".join([args.task, args.template_type, args.niche, args.target_buyer])
    record = product_record_by_id(root, args.product_type_id) or select_website_product_type(query, root)
    group_size = max(2, int(args.group_size or DEFAULT_GROUP_SIZE))
    min_group_size = max(1, int(args.min_group_size or MIN_REFERENCE_GROUP_SIZE))
    selection = select_references(
        source,
        record,
        query,
        args.limit,
        args.execution_count,
        group_size,
        min_group_size,
    )
    if args.respect_reference_usage_registry:
        if args.legacy_execution_pool:
            selection = apply_reference_usage_memory(
                selection,
                allow_pair=args.allow_pair_when_singles_exhausted,
                allow_triple=args.allow_triple_when_pairs_exhausted,
            )
        else:
            selection = filter_reference_usage_memory(selection)
    selection = apply_precomputed_product_groups(selection, root, record)
    if not args.legacy_execution_pool:
        selection = apply_group_rotation(
            selection,
            root=root,
            source=source,
            record=record,
            query=query,
            registry_path=rotation_registry_path(root, args.rotation_registry),
            should_record=not args.dry_run and not args.no_record_rotation,
        )
    selection["checkedSources"] = checked_sources
    if selection["candidateCount"] == 0:
        selection["corpusWarning"] = "No local reference candidates found in the checked folders."
    data = serializable(selection, root, source, record)
    text = json.dumps(data, indent=2, ensure_ascii=False) if args.json else build_markdown(data)

    if args.dry_run:
        print(text)
        return 0

    path = output_path(args, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Website reference selection written: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
