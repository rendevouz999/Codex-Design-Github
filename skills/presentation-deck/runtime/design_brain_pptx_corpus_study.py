#!/usr/bin/env python
"""Study a folder of zipped PPTX/Slides/Keynote marketplace templates."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


TEXT_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"
LATIN_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}latin"
CSLD_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}cSld"
SLD_SZ_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz"

MARKET_CLUSTERS = {
    "tech_ai_cyber": ["technology", "tech", "ai", "artificial", "cyber", "digital", "transformation"],
    "corporate_business": ["business", "company", "corporate", "project", "proposal", "sales", "strategy", "management"],
    "startup_pitch": ["startup", "pitch", "pitchdeck", "pitch-deck", "investment", "plan"],
    "creative_agency": ["creative", "agency", "marketing", "studio"],
    "brand_portfolio": ["brand", "branding", "portfolio", "portofolio", "showcase", "fashion", "streetwear"],
    "architecture_interiors": ["architecture", "building", "interior", "furniture", "catalogue", "catalog"],
    "education_social": ["education", "school", "pre-school", "pta", "event", "non-profit", "campaign", "leaders", "opinion"],
    "food_health_lifestyle": ["food", "beverages", "restaurant", "nutrition", "diet", "gym", "fitness", "pet", "veterinary", "psychology", "counseling"],
    "sustainability": ["sustainable", "agriculture", "green", "zero-waste", "healthy"],
}

MOOD_CLUSTERS = {
    "black_dark_high_contrast": ["black", "dark"],
    "white_clean": ["white", "clean", "simple"],
    "cream_beige_warm_editorial": ["cream", "beige", "brown", "terracota"],
    "blue_corporate": ["blue", "navy"],
    "green_natural": ["green", "lime", "agriculture", "healthy"],
    "orange_yellow_energy": ["orange", "yellow"],
    "purple_pink_gradient": ["purple", "pink", "gradient"],
    "retro_brutalism": ["retro", "brutalism", "neo-brutalism"],
    "monochrome_editorial": ["monochrome", "black-white", "white-black"],
}

ROLE_KEYWORDS = {
    "cover": ["cover", "title", "welcome"],
    "agenda": ["agenda", "table of content", "contents", "overview"],
    "about": ["about", "company", "profile", "who we are"],
    "problem": ["problem", "challenge", "issue", "opportunity"],
    "solution": ["solution", "services", "offer", "approach"],
    "features": ["feature", "capability", "benefit"],
    "market": ["market", "audience", "customer", "segment"],
    "process": ["process", "workflow", "how it works"],
    "timeline": ["timeline", "roadmap", "milestone"],
    "stats": ["stat", "metric", "number", "achievement", "growth"],
    "chart_table": ["chart", "table", "financial", "revenue", "data"],
    "comparison": ["comparison", "competitor", "versus", "strategy"],
    "case_study": ["case", "portfolio", "project"],
    "team": ["team", "member", "founder"],
    "pricing": ["pricing", "package", "rate"],
    "testimonial": ["testimonial", "quote", "client"],
    "contact": ["contact", "thank", "closing", "next step"],
}


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Study zipped presentation-template corpus.")
    parser.add_argument("--root", required=True, help="Folder containing template zip files.")
    parser.add_argument("--output", default="", help="Optional markdown report path.")
    parser.add_argument("--json-output", default="", help="Optional JSON data path.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max zip files to inspect.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def slug_tokens(name: str) -> set[str]:
    normalized = name.lower().replace("_", "-")
    return {part for part in re.split(r"[^a-z0-9]+", normalized) if part}


def classify(name: str, clusters: dict[str, list[str]], fallback: str) -> list[str]:
    lowered = name.lower()
    result = []
    for cluster, keywords in clusters.items():
        if any(keyword in lowered for keyword in keywords):
            result.append(cluster)
    return result or [fallback]


def platform_tags(name: str, inner_names: list[str]) -> list[str]:
    lowered = " ".join([name, *inner_names]).lower()
    tags = []
    for tag, keywords in {
        "powerpoint": [".pptx", ".ppt", "powerpoint", "ppt "],
        "google_slides": ["google slide", "google slides", "gsl"],
        "keynote": [".key", "keynote"],
        "pdf_docs": [".pdf"],
    }.items():
        if any(keyword in lowered for keyword in keywords):
            tags.append(tag)
    return tags or ["unknown"]


def natural_key(value: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", value)
    return (int(match.group(1)) if match else 0, value)


def extract_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    values = [node.text or "" for node in root.iter(TEXT_NS)]
    return " ".join(part.strip() for part in values if part and part.strip())


def extract_theme_fonts(theme_xml: bytes) -> list[str]:
    try:
        root = ET.fromstring(theme_xml)
    except ET.ParseError:
        return []
    fonts = []
    for node in root.iter(LATIN_NS):
        face = node.attrib.get("typeface")
        if face and face not in fonts:
            fonts.append(face)
    return fonts


def extract_layout_names(archive: zipfile.ZipFile, names: list[str]) -> list[str]:
    result = []
    for path in sorted([name for name in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", name)], key=natural_key):
        try:
            root = ET.fromstring(archive.read(path))
        except ET.ParseError:
            continue
        node = root.find(f".//{CSLD_NS}")
        if node is not None:
            layout_name = node.attrib.get("name", "").strip()
            if layout_name:
                result.append(layout_name)
    return result


def slide_size(archive: zipfile.ZipFile) -> str:
    try:
        root = ET.fromstring(archive.read("ppt/presentation.xml"))
    except (KeyError, ET.ParseError):
        return "unknown"
    node = root.find(f".//{SLD_SZ_NS}")
    if node is None:
        return "unknown"
    try:
        cx = int(node.attrib.get("cx", "0"))
        cy = int(node.attrib.get("cy", "0"))
    except ValueError:
        return "unknown"
    ratio = cx / cy if cy else 0
    if 1.72 <= ratio <= 1.82:
        return "16:9"
    if 1.30 <= ratio <= 1.40:
        return "4:3"
    return f"{cx}:{cy}"


def inspect_pptx_bytes(data: bytes) -> dict[str, Any]:
    try:
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            names = archive.namelist()
            slide_paths = sorted(
                [name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)],
                key=natural_key,
            )
            layout_paths = [name for name in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", name)]
            master_paths = [name for name in names if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", name)]
            media_paths = [name for name in names if name.startswith("ppt/media/")]
            chart_paths = [name for name in names if re.match(r"ppt/charts/chart\d+\.xml$", name)]
            notes_paths = [name for name in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)]
            theme_paths = [name for name in names if re.match(r"ppt/theme/theme\d+\.xml$", name)]
            slide_texts = []
            text_lengths = []
            role_hits: Counter[str] = Counter()
            for slide_path in slide_paths:
                text = extract_text(archive.read(slide_path))
                slide_texts.append(text[:260])
                text_lengths.append(len(text))
                lowered = text.lower()
                for role, keywords in ROLE_KEYWORDS.items():
                    if any(keyword in lowered for keyword in keywords):
                        role_hits[role] += 1
            fonts = []
            for theme_path in theme_paths[:3]:
                fonts.extend(extract_theme_fonts(archive.read(theme_path)))
            fonts = list(dict.fromkeys(fonts))
            return {
                "valid": True,
                "slideCount": len(slide_paths),
                "layoutCount": len(layout_paths),
                "masterCount": len(master_paths),
                "mediaCount": len(media_paths),
                "chartCount": len(chart_paths),
                "notesCount": len(notes_paths),
                "themeCount": len(theme_paths),
                "slideSize": slide_size(archive),
                "layoutNames": extract_layout_names(archive, names)[:24],
                "themeFonts": fonts[:12],
                "avgTextLength": round(statistics.mean(text_lengths), 1) if text_lengths else 0,
                "maxTextLength": max(text_lengths) if text_lengths else 0,
                "roleHits": dict(role_hits.most_common()),
                "textSamples": [text for text in slide_texts if text][:5],
            }
    except zipfile.BadZipFile:
        return {"valid": False, "error": "PPTX is not readable as zip."}


def inspect_outer_zip(path: Path) -> dict[str, Any]:
    record: dict[str, Any] = {
        "zip": path.name,
        "sizeBytes": path.stat().st_size,
        "marketClusters": classify(path.name, MARKET_CLUSTERS, "general_business"),
        "moodClusters": classify(path.name, MOOD_CLUSTERS, "neutral_marketplace"),
        "innerFileCount": 0,
        "pptxFiles": [],
        "pptFiles": [],
        "keyFiles": [],
        "pdfFiles": [],
        "readmeFiles": [],
        "imageFiles": [],
        "platformTags": [],
        "decks": [],
        "errors": [],
    }
    try:
        with zipfile.ZipFile(path) as outer:
            names = outer.namelist()
            record["innerFileCount"] = len(names)
            record["pptxFiles"] = [name for name in names if name.lower().endswith(".pptx")]
            record["pptFiles"] = [name for name in names if name.lower().endswith(".ppt")]
            record["keyFiles"] = [name for name in names if name.lower().endswith(".key")]
            record["pdfFiles"] = [name for name in names if name.lower().endswith(".pdf")]
            record["readmeFiles"] = [name for name in names if "read" in name.lower() and name.lower().endswith((".txt", ".md"))]
            record["imageFiles"] = [name for name in names if name.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
            record["platformTags"] = platform_tags(path.name, names)
            for pptx in record["pptxFiles"][:4]:
                try:
                    data = outer.read(pptx)
                    deck = inspect_pptx_bytes(data)
                    deck["path"] = pptx
                    record["decks"].append(deck)
                except Exception as exc:  # noqa: BLE001 - corpus study should keep going.
                    record["errors"].append(f"{pptx}: {exc}")
    except zipfile.BadZipFile:
        record["errors"].append("Outer zip is not readable.")
    return record


def safe_avg(values: list[int | float]) -> float:
    return round(statistics.mean(values), 1) if values else 0.0


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    decks = [deck for record in records for deck in record["decks"] if deck.get("valid")]
    market_counts: Counter[str] = Counter()
    mood_counts: Counter[str] = Counter()
    platform_counts: Counter[str] = Counter()
    role_counts: Counter[str] = Counter()
    layout_name_counts: Counter[str] = Counter()
    font_counts: Counter[str] = Counter()
    for record in records:
        market_counts.update(record["marketClusters"])
        mood_counts.update(record["moodClusters"])
        platform_counts.update(record["platformTags"])
        for deck in record["decks"]:
            role_counts.update(deck.get("roleHits", {}))
            layout_name_counts.update(deck.get("layoutNames", []))
            font_counts.update(deck.get("themeFonts", []))
    return {
        "zipCount": len(records),
        "pptxDeckCount": len(decks),
        "pptLegacyCount": sum(len(record["pptFiles"]) for record in records),
        "keyFileCount": sum(len(record["keyFiles"]) for record in records),
        "pdfDocCount": sum(len(record["pdfFiles"]) for record in records),
        "avgZipSizeMB": round(safe_avg([record["sizeBytes"] for record in records]) / 1_000_000, 2),
        "avgSlides": safe_avg([deck["slideCount"] for deck in decks]),
        "avgLayouts": safe_avg([deck["layoutCount"] for deck in decks]),
        "avgMasters": safe_avg([deck["masterCount"] for deck in decks]),
        "avgMedia": safe_avg([deck["mediaCount"] for deck in decks]),
        "avgCharts": safe_avg([deck["chartCount"] for deck in decks]),
        "marketCounts": dict(market_counts.most_common()),
        "moodCounts": dict(mood_counts.most_common()),
        "platformCounts": dict(platform_counts.most_common()),
        "roleSignalCounts": dict(role_counts.most_common(20)),
        "commonLayoutNames": dict(layout_name_counts.most_common(24)),
        "commonThemeFonts": dict(font_counts.most_common(20)),
    }


def examples_for(records: list[dict[str, Any]], key: str, value: str, limit: int = 4) -> list[str]:
    result = []
    for record in records:
        if value in record.get(key, []):
            result.append(record["zip"])
        if len(result) >= limit:
            break
    return result


def md_table(counts: dict[str, int], records: list[dict[str, Any]], record_key: str) -> str:
    lines = ["| Cluster | Count | Examples |", "| --- | ---: | --- |"]
    for cluster, count in counts.items():
        examples = "; ".join(examples_for(records, record_key, cluster, 3))
        lines.append(f"| {cluster} | {count} | {examples} |")
    return "\n".join(lines)


def technical_ranges(records: list[dict[str, Any]]) -> str:
    decks = []
    for record in records:
        for deck in record["decks"]:
            if deck.get("valid"):
                decks.append((record["zip"], deck))
    top_slides = sorted(decks, key=lambda item: item[1].get("slideCount", 0), reverse=True)[:8]
    top_layouts = sorted(decks, key=lambda item: item[1].get("layoutCount", 0), reverse=True)[:8]
    lines = ["### Largest Slide Counts", ""]
    lines.extend(f"- {name}: {deck.get('slideCount', 0)} slides, {deck.get('layoutCount', 0)} layouts" for name, deck in top_slides)
    lines.extend(["", "### Largest Layout Systems", ""])
    lines.extend(f"- {name}: {deck.get('layoutCount', 0)} layouts, {deck.get('slideCount', 0)} slides" for name, deck in top_layouts)
    return "\n".join(lines)


def build_markdown(root: Path, records: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    return f"""# Presentation Template Corpus Study

