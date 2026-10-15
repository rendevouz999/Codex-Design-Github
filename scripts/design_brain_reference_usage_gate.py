#!/usr/bin/env python
"""Gate template brand names and reference reuse for Brain Design workflows."""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = ROOT / ".design-brain" / "TEMPLATE_REFERENCE_USAGE_REGISTRY.json"
DEFAULT_RECEIPT_DIR = ROOT / ".design-brain" / "receipts" / "reference-usage"
MAX_GROUP_SIZE = 3
GROUP_MODE_BY_SIZE = {1: "single", 2: "pair", 3: "triple"}
GENERIC_SUFFIX_TOKENS = {
    "studio",
    "agency",
    "creative",
    "design",
    "digital",
    "template",
    "ui",
    "ux",
    "kit",
    "web",
    "website",
    "landing",
    "page",
    "saas",
    "app",
    "dashboard",
    "portfolio",
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "brand",
    "figma",
    "for",
    "site",
    "the",
} | GENERIC_SUFFIX_TOKENS


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def empty_registry() -> dict[str, Any]:
    return {
        "version": "1.0.0",
        "description": "Append-only memory registry for reference brand usage, reference groups, and generated template brand names.",
        "references": [],
        "referenceGroups": [],
        "generatedBrands": [],
        "blockedNames": [],
        "updatedAt": "",
    }


def registry_path(value: str = "") -> Path:
    path = Path(value).expanduser() if value else DEFAULT_REGISTRY_PATH
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def load_registry(path: Path | None = None) -> dict[str, Any]:
    target = path or DEFAULT_REGISTRY_PATH
    if not target.exists():
        return empty_registry()
    data = json.loads(target.read_text(encoding="utf-8"))
    base = empty_registry()
    for key, value in data.items():
        base[key] = value
    return base


