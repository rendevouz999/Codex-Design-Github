#!/usr/bin/env python
"""Render a PPTX from a file or ZIP into slide PNGs and a contact sheet."""

from __future__ import annotations

import argparse
import json
import os
import hashlib
import math
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from design_brain_process_utils import run_command


DEFAULT_SOFFICE = Path(r"C:\Program Files\LibreOffice\program\soffice.com")


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render PPTX/ZIP presentation to PNG contact sheet.")
    parser.add_argument("--input", required=True, help="Path to .pptx or .zip containing a .pptx.")
    parser.add_argument("--output-dir", default="", help="Output directory.")
    parser.add_argument("--soffice", default=str(DEFAULT_SOFFICE), help="Path to soffice.com/soffice.exe.")
    parser.add_argument("--renderer", choices=("auto", "powerpoint", "libreoffice"), default="auto")
    parser.add_argument("--scale", type=float, default=1.0, help="PDF render scale.")
    parser.add_argument("--thumb-width", type=int, default=320, help="Thumbnail width for contact sheet.")
    parser.add_argument("--max-slides", type=int, default=0, help="Optional max slides to render.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def slugify(value: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")[:90] or "presentation-render"


def output_dir_for(input_path: Path, value: str) -> Path:
    if value:
        out = Path(value).expanduser()
        if not out.is_absolute():
            out = Path.cwd() / out
        return out.resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return repo_root() / ".design-brain" / "screenshots" / f"{stamp}-{slugify(input_path.stem)}"


def extract_pptx(input_path: Path, work_dir: Path) -> Path:
    if input_path.suffix.lower() == ".pptx":
        target = work_dir / input_path.name
        shutil.copy2(input_path, target)
        return target
    if input_path.suffix.lower() != ".zip":
        raise ValueError("Input must be a .pptx or a .zip containing a .pptx.")
    with zipfile.ZipFile(input_path) as archive:
        pptx_entries = sorted(
            [entry for entry in archive.namelist() if entry.lower().endswith(".pptx")],
            key=lambda name: (len(name), name),
        )
        if not pptx_entries:
            raise ValueError(f"No .pptx found inside {input_path}")
        entry = pptx_entries[0]
        target = work_dir / Path(entry).name
        with archive.open(entry) as source, target.open("wb") as destination:
            shutil.copyfileobj(source, destination)
        return target


def convert_to_pdf(soffice: Path, pptx: Path, work_dir: Path) -> Path:
    if not soffice.exists():
        raise FileNotFoundError(f"LibreOffice soffice not found: {soffice}")
    command = [
        str(soffice),
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(work_dir),
        str(pptx),
    ]
    proc = run_command(command, cwd=work_dir, timeout=180, isolate_process_group=True)
    if not proc.ok:
        raise RuntimeError(f"LibreOffice conversion failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    pdf = work_dir / f"{pptx.stem}.pdf"
    if not pdf.exists():
        raise FileNotFoundError(f"Expected PDF was not created: {pdf}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return pdf


def render_pdf_pages(pdf: Path, output_dir: Path, scale: float, max_slides: int) -> list[Path]:
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(pdf))
    count = len(doc) if max_slides <= 0 else min(len(doc), max_slides)
    slide_dir = output_dir / "slides"
    slide_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    for index in range(count):
        page = doc[index]
        image = page.render(scale=scale).to_pil().convert("RGB")
        path = slide_dir / f"slide-{index + 1:03d}.png"
        image.save(path)
        rendered.append(path)
    return rendered


def make_contact_sheet(slides: list[Path], output_dir: Path, thumb_width: int) -> Path:
    if not slides:
        raise ValueError("No slide images were rendered.")
    images = [Image.open(path).convert("RGB") for path in slides]
    aspect = images[0].height / images[0].width
    thumb_height = int(thumb_width * aspect)
    columns = 4 if len(images) >= 4 else len(images)
    rows = math.ceil(len(images) / columns)
    label_height = 28
    gap = 18
    margin = 24
    sheet_width = margin * 2 + columns * thumb_width + (columns - 1) * gap
    sheet_height = margin * 2 + rows * (thumb_height + label_height) + (rows - 1) * gap
    sheet = Image.new("RGB", (sheet_width, sheet_height), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, image in enumerate(images):
        row, col = divmod(index, columns)
        x = margin + col * (thumb_width + gap)
        y = margin + row * (thumb_height + label_height + gap)
        thumb = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x, y))
        draw.rectangle([x, y, x + thumb_width - 1, y + thumb_height - 1], outline=(210, 210, 210), width=1)
        draw.text((x, y + thumb_height + 8), f"Slide {index + 1:02d}", fill=(40, 40, 40), font=font)
    out = output_dir / "contact-sheet.png"
    sheet.save(out)
    return out


def main() -> int:
    configure_stdout()
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = output_dir_for(input_path, args.output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Use a new render directory: {output_dir}")
    if output_dir.is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("Render outputs must be outside the capability installation")
    output_dir.mkdir(parents=True)
    before_hash = hashlib.sha256(input_path.read_bytes()).hexdigest()
    pptx = extract_pptx(input_path, output_dir)
    renderer = args.renderer
    if renderer == 'auto':
        renderer = 'powerpoint' if os.name == 'nt' else 'libreoffice'
    pdf = None
    if renderer == 'powerpoint':
        helper = Path(__file__).with_name('render_powerpoint.ps1')
        command = ['powershell.exe', '-NoProfile', '-File', str(helper), '-InputPath', str(pptx), '-OutputDirectory', str(output_dir / 'slides'), '-MaxSlides', str(args.max_slides)]
        result = run_command(command, cwd=output_dir, timeout=180, isolate_process_group=True)
        if not result.ok:
            raise RuntimeError(f'PowerPoint render failed (timeout={result.timedOut}): {result.stderrExcerpt}. Use --renderer libreoffice with --soffice when available.')
        receipt = json.loads(result.stdout)
        slides = sorted((output_dir / 'slides').glob('slide-*.png'))
        if len(slides) != receipt['slides']:
            raise RuntimeError('PowerPoint render count mismatch')
    else:
        pdf = convert_to_pdf(Path(args.soffice).expanduser().resolve(), pptx, output_dir)
        slides = render_pdf_pages(pdf, output_dir, args.scale, args.max_slides)
    if hashlib.sha256(input_path.read_bytes()).hexdigest() != before_hash:
        raise RuntimeError('Render input changed')
    contact_sheet = make_contact_sheet(slides, output_dir, args.thumb_width)
    summary = {
        "generatedAt": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z"),
        "input": str(input_path),
        "outputDir": str(output_dir),
        "pptx": str(pptx),
        "pdf": str(pdf) if pdf else None,
        "renderer": renderer,
        "sourcePreserved": True,
        "inputSha256": before_hash,
        "slideCount": len(slides),
        "contactSheet": str(contact_sheet),
        "slides": [str(path) for path in slides],
    }
    (output_dir / "render-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(f"Rendered {len(slides)} slides")
        print(f"Contact sheet: {contact_sheet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