Generated: {now}

Root: `{root}`

## Corpus Scope

- Zip packages studied: {summary['zipCount']}
- Readable PPTX decks found: {summary['pptxDeckCount']}
- Legacy `.ppt` files found: {summary['pptLegacyCount']}
- Keynote `.key` files found inside zips: {summary['keyFileCount']}
- Documentation PDFs found: {summary['pdfDocCount']}
- Average package size: {summary['avgZipSizeMB']} MB

## Technical Inventory Averages

- Average slides per readable deck: {summary['avgSlides']}
- Average slide layouts per readable deck: {summary['avgLayouts']}
- Average slide masters per readable deck: {summary['avgMasters']}
- Average media assets per readable deck: {summary['avgMedia']}
- Average chart parts per readable deck: {summary['avgCharts']}

{technical_ranges(records)}

## Market Fit Clusters

{md_table(summary['marketCounts'], records, 'marketClusters')}

## Visual Mood Clusters

{md_table(summary['moodCounts'], records, 'moodClusters')}

## Platform Packaging Signals

{json.dumps(summary['platformCounts'], indent=2, ensure_ascii=False)}

## Role Signals Found In Slide Text

{json.dumps(summary['roleSignalCounts'], indent=2, ensure_ascii=False)}

## Common Layout Names

