#!/usr/bin/env python
"""Render and measure presentation-template corpus contact sheets.

This is a visual evidence pass for PowerPoint/Slides/Keynote marketplace
references. It does not pretend to replace human art direction, but it creates
the proof layer Design Brain needs: rendered thumbnails, cluster coverage, and
basic visual-rhythm metrics.
"""

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter, ImageStat

from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command


PYTHON_INVOCATION = resolve_python_invocation()


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render visual contact sheets for a presentation corpus.")
    parser.add_argument("--root", required=True, help="Folder containing template zip files.")
    parser.add_argument("--corpus-json", default="", help="Existing corpus-study JSON. If omitted, inspect root live.")
    parser.add_argument("--output-dir", default="", help="Folder for rendered contact sheets.")
    parser.add_argument("--report", default="", help="Markdown report path.")
    parser.add_argument("--json-output", default="", help="JSON report path.")
    parser.add_argument("--mode", choices=["representative", "all"], default="representative")
    parser.add_argument("--max-samples", type=int, default=36, help="Max samples in representative mode.")
    parser.add_argument("--max-slides", type=int, default=10, help="Max slides rendered per deck.")
    parser.add_argument("--thumb-width", type=int, default=300, help="Contact-sheet thumbnail width.")
    parser.add_argument("--keep-intermediate", action="store_true", help="Keep extracted PPTX/PDF/slide PNGs.")
    parser.add_argument("--timeout", type=int, default=240, help="Seconds allowed for each render.")
    return parser.parse_args()


