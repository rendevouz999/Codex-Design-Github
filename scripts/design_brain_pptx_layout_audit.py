#!/usr/bin/env python3
"""Read-only PPTX composition evidence. MAIN owns visual originality decisions.

extract <deck.pptx> --deck-id ID; compare <fingerprint.json> --previous <json>
(repeatable); verify <fingerprint-or-report.json>. JSON goes to stdout; only an
explicit --output writes evidence, exclusively unless --overwrite is supplied.
The existing native OOXML loader/walker owns inheritance and group scaling.
No renderer, source mutations, persistent memory, or creative PASS is provided.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
from zipfile import BadZipFile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/presentation-deck/runtime/native"))
from pptx_to_svg.emu_units import NS
from pptx_to_svg.ooxml_loader import OoxmlPackage, inherited_shape_visibility
from pptx_to_svg.shape_walker import walk_sp_tree

FINGERPRINT = "pptx-layout-fingerprint"
REPORT = "pptx-layout-comparison"
LIMITS = ["Outer composition geometry only; text/image/color payloads and crop contents are ignored for matching.",
          "MAIN must review rendered structure, tone and purpose; no automatic visual-originality PASS.",
          "Small plain shapes are potential decoration; table/chart internals and custom paths are not reconstructed.",
          "Local evidence is reproducible and unsigned; canonical cross-session history belongs to Codex-Design local shared memory."]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def data_digest(data, hash_key):
    value = {key: item for key, item in data.items() if key != hash_key}
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def role_of(node):
    if node.kind == "pic":
        return "picture"
    if node.kind == "cxnSp":
        return "connector"
    if node.kind == "graphicFrame":
        uri = node.xml.find("a:graphic/a:graphicData", NS)
        uri = uri.get("uri", "") if uri is not None else ""
        return "table" if uri.endswith("/table") else "chart" if uri.endswith("/chart") else "unknown"
    if node.kind == "sp":
        has_text = any((item.text or "").strip() for item in node.xml.findall("p:txBody//a:t", NS)) or node.xml.find("p:txBody//a:fld", NS) is not None
        return "text" if has_text else "shape"
    return "unknown"


def region_of(box):
    x, y, width, height = box
    return ("left" if x + width / 2 < 0.35 else "right" if x + width / 2 > 0.65 else "center") + "/" + (
        "upper" if y + height / 2 < 0.35 else "lower" if y + height / 2 > 0.65 else "middle")


def content_regions(slide):
    return [shape for shape in slide["shapes"] if shape["region_role"] == "content"]


def relationships(shapes):
    rows = []
    for index, first in enumerate(shapes):
        x, y, width, height = first["box"]
        for second in shapes[index + 1:]:
            xx, yy, ww, hh = second["box"]
            overlap = min(x + width, xx + ww) > max(x, xx) and min(y + height, yy + hh) > max(y, yy)
            rows.append({"from": first["node_id"], "to": second["node_id"], "overlap": overlap,
                         "horizontal": "aligned" if abs(x - xx) < 0.015 else "left" if x < xx else "right",
                         "vertical": "aligned" if abs(y - yy) < 0.015 else "above" if y < yy else "below"})
    return rows


def extract(source, deck_id):
    source = Path(source).resolve()
    need(isinstance(deck_id, str) and bool(deck_id.strip()), "deck_id must be non-empty")
    need(source.is_file() and source.suffix.lower() == ".pptx", "source must be an existing .pptx")
    before = digest(source)
    fingerprint = {"schema_version": 1, "artifact_type": FINGERPRINT, "deck_id": deck_id,
                   "source": {"path": str(source), "sha256": before}, "slides": [], "limits": LIMITS}
    package = OoxmlPackage(source)
    try:
        package.open()
        size = package.presentation.xml.find("p:sldSz", NS)
        need(size is not None and "cx" in size.attrib and "cy" in size.attrib, "actual canvas is missing; native defaults cannot prove it")
        width, height = package.slide_size_px
        need(width > 0 and height > 0, "actual canvas must be positive")
        fingerprint["canvas"] = {"width_emu": package.slide_size_emu[0], "height_emu": package.slide_size_emu[1],
                                 "width_inches": package.slide_size_emu[0] / 914400,
                                 "height_inches": package.slide_size_emu[1] / 914400}
        ids = package.presentation.xml.findall("p:sldIdLst/p:sldId", NS)
        need(0 < len(ids) <= 500, "empty or excessive slide roster")
        need(len(ids) == package.slide_count, "unresolved slide relationship or missing slide part")
        fingerprint["ordered_slide_ids"] = [item.get("id") for item in ids]
        need(all(fingerprint["ordered_slide_ids"]) and len(set(fingerprint["ordered_slide_ids"])) == len(ids), "missing/duplicate native slide IDs")
        for slide in package.iter_slides():
            row = {"slide_number": slide.index, "slide_id": ids[slide.index - 1].get("id"),
                   "part": slide.part.path, "shapes": [], "issues": []}
            visible_layout, visible_master = inherited_shape_visibility(slide)
            parts = [("master", slide.master, visible_master), ("layout", slide.layout, visible_layout),
                     ("slide", slide.part, True)]

            def walk(nodes, origin, part, groups=(), unsupported_group=False):
                for node in nodes:
                    if node.hidden or (origin != "slide" and node.placeholder is not None):
                        continue
                    if node.kind == "grpSp":
                        bad = unsupported_group or bool(node.xfrm.rot or node.xfrm.flip_h or node.xfrm.flip_v)
                        if bad:
                            row["issues"].append("UNSUPPORTED_GROUP_ROTATION_OR_FLIP")
                        if not node.xfrm.ch_w or not node.xfrm.ch_h:
                            row["issues"].append("UNRESOLVED_GROUP_CHILD_FRAME")
                            bad = True
                        walk(node.children, origin, part, (*groups, node.spid), bad)
                        continue
                    geom = node.xfrm
                    values = [geom.x, geom.y, geom.w, geom.h, node.effective_rotation]
                    if not all(math.isfinite(value) for value in values) or geom.w < 0 or geom.h < 0:
                        row["issues"].append("UNKNOWN_GEOMETRY")
                    if geom.w == 0 and geom.h == 0:
                        row["issues"].append("UNRESOLVED_ZERO_GEOMETRY")
                    box = [round(value, 6) for value in (geom.x / width, geom.y / height, geom.w / width, geom.h / height)]
                    role = role_of(node)
                    if role == "unknown":
                        row["issues"].append("UNSUPPORTED_GRAPHIC_OR_SHAPE")
                    preset = node.xml.find("p:spPr/a:prstGeom", NS)
                    form = preset.get("prst", "") if preset is not None else "custom" if node.xml.find("p:spPr/a:custGeom", NS) is not None else node.kind
                    crop = node.xml.find("p:blipFill/a:srcRect", NS)
                    crop = {key: int(crop.get(key, "0")) / 100000 for key in ("l", "t", "r", "b")} if crop is not None else None
                    area = box[2] * box[3]
                    background = area >= 0.9 and box[0] <= 0.01 and box[1] <= 0.01
                    region_role = "background" if background and role == "shape" else "decoration" if role in ("shape", "connector") and area < 0.025 else "content"
                    row["shapes"].append({"node_id": f"n{len(row['shapes']) + 1}", "source_shape_id": node.spid,
                                          "origin": origin, "source_part": part, "group_origin": list(groups),
                                          "z_order": len(row["shapes"]), "role": role, "role_hint": node.placeholder.type if node.placeholder else None,
                                          "form": form, "box": box, "rotation": round(node.effective_rotation, 6),
                                          "flip_h": geom.flip_h, "flip_v": geom.flip_v, "image_crop": crop,
                                          "region_role": region_role, "dominant_region": region_of(box),
                                          "geometry_supported": not unsupported_group})

            for origin, part, visible in parts:
                if part is None or not visible:
                    continue
                # Detect shape-tree children that the native walker would omit.
                tree = part.xml.find("p:cSld/p:spTree", NS)
                if tree is not None:
                    for container in [tree, *tree.findall(".//p:grpSp", NS)]:
                        allowed = {"nvGrpSpPr", "grpSpPr", "sp", "pic", "cxnSp", "grpSp", "graphicFrame", "extLst"}
                        if any(child.tag.split("}")[-1] not in allowed for child in container):
                            row["issues"].append("UNSUPPORTED_SHAPE_TREE_CHILD")
                    for transform in [*tree.findall(".//a:xfrm", NS), *tree.findall(".//p:xfrm", NS)]:
                        for coordinate in transform:
                            if coordinate.tag.split("}")[-1] in ("off", "ext", "chOff", "chExt"):
                                try:
                                    for value in coordinate.attrib.values():
                                        int(value)
                                except ValueError:
                                    row["issues"].append("MALFORMED_TRANSFORM")
                nodes = walk_sp_tree(part.xml, layout_xml=slide.layout.xml if origin == "slide" and slide.layout else None,
                                     master_xml=slide.master.xml if origin == "slide" and slide.master else None)
                walk(nodes, origin, part.path)
            need(len(row["shapes"]) <= 1000, "excessive slide shape roster")
            content = content_regions(row)
            if not content:
                row["issues"].append("EMPTY_OR_NO_STRUCTURAL_REGIONS")
            if any(shape["role"] == "picture" and shape["box"][2] * shape["box"][3] >= 0.9 for shape in content) and not any(shape["role"] == "text" and shape["origin"] == "slide" for shape in content):
                row["issues"].append("POSSIBLY_FLATTENED_SINGLE_PICTURE")
            row["shape_counts"] = dict(Counter(shape["role"] for shape in row["shapes"]))
            row["dominant_regions"] = [shape["node_id"] for shape in sorted(content, key=lambda shape: shape["box"][2] * shape["box"][3], reverse=True)[:3]]
            row["relationships"] = relationships(content)
            row["issues"] = sorted(set(row["issues"]))
            fingerprint["slides"].append(row)
    finally:
        package.close()
    need(before == digest(source), "source changed during extraction")
    fingerprint["status"] = "BLOCKED" if any(slide["issues"] for slide in fingerprint["slides"]) else "EXTRACTED"
    fingerprint["fingerprint_sha256"] = data_digest(fingerprint, "fingerprint_sha256")
    return fingerprint


def load_current_fingerprint(path):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    verify_fingerprint(value)
    return value


def verify_fingerprint(value):
    need(isinstance(value, dict) and value.get("artifact_type") == FINGERPRINT and type(value.get("schema_version")) is int and value["schema_version"] == 1,
         "invalid fingerprint schema")
    need(value.get("fingerprint_sha256") == data_digest(value, "fingerprint_sha256"), "fingerprint evidence hash mismatch")
    source = value.get("source")
    need(isinstance(source, dict) and isinstance(source.get("path"), str) and Path(source["path"]).is_absolute(), "fingerprint source path must be absolute")
    need(digest(source["path"]) == source.get("sha256"), "STALE_SOURCE: fingerprint source hash mismatch")
    # Re-extraction also prevents a structurally edited fingerprint from becoming
    # authoritative merely by recalculating its unsigned JSON digest.
    need(extract(source["path"], value.get("deck_id")) == value, "STALE_FINGERPRINT: does not match current extraction")


def structural_key(shape):
    return (shape["role"], *shape["box"], shape["rotation"])


def exact_signature(slide):
    keys = sorted(structural_key(shape) for shape in slide["shapes"])
    # Only overlapping objects' stacking order affects a visible composition;
    # shape IDs and XML order of disjoint regions cannot prove originality.
    stacking = []
    for index, first in enumerate(slide["shapes"]):
        x, y, w, h = first["box"]
        for second in slide["shapes"][index + 1:]:
            xx, yy, ww, hh = second["box"]
            if min(x + w, xx + ww) > max(x, xx) and min(y + h, yy + hh) > max(y, yy):
                stacking.append((structural_key(first), structural_key(second)))
    return keys, sorted(stacking)


def anchor_key(shape):
    role = "text" if shape["role"] == "text" else "visual"
    return role, round(shape["box"][0] / 0.05), round(shape["box"][1] / 0.05)


def compare_pair(current, previous, current_deck, previous_deck):
    left, right = content_regions(current), content_regions(previous)
    matches, used = [], set()
    for region in left:
        candidates = [(math.hypot(region["box"][0] - other["box"][0], region["box"][1] - other["box"][1]), index, other)
                      for index, other in enumerate(right) if index not in used and anchor_key(region)[0] == anchor_key(other)[0]]
        if candidates:
            distance, index, other = min(candidates, key=lambda item: item[0])
            if distance <= 0.03:
                used.add(index)
                matches.append({"current_node": region["node_id"], "previous_node": other["node_id"],
                                "current_role": region["role"], "previous_role": other["role"],
                                "anchor_distance": round(distance, 6), "current_box": region["box"], "previous_box": other["box"]})
    identical = exact_signature(current) == exact_signature(previous)
    opaque_internals = any(shape["role"] in ("table", "chart") for shape in current["shapes"] + previous["shapes"])
    supported_identical = identical and not opaque_internals
    coarse_same = bool(left and right) and {anchor_key(shape) for shape in left} == {anchor_key(shape) for shape in right}
    blocked = current["issues"] or previous["issues"]
    return {"current": {"deck_id": current_deck["deck_id"], "source": current_deck["source"], "slide_number": current["slide_number"], "slide_id": current["slide_id"]},
            "previous": {"deck_id": previous_deck["deck_id"], "source": previous_deck["source"], "slide_number": previous["slide_number"], "slide_id": previous["slide_id"]},
            "status": "BLOCKED" if blocked else "REJECT_IDENTICAL" if supported_identical else "MAIN_REVIEW_REQUIRED",
            "identical_outer_composition": bool(supported_identical and not blocked),
            "outer_frames_match": bool(identical and not blocked),
            "opaque_table_chart_internals": opaque_internals,
            "likely_repeated_composition": bool(coarse_same and not blocked),
            "highest_matching_regions": sorted(matches, key=lambda match: match["anchor_distance"])[:8],
            "matched_anchor_count": len(matches), "coarse_rule": "Role-family + top-left anchors on a 0.05 normalized grid; ignores size, form and decorative count. A review flag, never a PASS criterion.",
            "issues": sorted(set(current["issues"] + previous["issues"])),
            "reason": "Identical normalized outer roles/boxes/overlap stacking; payload/form swaps do not create a new layout." if supported_identical and not blocked else
                      "Unsupported geometry/evidence blocks structural judgment." if blocked else
                      "Table/chart outer frames cannot establish identical inner composition; MAIN review is required." if opaque_internals else
                      "Likely repeated positional grammar; MAIN must inspect structural change." if coarse_same else
                      "Measured arrangement differs; MAIN still must establish visual/structural originality."}


def compare(current, previous):
    verify_fingerprint(current)
    for old in previous:
        verify_fingerprint(old)
    pairs = [compare_pair(slide, old_slide, current, old) for old in previous
             for slide in current["slides"] for old_slide in old["slides"]]
    blocked = current["status"] == "BLOCKED" or any(old["status"] == "BLOCKED" for old in previous)
    status = "BLOCKED" if blocked else "NO_HISTORY" if not previous else "REJECT_IDENTICAL" if any(pair["status"] == "REJECT_IDENTICAL" for pair in pairs) else "MAIN_REVIEW_REQUIRED"
    result = {"schema_version": 1, "artifact_type": REPORT, "status": status, "design_readiness": "UNVERIFIED",
              "current": current, "previous": previous, "comparisons": pairs, "compared_pair_count": len(pairs),
              "history_scope": "All explicitly supplied previous decks/slides only; Engineer retrieves local-memory cases; MAIN validates actual baseline coverage.", "limits": LIMITS}
    result["report_sha256"] = data_digest(result, "report_sha256")
    return result


def verify_report(value):
    need(isinstance(value, dict), "evidence must be a JSON object")
    if value.get("artifact_type") == FINGERPRINT:
        verify_fingerprint(value)
        return value
    need(value.get("artifact_type") == REPORT and type(value.get("schema_version")) is int and value["schema_version"] == 1, "invalid comparison report schema")
    need(value.get("report_sha256") == data_digest(value, "report_sha256"), "comparison report hash mismatch")
    need(compare(value["current"], value["previous"]) == value, "stale comparison evidence")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("extract", "compare", "verify"):
        command = commands.add_parser(name)
        command.add_argument("input", type=Path)
        command.add_argument("--output", type=Path)
        command.add_argument("--overwrite", action="store_true")
        if name == "extract":
            command.add_argument("--deck-id", required=True)
        elif name == "compare":
            command.add_argument("--previous", type=Path, action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == "extract":
            result = extract(args.input, args.deck_id)
        elif args.command == "compare":
            result = compare(load_current_fingerprint(args.input), [load_current_fingerprint(path) for path in args.previous])
        else:
            result = verify_report(json.loads(args.input.read_text(encoding="utf-8-sig")))
        if args.output:
            output = args.output.resolve()
            forbidden = {args.input.resolve(), *(path.resolve() for path in getattr(args, "previous", []))}
            fingerprints = [result] if result["artifact_type"] == FINGERPRINT else [result["current"], *result["previous"]]
            forbidden.update(Path(item["source"]["path"]).resolve() for item in fingerprints)
            need(output.suffix.lower() == ".json" and output not in forbidden, "output must be a separate .json evidence file; source/input overwrite forbidden")
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("w" if args.overwrite else "x", encoding="utf-8") as handle:
                handle.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, ArithmeticError, RecursionError, BadZipFile) as exc:
        result = {"status": "BLOCKED", "design_readiness": "UNVERIFIED", "errors": [str(exc)], "limits": LIMITS}
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return {"BLOCKED": 1, "REJECT_IDENTICAL": 2, "NO_HISTORY": 3}.get(result["status"], 0)


if __name__ == "__main__":
    raise SystemExit(main())
