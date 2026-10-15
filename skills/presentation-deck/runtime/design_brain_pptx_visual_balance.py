#!/usr/bin/env python
"""Owner balance gate 2 (owner rule, 2026-10-15): the visible design block of every slide must be centred
on the canvas (gap above == gap below), measured from rendered shape edges and glyphs on native renders,
never from text-box frames. The owner centres by moving the whole block as one group; sizes never change,
so --top/--bottom are optional extra targets.

Usage:
  python design_brain_pptx_visual_balance.py <render_dir> [--side 48] [--tol 2] [--top 25] [--bottom 515]
                                             [--ignore N:x0:y0:x1:y1 ...] [--left N:x ...] [--right N:gap ...]
                                             [--tol-slide N:units ...] [--threshold 8] [--json out.json]
  python design_brain_pptx_visual_balance.py --self-check

<render_dir> holds one PNG per slide (render_powerpoint.ps1 naming slide-NNN.png); the slide number is
the digits in the file name. Exit code 0 when every slide passes, 1 otherwise. Units: 960 x 540 (1 unit = 0.75 pt).
"""
import argparse
import collections
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

RULE = ("visible design block centred on the canvas by moving it as one group: gap above == gap below, "
        "measured from rendered edges, sizes unchanged (owner, 2026-10-15)")


def measure(im, ignore_regions=(), threshold=8):
    """Rendered extents in 960 x 540 units: (top, bottom, left, right_gap, background) or None when empty.
    Background = most common border colour; a row/column counts when more than one pixel differs from it,
    so a one-unit hairline (2 px at 1920 wide) counts and a lone anti-aliased pixel does not."""
    px = np.asarray(im.convert("RGB")).astype(int)
    H, W, _ = px.shape
    sx, sy = 960 / W, 540 / H
    border = np.concatenate([px[0], px[-1], px[:, 0], px[:, -1]])
    bg = collections.Counter(map(tuple, border)).most_common(1)[0][0]
    m = np.abs(px - np.array(bg)).max(axis=2) > threshold
    for x0, y0, x1, y1 in ignore_regions:
        m[int(y0 / sy):int(y1 / sy), int(x0 / sx):int(x1 / sx)] = False
    rows = np.where(m.sum(axis=1) > 1)[0]
    cols = np.where(m.sum(axis=0) > 1)[0]
    if len(rows) == 0:
        return None
    return rows.min() * sy, (rows.max() + 1) * sy, cols.min() * sx, 960 - (cols.max() + 1) * sx, bg


def judge(n, extents, a, left_target, right_target, tol_slide, ignore):
    if extents is None:
        return {"slide": n, "verdict": "EMPTY"}
    top, bot, left, right, bg = extents
    gap_t, gap_b = top, 540 - bot
    tol = max(a.tol, tol_slide.get(n, 0))
    want_l, want_r = left_target.get(n, a.side), right_target.get(n, a.side)
    problems = []
    if a.top is not None and abs(top - a.top) > tol:
        problems.append(f"top {top:.1f} != {a.top}")
    if a.bottom is not None and abs(bot - a.bottom) > tol:
        problems.append(f"bottom {bot:.1f} != {a.bottom}")
    if abs(gap_t - gap_b) > tol:
        problems.append(f"gaps {gap_t:.1f}/{gap_b:.1f} not equal")
    if abs(left - want_l) > tol:
        problems.append(f"left {left:.1f} != {want_l}")
    if abs(right - want_r) > tol:
        problems.append(f"right {right:.1f} != {want_r}")
    if problems:
        verdict = "FAIL: " + "; ".join(problems)
    else:
        verdict = "PASS" if n not in tol_slide else f"PASS (allowance {tol_slide[n]:g} units)"
    return {"slide": n, "background": "#%02X%02X%02X" % bg, "top": round(top, 1), "bottom": round(bot, 1),
            "gap_top": round(gap_t, 1), "gap_bottom": round(gap_b, 1), "left": round(left, 1), "right": round(right, 1),
            "ignored": ignore, "tolerance_used": tol, "verdict": verdict}


