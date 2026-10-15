#!/usr/bin/env python
"""Owner balance gate 1 (owner rule, 2026-10-15): grouped slide content must not move under
Arrange > Align > Align Center + Align Middle (relative to the slide).

PowerPoint's Align uses shape frames, so the file-level equivalent is: the union bounding box of
every shape frame on the slide is centred on the slide, horizontally and vertically.

Usage:
  python design_brain_pptx_group_align_check.py <deck.pptx> [--panel N:x0:x1 ...] [--exclude-pictures N ...]
                                                [--tol-pt 0.05] [--json out.json]
  python design_brain_pptx_group_align_check.py --self-check

--panel N:x0:x1      slide N keeps a full-bleed photo; its remaining content is centred vertically on the
                     slide and must sit with equal gaps to the panel edges x0..x1 (units, 960 x 540 basis)
                     instead of the slide edges.
--exclude-pictures N leave picture placeholders out of the union on slide N (the full-bleed photo that
                     defines the panel).
Exit code 0 when every slide passes, 1 otherwise. Units: 960 x 540 (1 unit = 0.75 pt = 9525 EMU).
"""
import argparse
import json
import sys

from pptx import Presentation
from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.util import Emu

EMU_PER_UNIT = 9525
EMU_PER_PT = 12700
RULE = ("owner acceptance test 2026-10-15: grouped slide content must not move under "
        "Arrange > Align > Align Center + Align Middle")


def check_slide(slide, n, width, height, panel, exclude_pictures, tol_emu):
    """Return the receipt row for one slide; verdict PASS, FAIL: ..., or EMPTY."""
    boxes = []
    for sh in slide.shapes:
        if n in exclude_pictures and sh.is_placeholder and sh.placeholder_format.type == PP_PLACEHOLDER.PICTURE:
            continue
        if sh.left is None or sh.width is None:
            continue
        boxes.append((sh.left, sh.top, sh.left + sh.width, sh.top + sh.height, sh.name))
    if not boxes:
        return {"slide": n, "verdict": "EMPTY"}
    l = min(b[0] for b in boxes); t = min(b[1] for b in boxes)
    r = max(b[2] for b in boxes); btm = max(b[3] for b in boxes)
    x0, x1 = panel.get(n, (0, width))
    dx = ((x0 + x1) - (l + r)) / 2      # move Align Center would apply inside the panel (0 = centred)
    dy = (height - (t + btm)) / 2       # move Align Middle would apply on the slide (0 = centred)
    problems = []
    if abs(dx) > tol_emu:
        problems.append(f"Align Center would move it {dx / EMU_PER_PT:+.2f} pt")
    if abs(dy) > tol_emu:
        problems.append(f"Align Middle would move it {dy / EMU_PER_PT:+.2f} pt")
    u = lambda v: round(v / EMU_PER_UNIT, 2)
    extremes = {"top": min(boxes, key=lambda b: b[1])[4], "bottom": max(boxes, key=lambda b: b[3])[4],
                "left": min(boxes, key=lambda b: b[0])[4], "right": max(boxes, key=lambda b: b[2])[4]}
    return {"slide": n, "union_units": {"left": u(l), "top": u(t), "right": u(r), "bottom": u(btm)},
            "panel_units": [u(x0), u(x1)], "align_center_move_pt": round(dx / EMU_PER_PT, 3),
            "align_middle_move_pt": round(dy / EMU_PER_PT, 3), "extreme_shapes": extremes,
            "verdict": "PASS" if not problems else "FAIL: " + "; ".join(problems)}


def check_deck(prs, panel, exclude_pictures, tol_pt):
    tol_emu = tol_pt * EMU_PER_PT
    rows = [check_slide(s, n, prs.slide_width, prs.slide_height, panel, exclude_pictures, tol_emu)
            for n, s in enumerate(prs.slides, 1)]
    status = "PASS" if rows and all(r["verdict"] == "PASS" for r in rows) else "FAIL"
    return rows, status


def self_check():
    """Synthetic deck: a symmetric pair passes, a shifted pair fails, a panel case passes."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(960 * EMU_PER_UNIT), Emu(540 * EMU_PER_UNIT)
    blank = prs.slide_layouts[6]
    U = EMU_PER_UNIT
    s1 = prs.slides.add_slide(blank)                       # centred: 48..912 x 60..480
    s1.shapes.add_textbox(Emu(48 * U), Emu(60 * U), Emu(300 * U), Emu(100 * U))
    s1.shapes.add_textbox(Emu(612 * U), Emu(380 * U), Emu(300 * U), Emu(100 * U))
    s2 = prs.slides.add_slide(blank)                       # 10 units too high, 6 units too far left
    s2.shapes.add_textbox(Emu(42 * U), Emu(50 * U), Emu(300 * U), Emu(100 * U))
    s2.shapes.add_textbox(Emu(612 * U), Emu(370 * U), Emu(300 * U), Emu(100 * U))
    s3 = prs.slides.add_slide(blank)                       # panel 384..960: centred inside it
    s3.shapes.add_textbox(Emu(426 * U), Emu(60 * U), Emu(100 * U), Emu(100 * U))
    s3.shapes.add_textbox(Emu(818 * U), Emu(380 * U), Emu(100 * U), Emu(100 * U))
    rows, status = check_deck(prs, {3: (384 * U, 960 * U)}, [], 0.05)
    assert rows[0]["verdict"] == "PASS", rows[0]
    assert rows[1]["verdict"].startswith("FAIL") and rows[1]["align_middle_move_pt"] == 7.5 \
        and rows[1]["align_center_move_pt"] == 2.25, rows[1]      # 3 units right, 10 units down
    assert rows[2]["verdict"] == "PASS", rows[2]
    assert status == "FAIL"
    print("self-check ok: centred PASS, shifted FAIL (+2.25 / +7.50 pt), panel PASS")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", nargs="?")
    ap.add_argument("--panel", action="append", default=[])
    ap.add_argument("--exclude-pictures", action="append", default=[], type=int)
    ap.add_argument("--tol-pt", type=float, default=0.05)
    ap.add_argument("--json")
    ap.add_argument("--self-check", action="store_true", help="run the built-in synthetic case and exit")
    a = ap.parse_args(argv)
    if a.self_check:
        self_check()
        return 0
    if not a.deck:
        ap.error("deck is required unless --self-check")
    panel = {int(s.split(":")[0]): (float(s.split(":")[1]) * EMU_PER_UNIT, float(s.split(":")[2]) * EMU_PER_UNIT)
             for s in a.panel}
    rows, status = check_deck(Presentation(a.deck), panel, a.exclude_pictures, a.tol_pt)
    print(f"{'slide':6} {'left':>7} {'top':>7} {'right':>7} {'bottom':>7} {'dx_pt':>7} {'dy_pt':>7}  verdict   (units)")
    for r in rows:
        if r["verdict"] == "EMPTY":
            print(f"{r['slide']:06d} empty")
            continue
        ub = r["union_units"]
        print(f"{r['slide']:06d} {ub['left']:7.1f} {ub['top']:7.1f} {ub['right']:7.1f} {ub['bottom']:7.1f} "
              f"{r['align_center_move_pt']:7.2f} {r['align_middle_move_pt']:7.2f}  {r['verdict']}")
    print("overall:", status)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"rule": RULE, "deck": a.deck, "tolerance_pt": a.tol_pt,
                       "panels": {k: [v[0] / EMU_PER_UNIT, v[1] / EMU_PER_UNIT] for k, v in panel.items()},
                       "exclude_pictures": a.exclude_pictures, "slides": rows, "status": status}, fh, indent=2)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
