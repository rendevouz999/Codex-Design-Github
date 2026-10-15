#!/usr/bin/env python
"""Inventory a PPTX file for deck-design review."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


TEXT_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory slide, layout, media, notes, and text from a PPTX.")
    parser.add_argument("--pptx", required=True, help="Path to .pptx file.")
    parser.add_argument("--output", default="", help="Optional report path.")
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def natural_key(name: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", name)
    return (int(match.group(1)) if match else 0, name)


def extract_text(xml_bytes: bytes) -> str:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return ""
    texts = [node.text or "" for node in root.iter(TEXT_NS)]
    return " ".join(part.strip() for part in texts if part and part.strip())


def inventory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
            "pptx": str(path),
            "valid": False,
            "error": "File not found.",
        }
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            slide_paths = sorted(
                [name for name in names if re.match(r"ppt/slides/slide\d+\.xml$", name)],
                key=natural_key,
            )
            layout_paths = [name for name in names if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml$", name)]
            master_paths = [name for name in names if re.match(r"ppt/slideMasters/slideMaster\d+\.xml$", name)]
            notes_paths = [name for name in names if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", name)]
            media_paths = [name for name in names if name.startswith("ppt/media/")]
            comments_paths = [name for name in names if "comments" in name.lower()]
            theme_paths = [name for name in names if re.match(r"ppt/theme/theme\d+\.xml$", name)]
            slides: list[dict[str, Any]] = []
            for index, slide_path in enumerate(slide_paths, start=1):
                xml_bytes = archive.read(slide_path)
                text = extract_text(xml_bytes)
                slides.append(
                    {
                        "index": index,
                        "path": slide_path,
                        "textLength": len(text),
                        "textPreview": text[:220],
                    }
                )
    except zipfile.BadZipFile:
        return {
            "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
            "pptx": str(path),
            "valid": False,
            "error": "Not a valid PPTX/ZIP file.",
        }

    return {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "pptx": str(path),
        "valid": True,
        "slideCount": len(slide_paths),
        "layoutCount": len(layout_paths),
        "masterCount": len(master_paths),
        "notesCount": len(notes_paths),
        "commentsCount": len(comments_paths),
        "mediaCount": len(media_paths),
        "themeCount": len(theme_paths),
        "slides": slides,
        "reviewPrompts": [
            "Map each slide to a role: cover, agenda, divider, problem, solution, metric, chart/table, team, closing.",
            "Check whether layouts are reusable or if each slide is a one-off composition.",
            "Run thumbnail review to confirm titles and key numbers stay readable at small size.",
            "Inspect chart/table slides for label clarity, contrast, and consistent data-color semantics.",
        ],
    }


def markdown_report(data: dict[str, Any]) -> str:
    if not data.get("valid"):
        return "\n".join(
            [
                "# PPTX Inventory",
                "",
                f"- Generated: {data['generatedAt']}",
                f"- PPTX: {data['pptx']}",
                f"- Valid: false",
                f"- Error: {data.get('error', 'Unknown error')}",
                "",
            ]
        )
    slide_lines = []
    for slide in data["slides"]:
        preview = slide["textPreview"] or "[no extracted text]"
        slide_lines.append(f"- Slide {slide['index']}: {preview}")
    return "\n".join(
        [
            "# PPTX Inventory",
            "",
            f"- Generated: {data['generatedAt']}",
            f"- PPTX: {data['pptx']}",
            f"- Slides: {data['slideCount']}",
            f"- Layouts: {data['layoutCount']}",
            f"- Masters: {data['masterCount']}",
            f"- Notes slides: {data['notesCount']}",
            f"- Comments parts: {data['commentsCount']}",
            f"- Media assets: {data['mediaCount']}",
            f"- Themes: {data['themeCount']}",
            "",
            "## Slide Text Preview",
            "",
            "\n".join(slide_lines) or "- No slides found.",
            "",
            "## Review Prompts",
            "",
            "\n".join(f"- {item}" for item in data["reviewPrompts"]),
            "",
        ]
    )


def output_path(args: argparse.Namespace) -> Path:
    if args.output:
        path = Path(args.output).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "reviews" / f"{stamp}-pptx-inventory.md"


def main() -> int:
    args = parse_args()
    pptx_path = Path(args.pptx).expanduser()
    if not pptx_path.is_absolute():
        pptx_path = Path.cwd() / pptx_path
    data = inventory(pptx_path.resolve())
    text = json.dumps(data, indent=2, ensure_ascii=False) if args.json else markdown_report(data)
    if args.output:
        path = output_path(args)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        print(f"PPTX inventory written: {path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
