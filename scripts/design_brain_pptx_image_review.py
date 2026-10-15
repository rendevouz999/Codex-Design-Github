#!/usr/bin/env python3
"""Read-only PPTX image receipt checker; MAIN supplies visual/rights attestations.

Run: python scripts/design_brain_pptx_image_review.py project/images/image_review.json
     --stage progress|handoff|final
File references contain path + sha256. Relative evidence paths resolve beside the
manifest; adopted assets and final decks require absolute paths. placement_sha256
uses placement_digest(manifest, slot, handoff); provenance record bindings use
json_digest(record). No downloads, mutations, visual judgment or exporter hooks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile

sys.dont_write_bytecode = True
STAGES = ("progress", "handoff", "final")
PLACEMENT_FIELDS = ("placement_inches", "crop_fit", "focal_crop_direction",
                    "protected_subject_areas", "text_safe_area", "semantic_role", "alt_text")


class Invalid(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Invalid(message)


def obj(value, label):
    need(isinstance(value, dict), f"{label} must be an object")
    return value


def text(value, label):
    need(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty text")
    return value


def number(value, label, positive=False):
    need(isinstance(value, (int, float)) and not isinstance(value, bool)
         and math.isfinite(value) and (value > 0 if positive else value >= 0),
         f"{label} must be a finite {'positive' if positive else 'non-negative'} number")
    return value


def slide_number(value, label):
    need(isinstance(value, int) and not isinstance(value, bool) and value > 0,
         f"{label} must be a 1-based slide number")


def sha(value, label):
    need(isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value)),
         f"{label} must be a lowercase SHA-256")
    return value


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def file_digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def placement_digest(manifest, slot, handoff):
    """Bind reviewed framing/content to this stable slot, slide and canvas."""
    value = {key: handoff.get(key) for key in PLACEMENT_FIELDS}
    value.update(deck_id=manifest["deck_id"], slot_id=slot["slot_id"],
                 deck_purpose=manifest["deck_purpose"], visual_tone=manifest["visual_tone"],
                 slide_number=slot["slide_number"], slide_title=slot["slide_title"],
                 message=slot["message"], image_brief=slot["image_brief"],
                 canvas_inches=manifest["canvas_inches"])
    return json_digest(value)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def file_ref(value, base, label, absolute=False):
    value = obj(value, label)
    path = Path(text(value.get("path"), f"{label}.path"))
    need(not absolute or path.is_absolute(), f"{label}.path must be absolute")
    path = path if path.is_absolute() else base / path
    need(path.is_file(), f"{label} file missing: {path}")
    need(file_digest(path) == sha(value.get("sha256"), f"{label}.sha256"),
         f"{label} file hash mismatch: {path}")
    return path


def evidence(values, base, label):
    need(isinstance(values, list) and values, f"{label} requires evidence path + SHA-256")
    for index, value in enumerate(values):
        file_ref(value, base, f"{label}[{index}]")


def main_review(value, label):
    need(value.get("reviewer") == "main", f"{label} reviewer must be main")
    text(value.get("reason"), f"{label}.reason")


def rounds_state(slot, base, round_registry):
    rounds = slot.get("rounds")
    need(isinstance(rounds, list), "rounds must be an ordered array")
    rejected = 0
    rejected_candidates = set()
    unique = []
    for raw in rounds:
        row = obj(raw, "round")
        round_id = text(row.get("round_id"), "round_id")
        identity = (slot["slot_id"], row)
        if round_id in round_registry:
            need(round_registry[round_id] == identity, f"conflicting duplicate round_id: {round_id}")
            continue
        round_registry[round_id] = identity
        owner = row.get("search_owner")
        need(owner in ("engineer", "main"), f"{round_id}: invalid search_owner")
        need(unique or owner == "engineer", f"{round_id}: initial search must be Engineer-owned")
        need(rejected < 2 or owner == "main", f"{round_id}: MAIN_SEARCH_REQUIRED; Engineer cannot search/accept after two rejected rounds")
        slide_number(row.get("slide_number"), f"{round_id}.slide_number")
        text(row.get("provider"), f"{round_id}.provider")
        text(row.get("query"), f"{round_id}.query")
        main_review(row, round_id)
        candidates = row.get("candidate_ids")
        need(isinstance(candidates, list), f"{round_id}.candidate_ids must be an array")
        for candidate in candidates:
            text(candidate, f"{round_id}.candidate_id")
        need(len(set(candidates)) == len(candidates), f"{round_id}: duplicate candidate IDs")
        verdict = row.get("verdict")
        need(verdict in ("accept", "reject", "blocked"), f"{round_id}: invalid verdict")
        if verdict == "blocked":
            need(row.get("blocked_kind") in ("provider", "network", "access", "evidence"),
                 f"{round_id}: blocked_kind must identify an access/tool/evidence failure")
            # No pixels may be available during a provider outage. Do not fake visual review.
            need(isinstance(row.get("visual_evidence"), list), f"{round_id}.visual_evidence must be an array (empty if pixels are unavailable)")
            if row["visual_evidence"]:
                evidence(row["visual_evidence"], base, f"{round_id}.visual_evidence")
        else:
            need(candidates, f"{round_id}: reviewed candidate round is empty")
            need(row.get("slide_context_seen") is True, f"{round_id}: MAIN must see actual candidates in slide context")
            evidence(row.get("visual_evidence"), base, f"{round_id}.visual_evidence")
            if verdict == "reject":
                rejected += owner == "engineer"
                rejected_candidates.update(candidates)
            else:
                fit = obj(row.get("fit_review"), f"{round_id}.fit_review")
                for criterion in ("tone", "content", "purpose"):
                    finding = obj(fit.get(criterion), f"{round_id}.fit_review.{criterion}")
                    need(finding.get("verdict") == "pass",
                         f"{round_id}: image {criterion} must pass; mismatch requires rejection")
                    text(finding.get("reason"), f"{round_id}.fit_review.{criterion}.reason")
                selected = row.get("selected_candidate_id")
                need(selected in candidates, f"{round_id}: selected candidate is absent from this round")
                need(selected not in rejected_candidates, f"{round_id}: cannot promote a previously rejected candidate")
                sha(row.get("asset_sha256"), f"{round_id}.asset_sha256")
                sha(row.get("placement_sha256"), f"{round_id}.placement_sha256")
        unique.append(row)
    defects = slot.get("rendering_defects", [])
    need(isinstance(defects, list), "rendering_defects must be an array separate from candidate rounds")
    defect_ids = set()
    for raw in defects:
        defect = obj(raw, "rendering_defect")
        event_id = text(defect.get("event_id"), "rendering_defect.event_id")
        need(event_id not in defect_ids, f"duplicate rendering defect: {event_id}")
        defect_ids.add(event_id)
        main_review(defect, event_id)
        need(defect.get("status") in ("open", "resolved"), f"{event_id}: invalid rendering defect status")
        evidence(defect.get("visual_evidence"), base, f"{event_id}.visual_evidence")
    accepted = unique[-1] if unique and unique[-1]["verdict"] == "accept" else None
    state = "ACCEPTED" if accepted else "MAIN_SEARCH_REQUIRED" if rejected >= 2 else "ENGINEER_SEARCH_REQUIRED"
    return state, rejected, accepted, defects


def source_record(path, filename):
    need(path.name == "image_sources.json", "source_manifest must reference image_sources.json")
    payload = obj(read_json(path), "image_sources.json")
    items = payload.get("items")
    need(isinstance(items, list), "image_sources.json must contain an items array")
    records = {}
    for raw in items:
        item = obj(raw, "image_sources item")
        name = text(item.get("filename"), "source filename")
        need(name not in (".", "..") and not any(char in name for char in "/\\:"), "source filename must be bare")
        need(name.casefold() not in records, f"duplicate source filename: {name}")
        records[name.casefold()] = item
    record = records.get(filename.casefold())
    need(record is not None and record["filename"] == filename, f"image_sources.json has no exact filename record: {filename}")
    need(record.get("status") == "sourced", "source record status must be sourced")
    for key in ("source_page_url", "license_url"):
        url = urlsplit(text(record.get(key), key))
        need(url.scheme in ("http", "https") and bool(url.netloc), f"source record {key} must be an HTTP(S) URL")
    license_name = text(record.get("license_name"), "license_name").casefold()
    need(license_name not in ("unknown", "manual", "manual-unverified", "unverified"), "unknown/manual-unverified license cannot pass")
    tier = record.get("license_tier")
    need(tier in ("no-attribution", "attribution-required"), "unknown/manual-unverified license_tier cannot pass")
    need(record.get("attribution_required") is (tier == "attribution-required"), "provenance attribution flag conflicts with license_tier")
    if tier == "attribution-required":
        text(record.get("attribution_text"), "canonical attribution_text")
    return record


def check_handoff(manifest, slot, accepted, base):
    need(accepted is not None, "current accepted round missing; search/review required before handoff")
    handoff = obj(slot.get("handoff"), "handoff")
    main_review(handoff, "handoff")
    for key, expected in (("round_id", accepted["round_id"]), ("candidate_id", accepted["selected_candidate_id"]),
                          ("slide_number", slot["slide_number"])):
        need(handoff.get(key) == expected, f"handoff {key} does not match current accepted slot/round")
    need(accepted["slide_number"] == slot["slide_number"], "accepted visual context is stale after slide renumbering")
    asset_path = file_ref(handoff.get("asset"), base, "handoff.asset", absolute=True)
    need(handoff["asset"]["sha256"] == accepted["asset_sha256"], "handoff asset differs from accepted candidate")
    placement = obj(handoff.get("placement_inches"), "placement_inches")
    for key in ("x", "y", "width", "height"):
        number(placement.get(key), f"placement_inches.{key}", positive=key in ("width", "height"))
    canvas = manifest["canvas_inches"]
    need(placement["x"] + placement["width"] <= canvas["width"] + 1e-9 and
         placement["y"] + placement["height"] <= canvas["height"] + 1e-9,
         "placement is outside declared actual canvas")
    need(handoff.get("crop_fit") in ("fill", "fit", "stretch"), "crop_fit must be fill, fit or stretch")
    for key in PLACEMENT_FIELDS[2:] + ("replacement_instructions",):
        text(handoff.get(key), f"handoff.{key}")
    binding = placement_digest(manifest, slot, handoff)
    need(binding == accepted["placement_sha256"], "accepted placement/context binding is stale")
    filename = text(handoff.get("source_filename"), "source_filename")
    need(filename == asset_path.name, "source_filename must link the adopted local original")
    source_path = Path(text(manifest.get("source_manifest"), "source_manifest"))
    source_path = source_path if source_path.is_absolute() else base / source_path
    record = source_record(source_path, filename)
    review = obj(handoff.get("provenance_review"), "provenance_review")
    main_review(review, "provenance_review")
    need(review.get("decision") == "approved", "MAIN intended-use license decision is not approved")
    need(review.get("intended_use") in ("presentation", "editable-commercial-template"), "provenance_review intended_use must be explicit")
    need(review.get("source_record_sha256") == json_digest(record), "provenance review is stale against image_sources.json")
    evidence(review.get("license_evidence"), base, "provenance_review.license_evidence")
    return handoff, binding


def check_final(manifest, slot, handoff, binding, defects, base):
    need(not any(defect["status"] == "open" for defect in defects), "unresolved rendering defect blocks final")
    deck = obj(manifest.get("deck"), "deck")
    path = file_ref(deck, base, "deck", absolute=True)
    need(path.suffix.lower() == ".pptx", "final deck must be a .pptx file")
    with ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("ppt/presentation.xml"))
    size = root.find("{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
    need(size is not None, "PPTX actual canvas missing")
    actual = {"width": int(size.attrib["cx"]) / 914400, "height": int(size.attrib["cy"]) / 914400}
    need(all(abs(actual[key] - manifest["canvas_inches"][key]) <= 1 / 914400 for key in actual),
         "declared canvas differs from actual PPTX canvas")
    slides = root.find("{http://schemas.openxmlformats.org/presentationml/2006/main}sldIdLst")
    need(slides is not None and slot["slide_number"] <= len(slides), "assigned slide does not exist in current PPTX")
    review = obj(slot.get("final_review"), "final_review")
    main_review(review, "final_review")
    need(review.get("verdict") == "pass", "MAIN rendered-slide review must pass")
    expected = {"round_id": handoff["round_id"], "candidate_id": handoff["candidate_id"],
                "slide_number": slot["slide_number"], "asset_sha256": handoff["asset"]["sha256"],
                "placement_sha256": binding, "deck_sha256": deck["sha256"]}
    for key, value in expected.items():
        need(review.get(key) == value, f"final_review {key} is stale")
    file_ref(review.get("screenshot"), base, "final_review.screenshot")
    need(review.get("native_picture_editable") is True, "MAIN native replaceable-picture attestation missing")
    evidence(review.get("native_picture_evidence"), base, "final_review.native_picture_evidence")


def validate(path, stage="progress"):
    """Return machine-readable results; PASS covers receipt checks only."""
    result = {"status": "BLOCKED", "stage": stage, "manifest": str(path), "errors": [], "slots": [],
              "scope": "Read-only receipt consistency; MAIN visual/rights/native-object attestations are not independently proved."}
    try:
        need(stage in STAGES, "invalid stage")
        path = Path(path).resolve()
        manifest = obj(read_json(path), "manifest")
        need(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 2,
             "schema_version must be integer 2; legacy receipts require fresh Main tone/content/purpose review")
        result["deck_id"] = text(manifest.get("deck_id"), "deck_id")
        text(manifest.get("deck_purpose"), "deck_purpose")
        text(manifest.get("visual_tone"), "visual_tone")
        canvas = obj(manifest.get("canvas_inches"), "canvas_inches")
        number(canvas.get("width"), "canvas_inches.width", positive=True)
        number(canvas.get("height"), "canvas_inches.height", positive=True)
        slots = manifest.get("slots")
        need(isinstance(slots, list) and slots, "slots must be a non-empty array")
        slot_ids, round_registry = set(), {}
        for index, raw in enumerate(slots):
            label = f"slots[{index}]"
            try:
                slot = obj(raw, label)
                slot_id = text(slot.get("slot_id"), "slot_id")
                label = slot_id
                need(slot_id not in slot_ids, f"duplicate stable slot_id within deck: {slot_id}")
                slot_ids.add(slot_id)
                slide_number(slot.get("slide_number"), "slide_number")
                for key in ("slide_title", "message", "image_brief"):
                    text(slot.get(key), key)
                state, rejected, accepted, defects = rounds_state(slot, path.parent, round_registry)
                result["slots"].append({"slot_id": slot_id, "slide_number": slot["slide_number"],
                                        "status": state, "engineer_rejected_rounds": rejected,
                                        "next_search_owner": "main" if rejected >= 2 else "engineer"})
                if stage != "progress":
                    handoff, binding = check_handoff(manifest, slot, accepted, path.parent)
                    if stage == "final":
                        check_final(manifest, slot, handoff, binding, defects, path.parent)
            except (Invalid, OSError, ValueError, TypeError, KeyError, ArithmeticError, RecursionError, BadZipFile, ElementTree.ParseError) as exc:
                result["errors"].append(f"{label}: {exc}")
        if not result["errors"]:
            states = [slot["status"] for slot in result["slots"]]
            result["status"] = ("MAIN_SEARCH_REQUIRED" if "MAIN_SEARCH_REQUIRED" in states else
                                "IN_PROGRESS" if "ENGINEER_SEARCH_REQUIRED" in states else "PASS")
    except (Invalid, OSError, ValueError, TypeError, KeyError, ArithmeticError, RecursionError) as exc:
        result["errors"].append(str(exc))
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=STAGES, default="progress")
    args = parser.parse_args(argv)
    result = validate(args.manifest, args.stage)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