def slugify(value: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")[:88] or "deck"


def default_paths(args: argparse.Namespace) -> tuple[Path, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = repo_root()
    out_dir = Path(args.output_dir).expanduser() if args.output_dir else root / ".design-brain" / "screenshots" / f"{stamp}-pptx-corpus-visual-study"
    report = Path(args.report).expanduser() if args.report else root / ".design-brain" / "reference-insights" / f"{stamp}-presentation-template-visual-study.md"
    json_out = Path(args.json_output).expanduser() if args.json_output else report.with_suffix(".json")
    if not out_dir.is_absolute():
        out_dir = Path.cwd() / out_dir
    if not report.is_absolute():
        report = Path.cwd() / report
    if not json_out.is_absolute():
        json_out = Path.cwd() / json_out
    return out_dir.resolve(), report.resolve(), json_out.resolve()


def load_or_build_corpus(root: Path, corpus_json: str) -> dict[str, Any]:
    if corpus_json:
        path = Path(corpus_json).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return json.loads(path.read_text(encoding="utf-8"))

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from design_brain_pptx_corpus_study import inspect_outer_zip, summarize  # type: ignore

    records = [inspect_outer_zip(path) for path in sorted(root.glob("*.zip"))]
    return {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "root": str(root),
        "summary": summarize(records),
        "records": records,
    }


def best_deck(record: dict[str, Any]) -> dict[str, Any] | None:
    decks = [deck for deck in record.get("decks", []) if deck.get("valid")]
    if not decks:
        return None
    return max(
        decks,
        key=lambda deck: (
            deck.get("layoutCount", 0),
            deck.get("slideCount", 0),
            deck.get("mediaCount", 0),
            deck.get("chartCount", 0),
        ),
    )


def record_score(record: dict[str, Any]) -> float:
    deck = best_deck(record)
    if not deck:
        return -1
    return (
        deck.get("layoutCount", 0) * 3
        + deck.get("slideCount", 0)
        + deck.get("mediaCount", 0) * 0.5
        + deck.get("chartCount", 0) * 2
        + deck.get("masterCount", 0) * 4
    )


def select_best_for_cluster(records: list[dict[str, Any]], key: str, cluster: str, selected: set[str]) -> dict[str, Any] | None:
    candidates = [
        record
        for record in records
        if record.get("zip") not in selected and cluster in record.get(key, []) and best_deck(record)
    ]
    if not candidates:
        return None
    return max(candidates, key=record_score)


def select_records(records: list[dict[str, Any]], mode: str, max_samples: int) -> list[dict[str, Any]]:
    eligible = [record for record in records if best_deck(record)]
    if mode == "all":
        return eligible

    selected: list[dict[str, Any]] = []
    selected_names: set[str] = set()

    market_counts = Counter(cluster for record in eligible for cluster in record.get("marketClusters", []))
    mood_counts = Counter(cluster for record in eligible for cluster in record.get("moodClusters", []))

    for key, counts in [("marketClusters", market_counts), ("moodClusters", mood_counts)]:
        for cluster, _count in counts.most_common():
            if len(selected) >= max_samples:
                break
            record = select_best_for_cluster(eligible, key, cluster, selected_names)
            if record:
                selected.append(record)
                selected_names.add(record["zip"])

    for record in sorted(eligible, key=record_score, reverse=True):
        if len(selected) >= max_samples:
            break
        if record["zip"] in selected_names:
            continue
        selected.append(record)
        selected_names.add(record["zip"])

    return selected


def render_record(
    record: dict[str, Any],
    root: Path,
    output_dir: Path,
    max_slides: int,
    thumb_width: int,
    timeout: int,
) -> dict[str, Any]:
    zip_path = root / record["zip"]
    sample_dir = output_dir / slugify(zip_path.stem)
    render_script = repo_root() / "scripts" / "design_brain_pptx_render_contact_sheet.py"
    command = py_command(
        [
            str(render_script),
            "--input",
            str(zip_path),
            "--output-dir",
            str(sample_dir),
            "--max-slides",
            str(max_slides),
            "--thumb-width",
            str(thumb_width),
            "--json",
        ]
    )
    proc = run_process_command(command, cwd=repo_root(), timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"render failed for {record['zip']}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return json.loads(proc.stdout)


def normalized_histogram(gray: Image.Image) -> list[float]:
    hist = gray.histogram()
    buckets = 32
    step = len(hist) // buckets
    values = [sum(hist[index : index + step]) for index in range(0, len(hist), step)]
    total = sum(values) or 1
    return [value / total for value in values[:buckets]]


def slide_metrics(slide_paths: list[str]) -> dict[str, Any]:
    per_slide = []
    histograms: list[list[float]] = []
    for path_value in slide_paths:
        path = Path(path_value)
        if not path.exists():
            continue
        with Image.open(path) as image:
            image = image.convert("RGB")
            image.thumbnail((480, 270))
            gray = image.convert("L")
            hsv = image.convert("HSV")
            saturation = hsv.getchannel("S")
            edges = gray.filter(ImageFilter.FIND_EDGES)
            lum = ImageStat.Stat(gray)
            sat = ImageStat.Stat(saturation)
            edge = ImageStat.Stat(edges)
            hist = normalized_histogram(gray)
            histograms.append(hist)
            per_slide.append(
                {
                    "slide": path.name,
                    "luminance": round(lum.mean[0], 2),
                    "contrast": round(lum.stddev[0], 2),
                    "saturation": round(sat.mean[0], 2),
                    "edgeDensity": round(edge.mean[0], 2),
                }
            )
    if not per_slide:
        return {"slideMetrics": [], "interpretation": ["no rendered slides available"]}

    def avg(key: str) -> float:
        return round(sum(item[key] for item in per_slide) / len(per_slide), 2)

    adjacent = []
    for left, right in zip(histograms, histograms[1:]):
        adjacent.append(sum(abs(a - b) for a, b in zip(left, right)))
    luminance_values = [item["luminance"] for item in per_slide]
    edge_values = [item["edgeDensity"] for item in per_slide]
    aggregate = {
        "slideMetrics": per_slide,
        "avgLuminance": avg("luminance"),
        "avgContrast": avg("contrast"),
        "avgSaturation": avg("saturation"),
        "avgEdgeDensity": avg("edgeDensity"),
        "luminanceRange": round(max(luminance_values) - min(luminance_values), 2),
        "densityRange": round(max(edge_values) - min(edge_values), 2),
        "thumbnailRhythm": round(sum(adjacent) / len(adjacent), 4) if adjacent else 0.0,
    }
    aggregate["interpretation"] = interpret_metrics(aggregate)
    return aggregate


def interpret_metrics(metrics: dict[str, Any]) -> list[str]:
    notes = []
    lum = metrics["avgLuminance"]
    sat = metrics["avgSaturation"]
    contrast = metrics["avgContrast"]
    edge = metrics["avgEdgeDensity"]
    rhythm = metrics["thumbnailRhythm"]
    lum_range = metrics["luminanceRange"]

    if lum < 95:
        notes.append("dark high-contrast base")
    elif lum > 188:
        notes.append("light/clean base")
    else:
        notes.append("mixed mid-tone base")

    if sat > 72:
        notes.append("high accent/color energy")
    elif sat < 34:
        notes.append("restrained color energy")
    else:
        notes.append("moderate color energy")

    if contrast > 70:
        notes.append("strong visual separation")
    elif contrast < 45:
        notes.append("soft visual separation")

    if edge > 27:
        notes.append("dense/detail-heavy thumbnails")
    elif edge < 16:
        notes.append("quiet/simple thumbnails")

    if rhythm > 0.36 or lum_range > 90:
        notes.append("varied thumbnail rhythm")
    elif rhythm < 0.18 and lum_range < 45:
        notes.append("monotony risk in thumbnail view")
    return notes


def compact_render(summary: dict[str, Any]) -> None:
    for file_key in ["pptx", "pdf"]:
        path = Path(summary.get(file_key, ""))
        if path.exists():
            path.unlink()
    slide_paths = [Path(path) for path in summary.get("slides", [])]
    if slide_paths:
        slide_dir = slide_paths[0].parent
        if slide_dir.exists():
            shutil.rmtree(slide_dir)


def cluster_coverage(samples: list[dict[str, Any]], key: str) -> Counter[str]:
    return Counter(cluster for sample in samples for cluster in sample["record"].get(key, []))


def table_rows(samples: list[dict[str, Any]]) -> str:
    lines = [
        "| # | Reference | Market | Mood | Slides/layouts | Visual signals | Contact sheet |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for index, sample in enumerate(samples, 1):
        record = sample["record"]
        deck = best_deck(record) or {}
        signals = ", ".join(sample.get("metrics", {}).get("interpretation", [])[:3])
        contact = sample.get("render", {}).get("contactSheet", "")
        contact_text = contact.replace("\\", "/") if contact else "render failed"
        lines.append(
            f"| {index} | {record['zip']} | {', '.join(record.get('marketClusters', []))} | "
            f"{', '.join(record.get('moodClusters', []))} | {deck.get('slideCount', 0)}/{deck.get('layoutCount', 0)} | "
            f"{signals} | `{contact_text}` |"
        )
    return "\n".join(lines)


def build_report(root: Path, data: dict[str, Any], samples: list[dict[str, Any]], failures: list[dict[str, str]]) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    rendered = [sample for sample in samples if "render" in sample]
    market = cluster_coverage(rendered, "marketClusters")
    mood = cluster_coverage(rendered, "moodClusters")
    rhythm_values = [sample["metrics"].get("thumbnailRhythm", 0) for sample in rendered if sample.get("metrics")]
    avg_rhythm = round(sum(rhythm_values) / len(rhythm_values), 4) if rhythm_values else 0
    return f"""# Presentation Template Visual Corpus Study

Generated: {now}

Root: `{root}`

## Scope

- Corpus zip packages: {data.get('summary', {}).get('zipCount', 'unknown')}
- Readable PPTX decks in corpus: {data.get('summary', {}).get('pptxDeckCount', 'unknown')}
- Rendered visual samples: {len(rendered)}
- Render failures: {len(failures)}
- Average thumbnail rhythm score: {avg_rhythm}

## Rendered Samples

{table_rows(rendered)}

## Cluster Coverage In This Visual Pass

### Market

```json
{json.dumps(dict(market.most_common()), indent=2, ensure_ascii=False)}
```

### Mood

```json
{json.dumps(dict(mood.most_common()), indent=2, ensure_ascii=False)}
```

## What This Visual Pass Teaches

1. Study decks as contact-sheet rhythm first. A strong template is readable as a set of slide silhouettes, not only as isolated full-size slides.
2. Dark business and gradient decks need stricter originality checks because the corpus has many similar high-contrast marketplace patterns.
3. Light/clean decks often rely on grid precision and typography confidence; they fail easily when alignment, title hierarchy, or image crop becomes loose.
4. Editorial/portfolio/architecture samples are useful for learning visual silence, asymmetry, and crop-led rhythm that can make future decks feel less generic.
5. Corporate/project proposal samples are useful for learning layout completeness, but they need reinterpretation so future decks do not repeat title/content/card-grid patterns.
6. Thumbnail monotony is a real risk. Future template design should intentionally alternate statement, divider, data, image, comparison, and rest slides.
7. Template usability should be judged after visual review: long titles, extra bullets, portrait/landscape image replacement, logo color swaps, and chart data changes must remain stable.

## How To Reuse These References Safely

- Use the rendered contact sheets as evidence for mood, pace, density, and role variety.
- Do not copy cover composition, slide order, color-role mapping, title/image placement, motifs, chart treatment, or divider logic.
- Extract one lesson per cluster, then rebuild a new slide-role matrix with a different order and different composition grammar.
- For future Figma Slides or PPTX design, start from master/layout rules, safe margins, type scale, chart/table rules, footer logic, and thumbnail rhythm before styling.

## Render Failures

```json
{json.dumps(failures, indent=2, ensure_ascii=False)}
```
"""


def main() -> int:
    configure_stdout()
    args = parse_args()
    corpus_root = Path(args.root).expanduser().resolve()
    output_dir, report_path, json_path = default_paths(args)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    corpus = load_or_build_corpus(corpus_root, args.corpus_json)
    records = corpus.get("records", [])
    selected = select_records(records, args.mode, args.max_samples)
    samples: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for record in selected:
        sample = {"record": record}
        try:
            render = render_record(record, corpus_root, output_dir, args.max_slides, args.thumb_width, args.timeout)
            metrics = slide_metrics(render.get("slides", []))
            sample["render"] = render
            sample["metrics"] = metrics
            if not args.keep_intermediate:
                compact_render(render)
        except Exception as exc:  # noqa: BLE001 - corpus render pass should continue.
            failures.append({"zip": record.get("zip", "unknown"), "error": str(exc)})
            sample["error"] = str(exc)
        samples.append(sample)
        print(f"[{len(samples)}/{len(selected)}] {record.get('zip')} -> {'OK' if 'render' in sample else 'FAILED'}", flush=True)

    output = {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "root": str(corpus_root),
        "outputDir": str(output_dir),
        "mode": args.mode,
        "maxSlides": args.max_slides,
        "samples": samples,
        "failures": failures,
    }
    json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    report_path.write_text(build_report(corpus_root, corpus, samples, failures), encoding="utf-8", newline="\n")
    print(f"Visual corpus report written: {report_path}", flush=True)
    print(f"Visual corpus JSON written: {json_path}", flush=True)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