{json.dumps(summary['commonLayoutNames'], indent=2, ensure_ascii=False)}

## Common Theme Fonts

{json.dumps(summary['commonThemeFonts'], indent=2, ensure_ascii=False)}

## Design Intelligence Learned

### 1. Market Fit Is The First Split

The corpus is not one presentation style. It breaks into corporate/project proposal, startup/tech, agency/creative, portfolio/brand/fashion, architecture/interior/furniture, education/social, food/health/lifestyle, and sustainability clusters. A single definition of "premium" would be wrong. Premium finance/project proposal leans disciplined and grid-led; premium creative/portfolio leans editorial, crop-led, and rhythm-led.

### 2. Dark Gradient Business Decks Are Saturated

Many references use black/dark bases, bright accent gradients, and modern business naming. Treat this as a saturated marketplace pattern. Learn the confidence, contrast, and impact, but avoid cloning black-gradient hero covers or repeated dark-card systems.

### 3. Product Readiness Depends On Layout Systems

The stronger packages are not only slide visuals; they include many role layouts, documentation, PPTX packaging, and sometimes legacy PPT compatibility. Future designs should define master/theme/layout behavior before slide-by-slide styling.

### 4. Density Needs A Map

Across business plans, proposals, and reports, useful decks need light statement slides, medium explanation slides, dense data/table slides, image breaks, and closing moments. Do not keep the same density across all slides.