def save_registry(path: Path, registry: dict[str, Any]) -> None:
    registry["updatedAt"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8", newline="\n")


def tokens(value: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", value.lower())


def distinctive_tokens(value: str) -> list[str]:
    return [token for token in tokens(value) if token not in STOPWORDS and len(token) > 1]


def compact_name(value: str) -> str:
    return "".join(tokens(value))


def normalized_name(value: str) -> str:
    return " ".join(tokens(value))


def normalize_reference_id(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).lower()


def split_values(value: str) -> list[str]:
    items = [item.strip() for item in re.split(r"[,+;|]", value or "") if item.strip()]
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def reference_ids(value: str) -> list[str]:
    ids = [item.strip() for item in re.split(r"[,+]", value or "") if item.strip()]
    seen: set[str] = set()
    result: list[str] = []
    for item in ids:
        key = normalize_reference_id(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def sorted_reference_ids(ids: list[str]) -> list[str]:
    return sorted(ids, key=lambda item: normalize_reference_id(item))


def group_key(ids: list[str]) -> str:
    return "+".join(sorted_reference_ids(ids))


def reference_lookup(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        normalize_reference_id(str(item.get("referenceId", ""))): item
        for item in registry.get("references", [])
        if item.get("referenceId")
    }


def find_reference(registry: dict[str, Any], reference_id: str) -> dict[str, Any] | None:
    return reference_lookup(registry).get(normalize_reference_id(reference_id))


def find_group(registry: dict[str, Any], key: str) -> dict[str, Any] | None:
    for item in registry.get("referenceGroups", []):
        if str(item.get("groupKey", "")) == key:
            return item
    return None


def group_is_used(group: dict[str, Any] | None) -> bool:
    if not group:
        return False
    usage = group.get("usageStatus", {})
    if isinstance(usage, dict):
        return bool(usage.get("used") or usage.get("singleUsed"))
    return str(usage).lower() in {"used", "single-used", "true"}


def reference_single_used(registry: dict[str, Any], reference_id: str) -> bool:
    reference = find_reference(registry, reference_id)
    if reference:
        usage = reference.get("usageStatus", {})
        if isinstance(usage, dict) and usage.get("singleUsed"):
            return True
    return group_is_used(find_group(registry, group_key([reference_id])))


def reference_brand_name(registry: dict[str, Any], reference_id: str) -> str:
    reference = find_reference(registry, reference_id)
    return str(reference.get("referenceBrandName", "")) if reference else ""


def reference_brand_names_for_ids(
    registry: dict[str, Any],
    ids: list[str],
    provided_names: list[str] | None = None,
) -> list[str]:
    names: list[str] = []
    for ref_id in sorted_reference_ids(ids):
        name = reference_brand_name(registry, ref_id)
        if name:
            names.append(name)
    for name in provided_names or []:
        if name and name not in names:
            names.append(name)
    return names


def row_kind(source: str) -> str:
    normalized = source.lower().replace("_", "-")
    if "reference" in normalized:
        return "reference"
    if "generated" in normalized or "output" in normalized:
        return "generated"
    return "blocked"


def blocked_name_rows(registry: dict[str, Any], extra_reference_brand_names: list[str] | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in registry.get("blockedNames", []):
        name = str(item.get("name", "")).strip()
        if name:
            rows.append({"name": name, "source": str(item.get("source", "blocked-name"))})
    for item in registry.get("generatedBrands", []):
        name = str(item.get("brandName", "") or item.get("candidateBrandName", "")).strip()
        if name:
            rows.append({"name": name, "source": "generated-brand"})
    for item in registry.get("references", []):
        name = str(item.get("referenceBrandName", "")).strip()
        if name:
            rows.append({"name": name, "source": "reference-brand"})
    for name in extra_reference_brand_names or []:
        if name.strip():
            rows.append({"name": name.strip(), "source": "reference-brand"})
    return rows


def first_distinctive(value: str) -> str:
    values = distinctive_tokens(value)
    return values[0] if values else ""


def generic_suffix(value: str) -> str:
    for token in reversed(tokens(value)):
        if token in GENERIC_SUFFIX_TOKENS:
            return token
    return ""


def reference_plus_generic_suffix(candidate: str, reference: str) -> bool:
    candidate_tokens = tokens(candidate)
    reference_tokens = tokens(reference)
    if not candidate_tokens or not reference_tokens:
        return False
    if candidate_tokens[: len(reference_tokens)] != reference_tokens:
        return False
    suffix = candidate_tokens[len(reference_tokens) :]
    return bool(suffix) and all(token in GENERIC_SUFFIX_TOKENS for token in suffix)


def add_unique(target: list[str], seen: set[str], value: str) -> None:
    key = value.lower()
    if key in seen:
        return
    seen.add(key)
    target.append(value)


def name_similarity_report(
    candidate: str,
    registry: dict[str, Any],
    reference_brand_names: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    warnings: list[str] = []
    blocking_seen: set[str] = set()
    warning_seen: set[str] = set()
    candidate = candidate.strip()
    if not candidate:
        return ["CANDIDATE_BRAND_NAME_MISSING"], []

    candidate_norm = normalized_name(candidate)
    candidate_compact = compact_name(candidate)
    candidate_first = first_distinctive(candidate)
    candidate_suffix = generic_suffix(candidate)

    for row in blocked_name_rows(registry, reference_brand_names):
        existing = row["name"].strip()
        if not existing:
            continue
        source = row["source"]
        kind = row_kind(source)
        existing_norm = normalized_name(existing)
        existing_compact = compact_name(existing)
        existing_first = first_distinctive(existing)
        existing_suffix = generic_suffix(existing)

        if candidate_norm and candidate_norm == existing_norm:
            add_unique(
                blocking,
                blocking_seen,
                f"BRAND_NAME_EXACT_MATCH {candidate} matches {existing} ({source})",
            )
            continue
        if candidate_compact and candidate_compact == existing_compact:
            add_unique(
                blocking,
                blocking_seen,
                f"BRAND_NAME_COMPACT_MATCH {candidate} matches {existing} ({source})",
            )
            continue
        if kind == "reference" and reference_plus_generic_suffix(candidate, existing):
            add_unique(
                blocking,
                blocking_seen,
                f"REFERENCE_BRAND_WITH_GENERIC_SUFFIX {candidate} is {existing} plus generic suffix",
            )
            continue
        if candidate_first and candidate_first == existing_first and candidate_suffix and candidate_suffix == existing_suffix:
            add_unique(
                warnings,
                warning_seen,
                f"SIMILARITY_REVISE same first distinctive token and product suffix as {existing} ({source})",
            )
            continue
        if kind == "generated" and candidate_first and candidate_first == existing_first:
            add_unique(
                warnings,
                warning_seen,
                f"SIMILARITY_REVISE same first distinctive token as used generated brand {existing}",
            )

    return blocking, warnings


def unused_single_references(registry: dict[str, Any]) -> list[str]:
    return [
        str(item.get("referenceId", ""))
        for item in registry.get("references", [])
        if item.get("referenceId") and not reference_single_used(registry, str(item.get("referenceId", "")))
    ]


def unused_pair_keys(registry: dict[str, Any]) -> list[str]:
    ids = [str(item.get("referenceId", "")) for item in registry.get("references", []) if item.get("referenceId")]
    unused: list[str] = []
    for pair in itertools.combinations(sorted_reference_ids(ids), 2):
        key = group_key(list(pair))
        if not group_is_used(find_group(registry, key)):
            unused.append(key)
    return unused


def validate_reference_group(
    ids: list[str],
    mode: str,
    registry: dict[str, Any],
    require_exhaustion_order: bool,
) -> tuple[str, list[str], list[str]]:
    reasons: list[str] = []
    warnings: list[str] = []
    size = len(ids)
    if size == 0:
        reasons.append("NO_REFERENCES_PROVIDED")
        return "", reasons, warnings
    if size > MAX_GROUP_SIZE:
        reasons.append("REFERENCE_GROUP_SIZE_EXCEEDS_MAX_3")
        return group_key(ids), reasons, warnings

    expected_mode = GROUP_MODE_BY_SIZE.get(size, "")
    if mode and mode != expected_mode:
        reasons.append(f"REFERENCE_MODE_MISMATCH expected {expected_mode}, got {mode}")
    mode = mode or expected_mode
    key = group_key(ids)

    missing = [ref_id for ref_id in ids if not find_reference(registry, ref_id)]
    if missing:
        warnings.append("UNKNOWN_REFERENCE_ID " + ", ".join(missing))

    existing_group = find_group(registry, key)
    if group_is_used(existing_group):
        reasons.append(f"REFERENCE_GROUP_ALREADY_USED {key}")
    if mode == "single" and reference_single_used(registry, ids[0]):
        reasons.append(f"REFERENCE_SINGLE_ALREADY_USED {ids[0]}")

    if require_exhaustion_order and mode == "pair":
        singles = unused_single_references(registry)
        if singles:
            reasons.append("SINGLES_AVAILABLE_BEFORE_PAIR " + ", ".join(singles[:8]))
    if require_exhaustion_order and mode == "triple":
        singles = unused_single_references(registry)
        pairs = unused_pair_keys(registry)
        if singles:
            reasons.append("SINGLES_AVAILABLE_BEFORE_TRIPLE " + ", ".join(singles[:8]))
        if pairs:
            reasons.append("PAIRS_AVAILABLE_BEFORE_TRIPLE " + ", ".join(pairs[:8]))

    return key, reasons, warnings


def normalized_args(args: argparse.Namespace) -> dict[str, Any]:
    """Normalize canonical args and compatibility aliases into internal names."""
    ids = reference_ids(str(getattr(args, "reference_ids", "") or ""))
    provided_brand_names = split_values(str(getattr(args, "reference_brand_names", "") or ""))
    mode = str(getattr(args, "reference_mode", "") or "").strip().lower()
    if mode not in {"", "single", "pair", "triple"}:
        mode = ""
    return {
        "registry": str(getattr(args, "registry", "") or ""),
        "templateId": str(getattr(args, "template_id", "") or "").strip(),
        "candidateBrandName": str(getattr(args, "candidate_brand_name", "") or "").strip(),
        "brandName": str(getattr(args, "brand_name", "") or "").strip(),
        "referenceIds": ids,
        "referenceBrandNames": provided_brand_names,
        "referenceMode": mode,
        "templateType": str(getattr(args, "template_type", "") or "").strip(),
        "productFamily": str(getattr(args, "product_family", "") or "").strip(),
        "niche": str(getattr(args, "niche", "") or "").strip(),
        "targetBuyer": str(getattr(args, "target_buyer", "") or "").strip(),
        "referenceGroupKey": group_key(ids) if ids else "",
        "requireExhaustionOrder": bool(getattr(args, "require_exhaustion_order", False)),
        "dryRun": bool(getattr(args, "dry_run", False)),
        "completionReceiptPath": str(getattr(args, "completion_receipt_path", "") or "").strip(),
        "fingerprintLockPath": str(getattr(args, "fingerprint_lock_path", "") or "").strip(),
        "doNotCopyBoundary": str(getattr(args, "do_not_copy_boundary", "") or "").strip(),
        "sourcePath": str(getattr(args, "source_path", "") or "").strip(),
        "sourceType": str(getattr(args, "source_type", "") or "").strip(),
    }


def status_from(blocking_reasons: list[str], warnings: list[str]) -> str:
    if blocking_reasons:
        return "BLOCKED"
    if any(warning.startswith("SIMILARITY_REVISE") for warning in warnings):
        return "REVISE_REQUIRED"
    return "PASS"


def check_payload(args: argparse.Namespace, registry: dict[str, Any]) -> dict[str, Any]:
    values = normalized_args(args)
    ids = values["referenceIds"]
    mode = values["referenceMode"]
    inferred_mode = GROUP_MODE_BY_SIZE.get(len(ids), "")
    key, group_reasons, warnings = validate_reference_group(ids, mode, registry, values["requireExhaustionOrder"])
    reference_names = reference_brand_names_for_ids(registry, ids, values["referenceBrandNames"])
    candidate = values["candidateBrandName"]
    name_reasons, name_warnings = name_similarity_report(candidate, registry, reference_names)
    blocking_reasons = name_reasons + group_reasons
    all_warnings = name_warnings + warnings
    status = status_from(blocking_reasons, all_warnings)
    mode = mode or inferred_mode
    next_action = (
        "Proceed with reference cognition and record usage after completion."
        if status == "PASS"
        else "Revise candidate name or choose the next allowed reference group."
    )
    return {
        "command": "check",
        "status": status,
        "templateId": values["templateId"],
        "candidateBrandName": candidate,
        "templateType": values["templateType"],
        "productFamily": values["productFamily"],
        "niche": values["niche"],
        "referenceMode": mode,
        "referenceGroupKey": key,
        "referenceIds": ids,
        "referenceBrandNames": reference_names,
        "blockingReasons": blocking_reasons,
        "warnings": all_warnings,
        "nextAction": next_action,
        "dryRun": values["dryRun"],
        "checkedAt": now(),
    }


def add_blocked_name(registry: dict[str, Any], name: str, source: str, **extra: Any) -> bool:
    if not name.strip():
        return False
    compact = compact_name(name)
    for item in registry.get("blockedNames", []):
        if compact and compact == str(item.get("normalized", "")):
            return False
    registry.setdefault("blockedNames", []).append(
        {
            "name": name.strip(),
            "normalized": compact,
            "source": source,
            "reason": "blocked by Brand & Reference Usage Memory",
            "createdAt": now(),
            **{key: value for key, value in extra.items() if value},
        }
    )
    return True


def ensure_group(
    registry: dict[str, Any],
    ids: list[str],
    mode: str,
    used: bool = False,
    template_id: str = "",
    reference_brand_names: list[str] | None = None,
) -> dict[str, Any]:
    key = group_key(ids)
    existing = find_group(registry, key)
    if existing:
        return existing
    group = {
        "groupKey": key,
        "groupSize": len(ids),
        "mode": mode or GROUP_MODE_BY_SIZE.get(len(ids), ""),
        "referenceIds": sorted_reference_ids(ids),
        "referenceBrandNames": reference_brand_names_for_ids(registry, sorted_reference_ids(ids), reference_brand_names),
        "usageStatus": {"used": used, "usedAt": now() if used else "", "templateId": template_id},
        "createdAt": now(),
    }
    registry.setdefault("referenceGroups", []).append(group)
    return group


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    path = registry_path(args.registry)
    registry = load_registry(path)
    return {
        "command": "status",
        "status": "PASS",
        "registryPath": str(path),
        "referenceCount": len(registry.get("references", [])),
        "referenceGroupCount": len(registry.get("referenceGroups", [])),
        "generatedBrandCount": len(registry.get("generatedBrands", [])),
        "blockedNameCount": len(registry.get("blockedNames", [])),
        "unusedSingles": unused_single_references(registry),
        "unusedPairs": unused_pair_keys(registry),
        "updatedAt": registry.get("updatedAt", ""),
    }


def command_check(args: argparse.Namespace) -> dict[str, Any]:
    return check_payload(args, load_registry(registry_path(args.registry)))


def record_payload_from_check(args: argparse.Namespace, check: dict[str, Any], *, saved: bool) -> dict[str, Any]:
    values = normalized_args(args)
    status = check["status"]
    blocked = check.get("blockingReasons", [])
    warnings = check.get("warnings", [])
    mode = check.get("referenceMode", values["referenceMode"])
    return {
        "command": "record",
        "status": status,
        "templateId": values["templateId"],
        "brandName": values["brandName"] or values["candidateBrandName"],
        "templateType": values["templateType"],
        "productFamily": values["productFamily"],
        "niche": values["niche"],
        "targetBuyer": values["targetBuyer"],
        "referenceMode": mode,
        "referenceGroupKey": check.get("referenceGroupKey", values["referenceGroupKey"]),
        "referenceIds": check.get("referenceIds", values["referenceIds"]),
        "referenceBrandNames": check.get("referenceBrandNames", values["referenceBrandNames"]),
        "registryUpdated": saved,
        "generatedBrandRecorded": saved,
        "referenceGroupRecorded": saved,
        "singleReferenceMarkedUsed": bool(saved and mode == "single"),
        "blockedNamesUpdated": saved,
        "completionReceiptPath": values["completionReceiptPath"],
        "fingerprintLockPath": values["fingerprintLockPath"],
        "blockingReasons": blocked,
        "warnings": warnings,
        "nextAction": (
            "Reference usage recorded. This output brand and reference group are now blocked from direct reuse."
            if saved
            else check.get("nextAction", "Review blocking reasons before recording reference usage.")
        ),
        "dryRun": values["dryRun"],
        "recordedAt": now(),
    }


def command_record(args: argparse.Namespace) -> dict[str, Any]:
    path = registry_path(args.registry)
    registry = load_registry(path)
    values = normalized_args(args)
    if values["brandName"] and not values["candidateBrandName"]:
        args.candidate_brand_name = values["brandName"]
    check = check_payload(args, registry)
    if check["status"] != "PASS":
        return record_payload_from_check(args, check, saved=False)
    if values["dryRun"]:
        return record_payload_from_check(args, check, saved=False)

    ids = check["referenceIds"]
    mode = check["referenceMode"]
    key = check["referenceGroupKey"]
    template_id = values["templateId"]
    group = ensure_group(registry, ids, mode, used=True, template_id=template_id, reference_brand_names=check["referenceBrandNames"])
    group["usageStatus"] = {"used": True, "usedAt": now(), "templateId": template_id}

    if mode == "single" and ids:
        reference = find_reference(registry, ids[0])
        if reference is not None:
            usage = reference.setdefault("usageStatus", {})
            usage["singleUsed"] = True
            usage["singleUsedAt"] = now()
            usage["templateId"] = template_id

    registry.setdefault("generatedBrands", []).append(
        {
            "templateId": template_id,
            "brandName": values["brandName"] or check["candidateBrandName"],
            "templateType": values["templateType"],
            "productFamily": values["productFamily"],
            "niche": values["niche"],
            "targetBuyer": values["targetBuyer"],
            "referenceMode": mode,
            "referenceUsageMode": mode,
            "referenceGroupKey": key,
            "referenceIds": ids,
            "referenceBrandNames": check["referenceBrandNames"],
            "styleDnaSummary": str(getattr(args, "style_dna_summary", "") or "").strip(),
            "reinterpretationPlan": str(getattr(args, "reinterpretation_plan", "") or "").strip(),
            "structuralReconfigurationPlan": str(getattr(args, "structural_reconfiguration_plan", "") or "").strip(),
            "completionReceiptPath": values["completionReceiptPath"],
            "fingerprintLockPath": values["fingerprintLockPath"],
            "doNotCopyBoundary": values["doNotCopyBoundary"],
            "createdAt": now(),
        }
    )
    add_blocked_name(registry, values["brandName"] or check["candidateBrandName"], "output-brand", templateId=template_id)
    for ref_id, ref_name in zip(ids, check["referenceBrandNames"]):
        if ref_name:
            add_blocked_name(registry, ref_name, "reference-brand", referenceId=ref_id)
    save_registry(path, registry)
    return record_payload_from_check(args, check, saved=True)


def command_suggest_group(args: argparse.Namespace) -> dict[str, Any]:
    values = normalized_args(args)
    registry = load_registry(registry_path(args.registry))
    requested_mode = values["referenceMode"]
    refs = [str(item.get("referenceId", "")) for item in registry.get("references", []) if item.get("referenceId")]
    if not refs:
        return {
            "command": "suggest-group",
            "status": "BLOCKED",
            "productFamily": values["productFamily"],
            "niche": values["niche"],
            "suggestedReferenceMode": requested_mode,
            "referenceGroupKey": "",
            "referenceIds": [],
            "referenceBrandNames": [],
            "reason": "Reference stock is empty.",
            "nextAction": "Register references first.",
            "checkedAt": now(),
        }

    candidates: list[tuple[str, list[str], str]] = []
    if requested_mode in {"", "single"}:
        for ref_id in sorted_reference_ids(refs):
            candidates.append(("single", [ref_id], "Use this single reference before escalating to pairs."))
    if requested_mode in {"", "pair"}:
        for pair in itertools.combinations(sorted_reference_ids(refs), 2):
            candidates.append(("pair", list(pair), "Use this pair; singles are exhausted or pair mode was requested."))
    if requested_mode in {"", "triple"}:
        for trio in itertools.combinations(sorted_reference_ids(refs), 3):
            candidates.append(("triple", list(trio), "Use this triple; lower groups are exhausted or triple mode was requested."))

    for mode, ids, reason in candidates:
        key = group_key(ids)
        if mode == "single" and reference_single_used(registry, ids[0]):
            continue
        if mode != "single" and group_is_used(find_group(registry, key)):
            continue
        return {
            "command": "suggest-group",
            "status": "PASS",
            "productFamily": values["productFamily"],
            "niche": values["niche"],
            "suggestedReferenceMode": mode,
            "referenceGroupKey": key,
            "referenceIds": ids,
            "referenceBrandNames": reference_brand_names_for_ids(registry, ids),
            "reason": reason,
            "nextAction": "Run check with this group before Style DNA extraction.",
            "checkedAt": now(),
        }

    return {
        "command": "suggest-group",
        "status": "BLOCKED",
        "productFamily": values["productFamily"],
        "niche": values["niche"],
        "suggestedReferenceMode": requested_mode,
        "referenceGroupKey": "",
        "referenceIds": [],
        "referenceBrandNames": [],
        "reason": "Requested reference stock is exhausted.",
        "nextAction": "Add new references or create a new reference pool.",
        "checkedAt": now(),
    }


def command_init_reference(args: argparse.Namespace) -> dict[str, Any]:
    path = registry_path(args.registry)
    registry = load_registry(path)
    values = normalized_args(args)
    ref_id = str(getattr(args, "reference_id", "") or "").strip()
    ref_brand = str(getattr(args, "reference_brand_name", "") or "").strip() or ref_id
    warnings: list[str] = []
    blocking: list[str] = []
    if not ref_id:
        blocking.append("REFERENCE_ID_MISSING")
    if not ref_brand:
        blocking.append("REFERENCE_BRAND_NAME_MISSING")

    existing = find_reference(registry, ref_id) if ref_id else None
    saved = False
    action = "dry-run"
    if not blocking and existing:
        action = "already-registered"
        if str(existing.get("referenceBrandName", "")) != ref_brand:
            warnings.append("REFERENCE_ID_ALREADY_REGISTERED_WITH_DIFFERENT_BRAND")
        if not values["dryRun"]:
            add_blocked_name(registry, str(existing.get("referenceBrandName", "")), "reference-brand", referenceId=ref_id)
            save_registry(path, registry)
    elif not blocking and not values["dryRun"]:
        reference = {
            "referenceId": ref_id,
            "referenceBrandName": ref_brand,
            "referencePath": str(getattr(args, "reference_path", "") or "").strip() or values["sourcePath"],
            "sourcePath": values["sourcePath"],
            "sourceType": values["sourceType"],
            "templateType": values["templateType"],
            "productFamily": values["productFamily"],
            "niche": values["niche"],
            "doNotCopyBoundary": values["doNotCopyBoundary"],
            "usageStatus": {"singleUsed": False, "singleUsedAt": "", "templateId": ""},
            "createdAt": now(),
        }
        registry.setdefault("references", []).append(reference)
        add_blocked_name(registry, ref_brand, "reference-brand", referenceId=ref_id)
        save_registry(path, registry)
        saved = True
        action = "registered"

    status = status_from(blocking, warnings)
    return {
        "command": "init-reference",
        "status": status,
        "referenceId": ref_id,
        "referenceBrandName": ref_brand,
        "productFamily": values["productFamily"],
        "niche": values["niche"],
        "sourcePath": values["sourcePath"],
        "sourceType": values["sourceType"],
        "registryUpdated": saved,
        "dryRun": values["dryRun"],
        "warnings": warnings,
        "blockingReasons": blocking,
        "nextAction": "Reference registered." if action == "registered" else "No registry write performed." if values["dryRun"] else action,
        "recordedAt": now(),
    }


def safe_filename(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._")
    return clean or "reference-usage"


def default_receipt_path(payload: dict[str, Any]) -> Path:
    template_id = (
        str(payload.get("templateId", "") or "")
        or str(payload.get("referenceId", "") or "")
        or str(payload.get("referenceGroupKey", "") or "")
        or "reference-usage"
    )
    command = str(payload.get("command", "reference-usage") or "reference-usage")
    return DEFAULT_RECEIPT_DIR / f"{safe_filename(template_id)}-{safe_filename(command)}-{timestamp_slug()}.json"


def write_receipt_if_requested(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    if not bool(getattr(args, "write_receipt", False)):
        return payload
    output = str(getattr(args, "receipt_output", "") or "").strip()
    path = Path(output).expanduser() if output else default_receipt_path(payload)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    payload["receiptPath"] = str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def add_common(parser: argparse.ArgumentParser, *, include_receipt: bool = True) -> None:
    parser.add_argument("--registry", default="", help="Optional registry JSON path.")
    parser.add_argument("--json", action="store_true", help="Print JSON payload.")
    if include_receipt:
        parser.add_argument("--write-receipt", action="store_true", help="Write JSON result to a receipt file.")
        parser.add_argument("--receipt-output", default="", help="Optional receipt output path.")


def add_metadata_fields(p: argparse.ArgumentParser) -> None:
    p.add_argument("--template-id", default="")
    p.add_argument("--template-type", default="")
    p.add_argument("--product-family", default="")
    p.add_argument("--niche", default="")
    p.add_argument("--target-buyer", default="")


def add_check_fields(p: argparse.ArgumentParser, *, candidate_required: bool = True) -> None:
    add_common(p)
    p.add_argument("--candidate-brand-name", "--candidate-name", dest="candidate_brand_name", required=candidate_required)
    p.add_argument("--reference-ids", "--references", dest="reference_ids", required=True, help="Comma-separated reference IDs.")
    p.add_argument("--reference-brand-names", "--reference-brands", "--ref-brands", dest="reference_brand_names", default="")
    p.add_argument("--reference-mode", "--mode", dest="reference_mode", default="", choices=["", "single", "pair", "triple"])
    p.add_argument("--require-exhaustion-order", "--require-order", dest="require_exhaustion_order", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    add_metadata_fields(p)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain Design brand/reference usage memory gate.")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    add_common(status, include_receipt=False)

    check = sub.add_parser("check")
    add_check_fields(check)

    record = sub.add_parser("record")
    add_common(record)
    record.add_argument("--candidate-brand-name", "--brand-name", dest="brand_name", required=True)
    record.add_argument("--reference-ids", "--references", dest="reference_ids", required=True, help="Comma-separated reference IDs.")
    record.add_argument("--reference-brand-names", "--reference-brands", "--ref-brands", dest="reference_brand_names", default="")
    record.add_argument("--reference-mode", "--mode", dest="reference_mode", default="", choices=["", "single", "pair", "triple"])
    record.add_argument("--require-exhaustion-order", "--require-order", dest="require_exhaustion_order", action="store_true")
    record.add_argument("--dry-run", action="store_true")
    add_metadata_fields(record)
    record.add_argument("--completion-receipt-path", "--receipt-path", "--completion-receipt", dest="completion_receipt_path", default="")
    record.add_argument("--fingerprint-lock-path", "--fingerprint-path", "--fingerprint-lock", dest="fingerprint_lock_path", default="")
    record.add_argument("--do-not-copy-boundary", "--do-not-copy", dest="do_not_copy_boundary", default="")
    record.add_argument("--style-dna-summary", default="")
    record.add_argument("--reinterpretation-plan", default="")
    record.add_argument("--structural-reconfiguration-plan", default="")

    suggest = sub.add_parser("suggest-group")
    add_common(suggest)
    suggest.add_argument("--reference-mode", "--mode", dest="reference_mode", default="", choices=["", "single", "pair", "triple"])
    suggest.add_argument("--product-family", default="")
    suggest.add_argument("--niche", default="")
    suggest.add_argument("--dry-run", action="store_true")

    init = sub.add_parser("init-reference")
    add_common(init)
    init.add_argument("--reference-id", required=True)
    init.add_argument("--reference-brand-name", "--reference-brand", "--brand-name", dest="reference_brand_name", required=True)
    init.add_argument("--reference-path", default="")
    init.add_argument("--source-path", "--source", dest="source_path", default="")
    init.add_argument("--source-type", default="")
    init.add_argument("--do-not-copy-boundary", "--do-not-copy", dest="do_not_copy_boundary", default="")
    init.add_argument("--dry-run", action="store_true")
    add_metadata_fields(init)

    return parser.parse_args()


def error_payload(args: argparse.Namespace, exc: Exception) -> dict[str, Any]:
    command = str(getattr(args, "command", "") or "unknown")
    blocking = [f"REFERENCE_USAGE_GATE_ERROR {exc}"]
    base: dict[str, Any] = {"command": command, "status": "BLOCKED", "blockingReasons": blocking, "warnings": []}
    if command == "check":
        base.update(
            {
                "templateId": str(getattr(args, "template_id", "") or ""),
                "candidateBrandName": str(getattr(args, "candidate_brand_name", "") or ""),
                "templateType": str(getattr(args, "template_type", "") or ""),
                "productFamily": str(getattr(args, "product_family", "") or ""),
                "niche": str(getattr(args, "niche", "") or ""),
                "referenceMode": str(getattr(args, "reference_mode", "") or ""),
                "referenceGroupKey": "",
                "referenceIds": reference_ids(str(getattr(args, "reference_ids", "") or "")),
                "referenceBrandNames": split_values(str(getattr(args, "reference_brand_names", "") or "")),
                "nextAction": "Fix the gate error before continuing.",
                "dryRun": bool(getattr(args, "dry_run", False)),
                "checkedAt": now(),
            }
        )
    return base


def main() -> int:
    args = parse_args()
    commands = {
        "status": command_status,
        "check": command_check,
        "record": command_record,
        "suggest-group": command_suggest_group,
        "init-reference": command_init_reference,
    }
    try:
        payload = commands[args.command](args)
        payload = write_receipt_if_requested(args, payload)
    except Exception as exc:
        payload = error_payload(args, exc)
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"{payload.get('status', 'BLOCKED')}: {args.command}")
        if payload.get("blockingReasons"):
            for reason in payload["blockingReasons"]:
                print(f"- {reason}")
        if payload.get("warnings"):
            for warning in payload["warnings"]:
                print(f"- warning: {warning}")
    return 0 if payload.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
