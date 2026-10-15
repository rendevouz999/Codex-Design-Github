#!/usr/bin/env python
"""Extract, validate, and select section-level layout patterns.

This tool builds the Section Layout Extraction Library as evidence-backed layout
vocabulary. It never promotes automated image/name guesses into stable patterns;
candidate extraction goes to `_incoming` until hyper-accuracy review passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


SECTION_TYPES: dict[str, dict[str, Any]] = {
    "hero": {
        "aliases": ["hero", "header", "banner", "masthead", "above fold"],
        "density": {"primaryMessage": 1, "cta": "1-2", "proofCue": 1, "mediaSystem": 1},
        "purpose": "Open the template with a product-fit promise, proof cue, and controlled action path.",
    },
    "navigation": {
        "aliases": ["nav", "navbar", "navigation", "menu"],
        "density": {"primaryNavGroups": "3-7", "primaryCta": "0-1", "secondaryCta": "0-1"},
        "purpose": "Create wayfinding and conversion access without becoming a repeated header scaffold.",
    },
    "trust-band": {
        "aliases": ["trust", "logo", "logos", "client", "rating", "credential", "partner"],
        "density": {"proofItems": "3-8", "primaryProofClaim": "0-1"},
        "purpose": "Bridge opening promise into credibility through logos, ratings, metrics, or credentials.",
    },
    "features": {
        "aliases": ["feature", "features", "benefit", "benefits"],
        "density": {"primaryModules": "3-6", "maxWhenGrouped": 8},
        "purpose": "Explain product/service value with grouped modules and clear hierarchy.",
    },
    "services": {
        "aliases": ["service", "services", "solutions", "capabilities", "what we do"],
        "density": {"primaryModules": "3-6", "maxWhenGrouped": 8},
        "purpose": "Show service scope and buyer-fit value without becoming a generic card grid.",
    },
    "process": {
        "aliases": ["process", "workflow", "step", "steps", "how it works"],
        "density": {"steps": "3-6"},
        "purpose": "Make the action path or delivery method understandable and credible.",
    },
    "stats-proof": {
        "aliases": ["stat", "stats", "metric", "metrics", "kpi", "counter", "result"],
        "density": {"metrics": "2-6", "contextNotes": "0-3"},
        "purpose": "Translate proof into scan-friendly evidence and confidence.",
    },
    "portfolio-gallery": {
        "aliases": ["portfolio", "gallery", "showcase", "work", "project", "projects"],
        "density": {"visibleItems": "3-9", "featuredItems": "1-2"},
        "purpose": "Show visual work or product proof with enough rhythm and curation.",
    },
    "case-study": {
        "aliases": ["case", "case study", "study", "result story", "project detail"],
        "density": {"cases": "1-3", "proofPoints": "2-5"},
        "purpose": "Prove capability through problem, action, and outcome evidence.",
    },
    "pricing-packages": {
        "aliases": ["pricing", "price", "plan", "plans", "package", "packages"],
        "density": {"tiers": "2-4", "featuredTier": "0-1"},
        "purpose": "Help buyers compare offers and choose an action path.",
    },
    "testimonials": {
        "aliases": ["testimonial", "testimonials", "review", "reviews", "quote", "client story"],
        "density": {"visibleItems": "2-6", "wallOrCarouselRequiresHierarchy": True},
        "purpose": "Convert social proof into trust without turning the section into noise.",
    },
    "faq-objection": {
        "aliases": ["faq", "question", "questions", "objection", "support"],
        "density": {"questions": "5-8"},
        "purpose": "Resolve buyer uncertainty before conversion or contact.",
    },
    "contact-booking": {
        "aliases": ["contact", "booking", "book", "reservation", "appointment", "form", "location"],
        "density": {"formFields": "3-7", "contactMethods": "1-4"},
        "purpose": "Turn interest into contact, booking, inquiry, or visit confidence.",
    },
    "cta": {
        "aliases": ["cta", "call to action", "get started", "start", "subscribe", "download"],
        "density": {"primaryMessage": 1, "cta": "1-2", "supportingProof": "0-2"},
        "purpose": "Create a product-fit conversion moment without repeating a generic CTA slab.",
    },
    "footer": {
        "aliases": ["footer", "copyright", "social", "legal"],
        "density": {"linkGroups": "2-6", "trustCues": "0-3"},
        "purpose": "Close the page with navigation, trust, contact, and source-template completeness.",
    },
    "dashboard-preview": {
        "aliases": ["dashboard", "analytics", "chart", "table", "widget", "interface"],
        "density": {"previewPanels": "2-6", "primaryScreen": "1"},
        "purpose": "Show interface reality, data hierarchy, and operational credibility.",
    },
    "commerce-grid": {
        "aliases": ["shop", "product", "products", "category", "collection", "cart", "checkout"],
        "density": {"products": "4-12", "featuredProducts": "1-3"},
        "purpose": "Support browsing, product comparison, and purchase confidence.",
    },
    "blog-resources": {
        "aliases": ["blog", "article", "articles", "news", "journal", "resource", "resources"],
        "density": {"visibleItems": "3-6", "featuredItem": "0-1"},
        "purpose": "Add editorial depth, learning value, or ongoing credibility.",
    },
}

REQUIRED_PATTERN_FIELDS = [
    "patternId",
    "sectionType",
    "sourceRefs",
    "productFamilies",
    "commercialPurpose",
    "purposeLayer",
    "anatomyLayer",
    "hierarchyLayer",
    "gridRhythmLayer",
    "densityLimitLayer",
    "originalityLayer",
    "usageRuleLayer",
    "layoutGesture",
    "sectionSilhouette",
    "compositionTension",
    "focalPath",
    "negativeSpaceShape",
    "depthLayering",
    "moduleScaleVariation",
    "breakoutBehavior",
    "contentLimits",
    "antiCopyBoundary",
    "compatibleBeforeAfter",
    "structuralSignature",
    "matchStatus",
    "matchScore",
    "matchGroupId",
    "duplicateOf",
    "variantOf",
    "matchingEvidence",
    "dedupeDecision",
    "confidence",
    "qualityStatus",
]

NULLABLE_REQUIRED_FIELDS = {"duplicateOf", "variantOf"}

MATCH_STATUSES = {"DUPLICATE", "NEAR_DUPLICATE", "VARIANT", "NEW_PATTERN"}
MATCH_AXES = [
    "layoutGesture",
    "sectionSilhouette",
    "anatomyLayer",
    "hierarchyLayer",
    "gridRhythmLayer",
    "focalPath",
    "compositionTension",
    "negativeSpaceShape",
    "moduleScaleVariation",
    "breakoutBehavior",
    "contentLimits",
]
MATCH_THRESHOLDS = {
    "DUPLICATE": 0.90,
    "NEAR_DUPLICATE": 0.78,
    "VARIANT": 0.55,
}
RELATED_SECTION_FAMILIES = [
    {"features", "services"},
    {"cta", "contact-booking", "footer"},
    {"portfolio-gallery", "case-study"},
]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
REFERENCE_EXTENSIONS = IMAGE_EXTENSIONS | {".fig"}


@dataclass
class ValidationResult:
    status: str
    errors: list[str]
    warnings: list[str]
    stable_count: int
    incoming_count: int


@dataclass
class ExtractionWriteResult:
    incoming_patterns: list[Path]
    match_receipts: list[Path]

    def extend(self, other: "ExtractionWriteResult") -> None:
        self.incoming_patterns.extend(other.incoming_patterns)
        self.match_receipts.extend(other.match_receipts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage section layout extraction catalog.")
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="Extract incoming section patterns from evidence/reference files.")
    extract.add_argument("--source", default="Template Website", help="Existing corpus or fig-extract source.")
    extract.add_argument("--new-source", default="", help="Optional new reference folder or file.")
    extract.add_argument("--mode", choices=("existing", "new", "hybrid"), default="hybrid")
    extract.add_argument("--output", default=".design-brain/section-layout-library")
    extract.add_argument("--max-patterns", type=int, default=80)
    extract.add_argument("--json", action="store_true")

    validate = sub.add_parser("validate", help="Validate catalog skeleton and pattern quality gates.")
    validate.add_argument("--catalog", default=".design-brain/section-layout-library")
    validate.add_argument("--json", action="store_true")

    select = sub.add_parser("select", help="Select a stable PASS pattern for a section.")
    select.add_argument("--catalog", default=".design-brain/section-layout-library")
    select.add_argument("--product-family", required=True)
    select.add_argument("--section", required=True)
    select.add_argument("--density", default="")
    select.add_argument("--exclude-fingerprint", default="")
    select.add_argument("--json", action="store_true")

    match = sub.add_parser("match", help="Match one candidate against catalog and report dedupe status.")
    match.add_argument("--candidate", required=True)
    match.add_argument("--catalog", default=".design-brain/section-layout-library")
    match.add_argument("--json", action="store_true")

    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(root: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def slugify(value: str, limit: int = 90) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return (slug or "section-layout")[:limit]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_match_value(value: Any) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).lower()
    if isinstance(value, list):
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).lower()
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def match_tokens(value: Any) -> set[str]:
    text = normalize_match_value(value)
    return {token for token in re.split(r"[^a-z0-9]+", text) if token}


def value_similarity(left: Any, right: Any) -> float:
    left_norm = normalize_match_value(left)
    right_norm = normalize_match_value(right)
    if not left_norm or not right_norm:
        return 0.0
    if left_norm == right_norm:
        return 1.0
    left_tokens = match_tokens(left_norm)
    right_tokens = match_tokens(right_norm)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def pattern_signature_payload(pattern: dict[str, Any]) -> dict[str, str]:
    return {axis: normalize_match_value(pattern.get(axis)) for axis in MATCH_AXES}


def structural_signature(pattern: dict[str, Any]) -> dict[str, Any]:
    axes = pattern_signature_payload(pattern)
    signature_text = json.dumps(axes, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    signature_hash = hashlib.sha1(signature_text.encode("utf-8")).hexdigest()
    return {
        "signatureId": f"{pattern.get('sectionType', 'unknown')}:{signature_hash[:16]}",
        "hash": signature_hash,
        "axes": axes,
    }


def compare_patterns(candidate: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    axis_scores = {
        axis: round(value_similarity(candidate.get(axis), existing.get(axis)), 4)
        for axis in MATCH_AXES
    }
    score = sum(axis_scores.values()) / len(MATCH_AXES)
    return {
        "score": round(score, 4),
        "axisScores": axis_scores,
        "patternId": existing.get("patternId"),
        "sectionType": existing.get("sectionType"),
        "source": existing.get("_matchSource", "unknown"),
        "path": existing.get("_path") or existing.get("_matchPath", ""),
    }


def sections_are_related(left: str, right: str) -> bool:
    if left == right:
        return False
    return any(left in family and right in family for family in RELATED_SECTION_FAMILIES)


def canonical_section(value: str) -> str:
    lowered = value.strip().lower().replace("_", "-")
    aliases = {
        "pricing": "pricing-packages",
        "packages": "pricing-packages",
        "testimonial": "testimonials",
        "faq": "faq-objection",
        "contact": "contact-booking",
        "booking": "contact-booking",
        "stats": "stats-proof",
        "portfolio": "portfolio-gallery",
        "gallery": "portfolio-gallery",
        "dashboard": "dashboard-preview",
        "commerce": "commerce-grid",
        "blog": "blog-resources",
        "resources": "blog-resources",
    }
    return aliases.get(lowered, lowered)


def classify_section(name: str) -> str | None:
    text = f" {name.lower().replace('_', ' ').replace('-', ' ')} "
    best: tuple[int, str] | None = None
    for section, config in SECTION_TYPES.items():
        score = 0
        for alias in config["aliases"]:
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, text):
                score += 2 if " " in alias else 1
        if score and (best is None or score > best[0]):
            best = (score, section)
    return best[1] if best else None


def normalize_product_family(value: str) -> str:
    text = value.lower()
    if "saas" in text or "technology" in text or "ai" in text:
        return "saas"
    if "dashboard" in text or "admin" in text:
        return "dashboard"
    if "ecommerce" in text or "commerce" in text or "shop" in text:
        return "ecommerce"
    if "portfolio" in text:
        return "portfolio"
    if "agency" in text or "studio" in text:
        return "agency"
    if "travel" in text or "hospitality" in text:
        return "travel"
    if "event" in text or "festival" in text:
        return "event"
    if "website" in text or "landing" in text:
        return "website"
    return slugify(value or "general", 40)


def product_families_from_summary(summary: dict[str, Any]) -> list[str]:
    families: list[str] = []
    for item in summary.get("inferredTemplateTypes", []):
        if isinstance(item, dict):
            family = normalize_product_family(str(item.get("type", "")))
            if family and family not in families:
                families.append(family)
    return families or ["website"]


def stable_section_dirs(catalog: Path) -> list[Path]:
    return [catalog / section for section in SECTION_TYPES]


def ensure_catalog(catalog: Path) -> None:
    catalog.mkdir(parents=True, exist_ok=True)
    incoming = catalog / "_incoming"
    (incoming / "source-records").mkdir(parents=True, exist_ok=True)
    (incoming / "_matches").mkdir(parents=True, exist_ok=True)
    for section, config in SECTION_TYPES.items():
        section_dir = catalog / section
        (section_dir / "patterns").mkdir(parents=True, exist_ok=True)
        readme = section_dir / "README.md"
        if not readme.exists():
            readme.write_text(
                f"# {section.replace('-', ' ').title()} Section Patterns\n\n"
                f"{config['purpose']}\n",
                encoding="utf-8",
            )
        index = section_dir / "index.json"
        if not index.exists():
            write_json(
                index,
                {
                    "sectionType": section,
                    "stablePatterns": [],
                    "incomingPolicy": "incoming patterns require hyper-accuracy PASS before selection",
                },
            )


def pattern_from_section(
    *,
    section: str,
    source_ref: str,
    product_families: list[str],
    node_name: str,
    source_kind: str,
    index: int,
) -> dict[str, Any]:
    config = SECTION_TYPES[section]
    slug = slugify(f"{section}-{Path(source_ref).stem}-{node_name}-{index}")
    confidence = "medium" if source_kind == "fig-extract" else "low"
    return {
        "patternId": f"incoming-{slug}",
        "sectionType": section,
        "sourceRefs": [source_ref],
        "productFamilies": product_families,
        "commercialPurpose": config["purpose"],
        "purposeLayer": f"{section} section appears to support: {config['purpose']}",
        "anatomyLayer": f"Observed candidate name `{node_name}` from {source_kind}; requires visual review for exact element anatomy.",
        "hierarchyLayer": "Incoming evidence suggests a section-level attention path, but first/second/third focal order needs visual confirmation.",
        "gridRhythmLayer": "Incoming geometry/name evidence is available; exact grid, rhythm, spacing, and responsive behavior require hyper-accuracy review.",
        "densityLimitLayer": f"Use section density limit: {json.dumps(config['density'], ensure_ascii=False)}.",
        "originalityLayer": "Learn the section role and abstract layout behavior only; do not copy exact reference composition, spacing, copy, imagery, or motif.",
        "usageRuleLayer": "Candidate may inform review vocabulary only until qualityStatus becomes PASS.",
        "layoutGesture": "review-required",
        "sectionSilhouette": "review-required",
        "compositionTension": "review-required",
        "focalPath": "review-required",
        "negativeSpaceShape": "review-required",
        "depthLayering": "review-required",
        "moduleScaleVariation": "review-required",
        "breakoutBehavior": "review-required",
        "contentLimits": config["density"],
        "antiCopyBoundary": "Do not copy exact layout, section shape, component grouping, image placement, color roles, or visual motif.",
        "compatibleBeforeAfter": {
            "before": ["product-family dependent"],
            "after": ["product-family dependent"],
            "notAScaffold": True,
        },
        "confidence": confidence,
        "qualityStatus": "REVIEW_REQUIRED",
        "hyperAccuracyReceipt": {
            "status": "REVIEW_REQUIRED",
            "reviewedAt": "",
            "evidenceType": source_kind,
            "reviewNotes": "Automated extraction created this candidate; visual/source hyper-accuracy review is required before promotion.",
            "nonCopyBoundary": "Do not copy exact visual execution from the source reference.",
        },
        "extractedAt": now_iso(),
    }


def latest_fig_extract_root(root: Path) -> Path | None:
    latest = root / ".design-brain" / "evidence" / "fig-extracts" / "latest.json"
    if not latest.exists():
        return None
    payload = read_json(latest)
    latest_run = payload.get("latestRun")
    if not latest_run:
        return None
    return resolve_path(root, str(latest_run))


def fig_summary_files(root: Path, source: Path) -> list[Path]:
    candidates: list[Path] = []
    if source.exists():
        if source.is_file() and source.name == "message-summary.json":
            candidates.append(source)
        elif source.is_dir():
            candidates.extend(source.rglob("message-summary.json"))

    latest = latest_fig_extract_root(root)
    if latest and latest.exists() and not candidates:
        candidates.extend(latest.rglob("message-summary.json"))
    return sorted(set(path.resolve() for path in candidates))


def patterns_for_matching(catalog: Path) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for path in catalog.glob("*/patterns/*.json"):
        try:
            payload = read_json(path)
        except Exception:
            continue
        payload["_matchPath"] = str(path)
        payload["_path"] = str(path)
        payload["_matchSource"] = "stable"
        patterns.append(payload)

    incoming_root = catalog / "_incoming"
    if incoming_root.exists():
        for path in incoming_root.glob("*/*.json"):
            if path.parent.name in {"source-records", "_matches"}:
                continue
            try:
                payload = read_json(path)
            except Exception:
                continue
            payload["_matchPath"] = str(path)
            payload["_path"] = str(path)
            payload["_matchSource"] = "incoming"
            patterns.append(payload)
    return patterns


def match_status_from_score(score: float) -> str:
    if score >= MATCH_THRESHOLDS["DUPLICATE"]:
        return "DUPLICATE"
    if score >= MATCH_THRESHOLDS["NEAR_DUPLICATE"]:
        return "NEAR_DUPLICATE"
    if score >= MATCH_THRESHOLDS["VARIANT"]:
        return "VARIANT"
    return "NEW_PATTERN"


def match_pattern(candidate: dict[str, Any], catalog: Path) -> dict[str, Any]:
    candidate_section = str(candidate.get("sectionType", ""))
    candidate_signature = structural_signature(candidate)
    same_section_matches: list[dict[str, Any]] = []
    related_warnings: list[dict[str, Any]] = []

    for existing in patterns_for_matching(catalog):
        existing_section = str(existing.get("sectionType", ""))
        comparison = compare_patterns(candidate, existing)
        if existing_section == candidate_section:
            same_section_matches.append(comparison)
        elif sections_are_related(candidate_section, existing_section) and comparison["score"] >= MATCH_THRESHOLDS["NEAR_DUPLICATE"]:
            related_warnings.append(
                {
                    "patternId": comparison["patternId"],
                    "sectionType": comparison["sectionType"],
                    "score": comparison["score"],
                    "source": comparison["source"],
                    "risk": "related-section near-match; warn only, do not auto-block across section types",
                }
            )

    best = sorted(same_section_matches, key=lambda item: item["score"], reverse=True)[0] if same_section_matches else None
    score = float(best["score"]) if best else 0.0
    status = match_status_from_score(score)
    duplicate_of = str(best["patternId"]) if best and status in {"DUPLICATE", "NEAR_DUPLICATE"} else None
    variant_of = str(best["patternId"]) if best and status == "VARIANT" else None
    if best and status != "NEW_PATTERN":
        group_anchor = str(best.get("patternId") or candidate.get("patternId"))
        match_group_id = f"{candidate_section}:{group_anchor}"
    else:
        match_group_id = candidate_signature["signatureId"]

    decisions = {
        "DUPLICATE": "BLOCK_NEW_PATTERN: exact structural duplicate; write match receipt only.",
        "NEAR_DUPLICATE": "REVIEW_REQUIRED: near duplicate evidence recorded; keep candidate only if review proves useful variation.",
        "VARIANT": "REVIEW_REQUIRED: variant candidate may continue with variantOf and hyper-accuracy review.",
        "NEW_PATTERN": "ALLOW_INCOMING: new structural vocabulary candidate; hyper-accuracy review still required.",
    }

    return {
        "matchStatus": status,
        "matchScore": round(score, 4),
        "matchGroupId": match_group_id,
        "duplicateOf": duplicate_of,
        "variantOf": variant_of,
        "structuralSignature": candidate_signature,
        "matchingEvidence": {
            "mode": "exploratory",
            "matchedAt": now_iso(),
            "matchingAxes": MATCH_AXES,
            "thresholds": MATCH_THRESHOLDS,
            "sameSectionCompared": len(same_section_matches),
            "bestMatch": best,
            "relatedSectionWarnings": related_warnings,
        },
        "dedupeDecision": decisions[status],
        "safeToAddPattern": status != "DUPLICATE",
    }


def apply_match_result(pattern: dict[str, Any], match_result: dict[str, Any]) -> dict[str, Any]:
    updated = dict(pattern)
    for field in [
        "structuralSignature",
        "matchStatus",
        "matchScore",
        "matchGroupId",
        "duplicateOf",
        "variantOf",
        "matchingEvidence",
        "dedupeDecision",
    ]:
        updated[field] = match_result.get(field)
    return updated


def write_match_receipt(catalog: Path, candidate: dict[str, Any], match_result: dict[str, Any]) -> Path:
    receipt = {
        "receiptType": "section-layout-match",
        "candidatePatternId": candidate.get("patternId"),
        "sectionType": candidate.get("sectionType"),
        "sourceRefs": candidate.get("sourceRefs", []),
        "matchStatus": match_result.get("matchStatus"),
        "matchScore": match_result.get("matchScore"),
        "matchGroupId": match_result.get("matchGroupId"),
        "duplicateOf": match_result.get("duplicateOf"),
        "variantOf": match_result.get("variantOf"),
        "dedupeDecision": match_result.get("dedupeDecision"),
        "matchingEvidence": match_result.get("matchingEvidence"),
        "recordedAt": now_iso(),
    }
    target = catalog / "_incoming" / "_matches" / f"{slugify(str(candidate.get('patternId', 'candidate')))}-match.json"
    write_json(target, receipt)
    return target


def write_candidate_with_matching(catalog: Path, pattern: dict[str, Any]) -> tuple[Path | None, Path | None, dict[str, Any]]:
    match_result = match_pattern(pattern, catalog)
    updated = apply_match_result(pattern, match_result)
    receipt_path: Path | None = None
    if updated["matchStatus"] in {"DUPLICATE", "NEAR_DUPLICATE"}:
        receipt_path = write_match_receipt(catalog, updated, match_result)
    if updated["matchStatus"] == "DUPLICATE":
        return None, receipt_path, updated
    target = catalog / "_incoming" / str(updated["sectionType"]) / f"{updated['patternId']}.json"
    write_json(target, updated)
    return target, receipt_path, updated


def extract_from_fig_evidence(root: Path, source: Path, catalog: Path, max_patterns: int) -> ExtractionWriteResult:
    result = ExtractionWriteResult([], [])
    for summary_path in fig_summary_files(root, source):
        if len(result.incoming_patterns) >= max_patterns:
            break
        summary = read_json(summary_path)
        source_ref = str(summary.get("source") or summary_path)
        product_families = product_families_from_summary(summary)
        pattern_index = 0
        for group in summary.get("sectionCandidates", []):
            for child in group.get("sections", []):
                node_name = str(child.get("name", ""))
                section = classify_section(node_name)
                if not section:
                    continue
                pattern_index += 1
                pattern = pattern_from_section(
                    section=section,
                    source_ref=source_ref,
                    product_families=product_families,
                    node_name=node_name,
                    source_kind="fig-extract",
                    index=pattern_index,
                )
                pattern_path, receipt_path, _updated = write_candidate_with_matching(catalog, pattern)
                if pattern_path:
                    result.incoming_patterns.append(pattern_path)
                if receipt_path:
                    result.match_receipts.append(receipt_path)
                if len(result.incoming_patterns) >= max_patterns:
                    break
            if len(result.incoming_patterns) >= max_patterns:
                break
    return result


def reference_files(source: Path) -> list[Path]:
    if not source.exists():
        return []
    if source.is_file() and source.suffix.lower() in REFERENCE_EXTENSIONS:
        return [source]
    if source.is_dir():
        return sorted(path for path in source.rglob("*") if path.is_file() and path.suffix.lower() in REFERENCE_EXTENSIONS)
    return []


def extract_new_sources(source: Path, catalog: Path, max_patterns: int) -> ExtractionWriteResult:
    result = ExtractionWriteResult([], [])
    for idx, path in enumerate(reference_files(source), start=1):
        source_record = {
            "sourceId": f"new-source-{slugify(path.stem, 60)}",
            "path": str(path),
            "extension": path.suffix.lower(),
            "recordedAt": now_iso(),
            "status": "REVIEW_REQUIRED",
            "rule": "Image/new-reference sources require visual hyper-accuracy receipt before promotion.",
        }
        write_json(catalog / "_incoming" / "source-records" / f"{source_record['sourceId']}.json", source_record)

        if len(result.incoming_patterns) >= max_patterns:
            continue
        section = classify_section(path.stem)
        if not section:
            continue
        pattern = pattern_from_section(
            section=section,
            source_ref=str(path),
            product_families=["website"],
            node_name=path.stem,
            source_kind="new-reference",
            index=idx,
        )
        pattern_path, receipt_path, _updated = write_candidate_with_matching(catalog, pattern)
        if pattern_path:
            result.incoming_patterns.append(pattern_path)
        if receipt_path:
            result.match_receipts.append(receipt_path)
    return result


def validate_pattern(payload: dict[str, Any], stable: bool) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_PATTERN_FIELDS:
        if field not in payload:
            errors.append(f"missing field `{field}`")
            continue
        value = payload.get(field)
        if field in NULLABLE_REQUIRED_FIELDS:
            continue
        if value is None or value == "" or value == [] or value == {}:
            errors.append(f"missing field `{field}`")
    if payload.get("sectionType") not in SECTION_TYPES:
        errors.append(f"unknown sectionType `{payload.get('sectionType')}`")
    if payload.get("matchStatus") not in MATCH_STATUSES:
        errors.append(f"matchStatus must be one of {sorted(MATCH_STATUSES)}")
    try:
        match_score = float(payload.get("matchScore"))
        if match_score < 0 or match_score > 1:
            errors.append("matchScore must be between 0 and 1")
    except (TypeError, ValueError):
        errors.append("matchScore must be numeric")
    if payload.get("confidence") not in {"high", "medium", "low"}:
        errors.append("confidence must be high, medium, or low")
    if payload.get("qualityStatus") not in {"PASS", "REVIEW_REQUIRED", "BLOCKED"}:
        errors.append("qualityStatus must be PASS, REVIEW_REQUIRED, or BLOCKED")
    receipt = payload.get("hyperAccuracyReceipt", {})
    receipt_status = receipt.get("status") if isinstance(receipt, dict) else None
    if stable:
        if payload.get("qualityStatus") != "PASS":
            errors.append("stable patterns must have qualityStatus PASS")
        if payload.get("confidence") != "high":
            errors.append("stable patterns must have high confidence")
        if receipt_status != "PASS":
            errors.append("stable patterns require hyperAccuracyReceipt.status PASS")
        if payload.get("matchStatus") in {"DUPLICATE", "NEAR_DUPLICATE"}:
            errors.append("stable patterns cannot have DUPLICATE or NEAR_DUPLICATE matchStatus")
    return errors


def validate_catalog(catalog: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    stable_count = 0
    incoming_count = 0

    if not catalog.exists():
        return ValidationResult("BLOCKED", [f"catalog does not exist: {catalog}"], [], 0, 0)

    for section in SECTION_TYPES:
        section_dir = catalog / section
        if not section_dir.exists():
            errors.append(f"missing section folder: {section}")
            continue
        if not (section_dir / "README.md").exists():
            errors.append(f"missing README.md for section: {section}")
        if not (section_dir / "index.json").exists():
            errors.append(f"missing index.json for section: {section}")
        if not (section_dir / "patterns").exists():
            errors.append(f"missing patterns folder for section: {section}")

    stable_payloads: list[dict[str, Any]] = []
    for path in catalog.glob("*/patterns/*.json"):
        stable_count += 1
        try:
            payload = read_json(path)
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        payload["_path"] = str(path)
        stable_payloads.append(payload)
        for error in validate_pattern(payload, stable=True):
            errors.append(f"{path}: {error}")

    for index, left in enumerate(stable_payloads):
        for right in stable_payloads[index + 1 :]:
            if left.get("sectionType") != right.get("sectionType"):
                continue
            comparison = compare_patterns(left, right)
            if comparison["score"] >= MATCH_THRESHOLDS["DUPLICATE"]:
                errors.append(
                    f"stable duplicate patterns: {left.get('patternId')} and {right.get('patternId')} "
                    f"score={comparison['score']}"
                )

    incoming_root = catalog / "_incoming"
    if incoming_root.exists():
        for path in incoming_root.glob("*/*.json"):
            if path.parent.name in {"source-records", "_matches"}:
                continue
            incoming_count += 1
            try:
                payload = read_json(path)
            except Exception as exc:
                errors.append(f"{path}: invalid JSON: {exc}")
                continue
            for error in validate_pattern(payload, stable=False):
                errors.append(f"{path}: {error}")
            if payload.get("qualityStatus") == "PASS":
                warnings.append(f"{path}: PASS incoming pattern should be promoted or reviewed for correct location")

    status = "PASS" if not errors else "BLOCKED"
    return ValidationResult(status, errors, warnings, stable_count, incoming_count)


def stable_patterns(catalog: Path) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for path in catalog.glob("*/patterns/*.json"):
        try:
            payload = read_json(path)
        except Exception:
            continue
        if payload.get("qualityStatus") == "PASS":
            payload["_path"] = str(path)
            patterns.append(payload)
    return patterns


def excluded_pattern_ids(path: Path) -> set[str]:
    if not path or not path.exists():
        return set()
    payload = read_json(path)
    excluded: set[str] = set()
    for value in payload.get("sectionPatternIds", []) or []:
        excluded.add(str(value))
    mix = payload.get("sectionPatternMix", []) or []
    if isinstance(mix, list):
        for item in mix:
            if isinstance(item, dict):
                pattern_id = item.get("patternId")
                if pattern_id:
                    excluded.add(str(pattern_id))
            elif isinstance(item, str):
                excluded.add(item)
    return excluded


def select_pattern(catalog: Path, product_family: str, section: str, density: str, exclude_path: Path | None) -> dict[str, Any]:
    canonical = canonical_section(section)
    excluded = excluded_pattern_ids(exclude_path) if exclude_path else set()
    family = normalize_product_family(product_family)
    candidates: list[tuple[int, dict[str, Any]]] = []
    for pattern in stable_patterns(catalog):
        if pattern.get("sectionType") != canonical:
            continue
        if pattern.get("patternId") in excluded:
            continue
        families = [normalize_product_family(str(item)) for item in pattern.get("productFamilies", [])]
        if family not in families and "website" not in families and "general" not in families:
            continue
        score = 10
        if family in families:
            score += 10
        if density and density.lower() in json.dumps(pattern.get("contentLimits", {})).lower():
            score += 2
        candidates.append((score, pattern))

    if not candidates:
        return {
            "status": "BLOCKED",
            "safeToProceed": False,
            "section": canonical,
            "productFamily": family,
            "selectedPattern": None,
            "requiredRepairs": [
                "No stable PASS section pattern matched. Use extraction output as incoming review material, or promote a hyper-accuracy PASS pattern before build.",
            ],
        }

    selected = sorted(candidates, key=lambda item: (-item[0], item[1]["patternId"]))[0][1]
    return {
        "status": "PASS",
        "safeToProceed": True,
        "section": canonical,
        "productFamily": family,
        "selectedPattern": selected,
        "contentLimits": selected.get("contentLimits"),
        "antiCopyBoundary": selected.get("antiCopyBoundary"),
    }


def main() -> int:
    args = parse_args()
    root = repo_root()

    if args.command == "extract":
        catalog = resolve_path(root, args.output)
        ensure_catalog(catalog)
        written = ExtractionWriteResult([], [])
        if args.mode in {"existing", "hybrid"}:
            written.extend(extract_from_fig_evidence(root, resolve_path(root, args.source), catalog, args.max_patterns))
        if args.mode in {"new", "hybrid"} and args.new_source:
            written.extend(extract_new_sources(resolve_path(root, args.new_source), catalog, args.max_patterns))
        result = {
            "status": "PASS",
            "catalog": str(catalog),
            "mode": args.mode,
            "writtenIncomingPatterns": len(written.incoming_patterns),
            "writtenMatchReceipts": len(written.match_receipts),
            "incomingPatternPaths": [str(path) for path in written.incoming_patterns],
            "matchReceiptPaths": [str(path) for path in written.match_receipts],
            "rule": "Extracted patterns are matched before write and remain incoming review material until hyper-accuracy PASS.",
        }
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(
                f"PASS: wrote {len(written.incoming_patterns)} incoming section pattern(s) "
                f"and {len(written.match_receipts)} match receipt(s) to {catalog}"
            )
        return 0

    if args.command == "validate":
        result = validate_catalog(resolve_path(root, args.catalog))
        payload = {
            "status": result.status,
            "stablePatterns": result.stable_count,
            "incomingPatterns": result.incoming_count,
            "errors": result.errors,
            "warnings": result.warnings,
            "safeToProceed": result.status == "PASS",
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"{result.status}: stable={result.stable_count} incoming={result.incoming_count}")
            for error in result.errors:
                print(f"- {error}")
            for warning in result.warnings:
                print(f"- warning: {warning}")
        return 0 if result.status == "PASS" else 1

    if args.command == "match":
        catalog = resolve_path(root, args.catalog)
        candidate_path = resolve_path(root, args.candidate)
        candidate = read_json(candidate_path)
        result = match_pattern(candidate, catalog)
        payload = {
            "status": "PASS",
            "candidate": str(candidate_path),
            **result,
        }
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(
                f"PASS: {candidate.get('patternId')} -> {result['matchStatus']} "
                f"score={result['matchScore']}"
            )
            if result.get("duplicateOf"):
                print(f"- duplicateOf: {result['duplicateOf']}")
            if result.get("variantOf"):
                print(f"- variantOf: {result['variantOf']}")
        return 0

    if args.command == "select":
        exclude = resolve_path(root, args.exclude_fingerprint) if args.exclude_fingerprint else None
        result = select_pattern(
            resolve_path(root, args.catalog),
            args.product_family,
            args.section,
            args.density,
            exclude,
        )
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"{result['status']}: section={result['section']} productFamily={result['productFamily']}")
            if result.get("selectedPattern"):
                print(f"- selected: {result['selectedPattern']['patternId']}")
            for repair in result.get("requiredRepairs", []):
                print(f"- {repair}")
        return 0 if result["status"] == "PASS" else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