### 5. Editorial Influence Separates Premium From Generic

The portfolio, fashion, architecture, furniture, and annual-report clusters point toward magazine/editorial thinking: stronger crops, fewer elements, better silence, and more deliberate type scale. This is a high-value direction for premium deck originality.

### 6. Template Usability Must Be Tested

Corpus packages often sell through style, but the reusable product test is harsher: longer titles, more bullets, image aspect changes, chart data changes, and logo swaps must not break the layout. This should become a required stress test before declaring a deck marketplace-ready.

### 7. Export Reality Is A Marketplace Gate

Because packages mix PowerPoint, Google Slides labels, Keynote labels, PDFs, and sometimes legacy `.ppt`, future template work should assume conversion risk. Keep charts editable, shapes reasonable, fonts documented, and PDF export clean.

## Reusable Design Rules For Future Decks

- Start every deck with market fit, not mood.
- Build a slide-role matrix before styling.
- Use two to three layout variations for major roles.
- Define master/layout placeholders before designing individual slides.
- Mix light, medium, dense, data-heavy, image-heavy, and rest slides.
- Use thumbnail contact-sheet review to catch monotony.
- Use edit stress tests for title length, bullet count, image ratio, logo color, and chart data.
- Avoid saturated corpus tropes: black-gradient business covers, generic corporate card grids, and repeated "modern project proposal" structure.
- Borrow from editorial, annual report, architecture, dashboard, and keynote rhythm to create originality beyond typical marketplace PPT templates.