def self_check():
    """Synthetic renders: centred block passes, a 10-unit-high block fails, a hairline counts as content."""
    from PIL import ImageDraw

    def render(y0, y1, hairline=None):
        im = Image.new("RGB", (1920, 1080), (255, 255, 255))
        d = ImageDraw.Draw(im)
        d.rectangle((96, y0 * 2, 1823, y1 * 2 - 1), fill=(30, 30, 30))       # 48..912 units wide
        if hairline is not None:
            d.line((96, hairline * 2, 1823, hairline * 2), fill=(200, 200, 200), width=2)
        return im

    class A:
        top = bottom = None
        side = 48.0
        tol = 2.0

    ok = judge(1, measure(render(100, 440)), A, {}, {}, {}, [])
    assert ok["verdict"] == "PASS" and ok["gap_top"] == 100 and ok["gap_bottom"] == 100 and ok["left"] == 48, ok
    bad = judge(2, measure(render(90, 440)), A, {}, {}, {}, [])
    assert bad["verdict"].startswith("FAIL") and "gaps 90.0/100.0" in bad["verdict"], bad
    line = judge(3, measure(render(100, 440, hairline=60)), A, {}, {}, {}, [])
    assert line["top"] == 60 and line["verdict"].startswith("FAIL"), line
    assert measure(Image.new("RGB", (1920, 1080), (255, 255, 255))) is None
    print("self-check ok: centred PASS, 10 units high FAIL, hairline counted, empty render detected")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render_dir", nargs="?")
    ap.add_argument("--top", type=float, default=None, help="optional target visible top edge")
    ap.add_argument("--bottom", type=float, default=None, help="optional target visible bottom edge")
    ap.add_argument("--left", action="append", default=[],
                    help="slide:value expected left edge (e.g. 1:426 for a cover whose block starts right of a full-bleed photo)")
    ap.add_argument("--right", action="append", default=[],
                    help="slide:value expected right gap (e.g. 1:42 when the cover block is centred in the panel beside the photo)")
    ap.add_argument("--tol-slide", action="append", default=[],
                    help="slide:units documented allowance for that slide only (e.g. 14:4 for PowerPoint chart-space padding below axis labels); the JSON records it")
    ap.add_argument("--side", type=float, default=48.0)
    ap.add_argument("--tol", type=float, default=2.0)
    ap.add_argument("--threshold", type=int, default=8, help="max channel distance from the background that counts as design")
    ap.add_argument("--ignore", action="append", default=[], help="slide:x0:y0:x1:y1 region to ignore (full-bleed photo)")
    ap.add_argument("--json")
    ap.add_argument("--self-check", action="store_true", help="run the built-in synthetic case and exit")
    a = ap.parse_args(argv)
    if a.self_check:
        self_check()
        return 0
    if not a.render_dir:
        ap.error("render_dir is required unless --self-check")
    ignore = collections.defaultdict(list)
    for spec in a.ignore:
        n, x0, y0, x1, y1 = spec.split(":")
        ignore[int(n)].append(tuple(float(v) for v in (x0, y0, x1, y1)))
    left_target = {int(s.split(":")[0]): float(s.split(":")[1]) for s in a.left}
    right_target = {int(s.split(":")[0]): float(s.split(":")[1]) for s in a.right}
    tol_slide = {int(s.split(":")[0]): float(s.split(":")[1]) for s in a.tol_slide}
    rows_out = []
    print(f"{'slide':6} {'bg':8} {'top':>6} {'bottom':>7} {'gapT':>6} {'gapB':>6} {'left':>6} {'right':>6}  verdict")
    for f in sorted(glob.glob(os.path.join(a.render_dir, "*.png"))):
        n = int("".join(ch for ch in os.path.basename(f) if ch.isdigit()) or 0)
        r = judge(n, measure(Image.open(f), ignore[n], a.threshold), a, left_target, right_target, tol_slide, ignore[n])
        rows_out.append(r)
        if r["verdict"] == "EMPTY":
            print(f"{n:06d} empty")
            continue
        print(f"{n:06d} {r['background']} {r['top']:6.1f} {r['bottom']:7.1f} {r['gap_top']:6.1f} {r['gap_bottom']:6.1f} "
              f"{r['left']:6.1f} {r['right']:6.1f}  {r['verdict']}")
    status = "PASS" if rows_out and all(r["verdict"].startswith("PASS") for r in rows_out) else "FAIL"
    print("overall:", status)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"rule": RULE,
                       "targets": {"top": a.top, "bottom": a.bottom, "side": a.side, "left_overrides": left_target,
                                   "right_overrides": right_target, "slide_allowances": tol_slide, "tolerance": a.tol,
                                   "threshold": a.threshold},
                       "render_dir": os.path.abspath(a.render_dir), "slides": rows_out, "status": status}, fh, indent=2)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