## Do-Not-Copy Guard

- Do not copy exact slide order from any reference package.
- Do not copy black/purple/green/orange gradient motifs directly.
- Do not copy cover composition, title/image placement, section divider motif, or chart styling one-to-one.
- Do not treat Google Slides or Keynote labels as different design logic if the underlying package is a PPTX export; inspect the actual editable structure.
- Do not let a fashionable mood override template usability.

## Recommended Next Learning Pass

This pass read the corpus structurally from filenames, package contents, and PPTX XML metadata. A deeper visual pass should render representative decks from each cluster into thumbnails/contact sheets and score them for attention control, visual silence, hierarchy, grid discipline, density rhythm, and edit stress resilience.
"""


def output_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if args.output:
        report = Path(args.output).expanduser()
        if not report.is_absolute():
            report = Path.cwd() / report
    else:
        report = repo_root() / ".design-brain" / "reference-insights" / f"{stamp}-presentation-template-corpus-study.md"
    if args.json_output:
        json_path = Path(args.json_output).expanduser()
        if not json_path.is_absolute():
            json_path = Path.cwd() / json_path
    else:
        json_path = report.with_suffix(".json")
    return report.resolve(), json_path.resolve()


def main() -> int:
    configure_stdout()
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    zip_paths = sorted(root.glob("*.zip"))
    if args.limit:
        zip_paths = zip_paths[: args.limit]
    records = [inspect_outer_zip(path) for path in zip_paths]
    summary = summarize(records)
    data = {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "root": str(root),
        "summary": summary,
        "records": records,
    }
    if args.json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    report_path, json_path = output_paths(args)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_markdown(root, records, summary), encoding="utf-8", newline="\n")
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")
    print(f"Presentation corpus report written: {report_path}")
    print(f"Presentation corpus JSON written: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
