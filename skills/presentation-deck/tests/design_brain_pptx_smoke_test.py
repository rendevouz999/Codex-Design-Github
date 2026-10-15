#!/usr/bin/env python
"""Bounded integration smoke using isolated native-PPTX fixtures."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import argparse
import json
import re
from pathlib import Path
import sys
import tempfile
import time
import zipfile
from xml.etree import ElementTree as ET

from design_brain_modules import select_module
from design_brain_presentation_route import artifact_intent, route_pptx
from design_brain_process_utils import run_command

ROOT = Path(__file__).resolve().parents[3]
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main", "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


def slide(text: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" font-family="Arial" lang="en-US" data-pptx-page-role="content">
<rect id="background" data-pptx-role="background" x="0" y="0" width="1280" height="720" fill="#FFFFFF"/>
<g id="heading" data-pptx-bounds="80 55 1120 80">
<text id="title" x="80" y="110" font-size="40" font-weight="700" fill="#17243B">{text}</text>
</g><g id="content" data-pptx-bounds="80 180 1120 360">
<rect id="panel" x="80" y="180" width="1120" height="360" fill="#EAF0F7"/>
<text id="body" x="120" y="280" font-size="28" fill="#17243B">Editable shapes and text</text>
</g><g id="page-footer" data-pptx-bounds="80 600 1120 70">
<text id="footer" x="80" y="640" font-size="18" fill="#526176">Brain Design integration fixture</text>
</g>
</svg>'''


def data_slide() -> str:
    chart = {"name": "revenue", "x": 80, "y": 160, "width": 520, "height": 430, "type": "column", "categories": ["Q1", "Q2"], "series": [{"name": "Revenue", "values": [12, 18]}], "show_legend": False, "data_labels": {"show_value": True}, "axes": {"category": {"visible": True, "major_gridlines": False}, "value": {"visible": False, "major_gridlines": False}}, "style": {"colors": ["#2563EB"], "font_family": "Arial", "text_color": "#1F2937", "axis_color": "none", "grid_color": "none"}}
    table = {"schema": "ppt-master.semantic-table.v2", "name": "results", "x": 720, "y": 180, "width": 480, "height": 240, "columns": ["Quarter", "Revenue"], "rows": [["Q1", "12"], ["Q2", "18"]], "style": {"font_family": "Arial", "font_size": 24, "header_font_size": 24, "header_text": "#1F2937", "body_text": "#1F2937", "border_width": 0}}
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" font-family="Arial" lang="en-US" data-pptx-page-role="content">
<rect id="background" data-pptx-role="background" width="1280" height="720" fill="#FFFFFF"/>
<g id="heading" data-pptx-bounds="80 50 1120 80"><text x="80" y="110" font-size="40" fill="#17243B">Native data fixture</text></g>
<g id="revenue" data-pptx-bounds="80 160 520 430" data-pptx-replace-with="chart">
<metadata type="application/json">{json.dumps(chart)}</metadata>
<rect x="180" y="390" width="80" height="160" fill="#2563EB"/>
<rect x="380" y="310" width="80" height="240" fill="#2563EB"/>
<text x="220" y="580" text-anchor="middle" font-size="24" fill="#1F2937">Q1</text>
<text x="420" y="580" text-anchor="middle" font-size="24" fill="#1F2937">Q2</text>
<text x="220" y="375" text-anchor="middle" font-size="24" fill="#1F2937">12</text>
<text x="420" y="295" text-anchor="middle" font-size="24" fill="#1F2937">18</text>
</g>
<g id="results" data-pptx-bounds="720 180 480 240" data-pptx-replace-with="table">
<metadata type="application/json">{json.dumps(table)}</metadata>
<text x="744" y="225" font-size="24" fill="#1F2937">Quarter</text>
<text x="984" y="225" font-size="24" fill="#1F2937">Revenue</text>
<text x="744" y="305" font-size="24" fill="#1F2937">Q1</text>
<text x="984" y="305" font-size="24" fill="#1F2937">12</text>
<text x="744" y="385" font-size="24" fill="#1F2937">Q2</text>
<text x="984" y="385" font-size="24" fill="#1F2937">18</text>
</g></svg>'''


def run_checks(args, work: Path) -> dict:
    started = time.monotonic()
    checks = []
    project = work / "native_fixture_20261012"
    prefix = [args.python or sys.executable, "-B", str(ROOT / "skills/presentation-deck/runtime/presentation.py")]
    if args.python:
        prefix += ["--python", args.python]
    prefix += ["--timeout", "50"]

    def record(name):
        checks.append(name)
        print(f"PASS {name}", flush=True)

    def cli(name, argv, expected=0):
        remaining = args.global_timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise AssertionError("Global smoke timeout exceeded")
        result = run_command(prefix + argv, cwd=work, timeout=min(remaining, 75), isolate_process_group=True)
        if result.timedOut or (result.returncode != 0 if expected == 0 else result.returncode == 0):
            raise AssertionError(f"{name}: exit {result.returncode}, timeout={result.timedOut}\n{result.stdout[-8000:]}\n{result.stderr[-4000:]}")
        if result.stdout.strip():
            value = json.loads(result.stdout)
        else:
            value = json.loads(result.stderr)
        record(name)
        return value

    assert artifact_intent("tambahkan slide animasi ke PowerPoint ini") == "native"
    unresolved = route_pptx("tambahkan slide animasi ke PowerPoint ini")
    assert unresolved["route"] == "edit-native" and unresolved["sourceRequired"]
    assert route_pptx("buat PowerPoint dengan animasi")["route"] == "generate"
    assert select_module(task="tambahkan slide animasi ke PowerPoint ini")["id"] == "presentation-deck"
    assert select_module(task="ubah PPTX ke HTML")["id"] == "web-deck"
    assert artifact_intent("buat PPTX dan HTML") == "both"
    assert route_pptx("isi template PPTX", "source.pptx")["route"] == "edit-native"
    assert route_pptx("buat template PPTX reusable")["route"] == "create-template"
    assert route_pptx("buat PPTX cepat")["profile"] == "quick"
    record("route boundaries")

    cli("initialize exact project", ["init", str(project), "--mode", "quick", "--format", "ppt169"])
    cli("refuse existing project", ["init", str(project)], expected=1)
    first = project / "svg_output/slide_01.svg"
    first.write_text(slide("Fixture alpha"), encoding="utf-8")
    (project / "svg_output/slide_02.svg").write_text(slide("Fixture beta"), encoding="utf-8")
    cli("reject missing quality report", ["export", str(project), "--mode", "quick", "--output", str(work / "unchecked.pptx")], expected=1)
    cli("final source-bound quality check", ["check", str(project), "--mode", "quick"])
    output = work / "editable.pptx"
    exported = cli("native export", ["export", str(project), "--mode", "quick", "--output", str(output)])
    assert exported["output"]["sha256"] and exported["designReadiness"] == "NOT_EVALUATED"
    with zipfile.ZipFile(output) as package:
        original_slides = {name: package.read(name) for name in ("ppt/slides/slide1.xml", "ppt/slides/slide2.xml")}
        xml = ET.fromstring(original_slides["ppt/slides/slide1.xml"])
        assert "Fixture alpha" in [n.text for n in xml.findall(".//a:t", NS)]
        assert len(xml.findall(".//p:sp", NS)) >= 3
        assert not xml.findall(".//p:pic", NS), "Fixture must contain editable objects, not a screenshot"
    record("native text and shapes in OOXML")
    audit = cli("delivery audit", ["delivery-check", str(output)])
    assert json.loads(audit["stdout"])["status"] != "failed"
    cli("refuse output overwrite", ["export", str(project), "--mode", "quick", "--output", str(output)], expected=1)
    original = first.read_bytes()
    first.write_text(slide("Fixture changed"), encoding="utf-8")
    stale = cli("reject stale quality report", ["export", str(project), "--mode", "quick", "--output", str(work / "stale.pptx")], expected=1)
    assert "stale" in (stale.get("stderr", "") + stale.get("stdout", "")).lower()
    first.write_bytes(original)
    assert not (work / "stale.pptx").exists()

    imported = work / "roundtrip"
    cli("source-preserving import", ["import-pptx", str(imported), "--source", str(output)])
    cli("reject mixed workspace", ["check", str(imported), "--mode", "quick"], expected=1)
    unchanged = work / "unchanged.pptx"
    cli("round-trip without edits", ["export-roundtrip", str(imported), "--output", str(unchanged)])
    with zipfile.ZipFile(unchanged) as package:
        assert all(package.read(name) == data for name, data in original_slides.items())
    record("untouched slide XML preserved byte-for-byte")
    files = sorted((imported / "authoring-svg-flat").glob("*.svg"))
    edited = next(path for path in files if "Fixture alpha" in path.read_text(encoding="utf-8"))
    edited.write_text(edited.read_text(encoding="utf-8").replace("Fixture alpha", "Fixture gamma"), encoding="utf-8")
    changed = work / "selective-edit.pptx"
    cli("selective native edit", ["export-roundtrip", str(imported), "--output", str(changed)])
    with zipfile.ZipFile(changed) as package:
        assert package.read("ppt/slides/slide2.xml") == original_slides["ppt/slides/slide2.xml"]
        assert b"Fixture gamma" in package.read("ppt/slides/slide1.xml")
    with zipfile.ZipFile(output) as package:
        assert all(package.read(name) == data for name, data in original_slides.items())
    record("selective edit preserves other slide and original input")
    cli("edited delivery audit", ["delivery-check", str(changed)])
    data_project = work / "data_fixture_20261012"
    cli("initialize data fixture", ["init", str(data_project), "--mode", "quick", "--format", "ppt169"])
    (data_project / "svg_output/slide_01.svg").write_text(data_slide(), encoding="utf-8")
    cli("stamp complete native data fallback", ["stamp-data", str(data_project)])
    cli("validate chart and table source", ["check", str(data_project), "--mode", "quick"])
    data_output = work / "native-data.pptx"
    data_export = cli("opt-in chart and table export", ["export", str(data_project), "--mode", "quick", "--native-data", "--output", str(data_output)])
    with zipfile.ZipFile(data_output) as package:
        xml = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        assert len(xml.findall(".//a:tbl", NS)) == 1
        texts = [n.text for n in xml.findall(".//a:tbl//a:t", NS)]
        assert all(t in texts for t in ("Quarter", "Revenue", "Q1", "Q2", "12", "18"))
        charts = [name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml")]
        assert len(charts) == 1, charts
        chart_xml = ET.fromstring(package.read(charts[0]))
        values = [n.text for n in chart_xml.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/chart}numCache/{http://schemas.openxmlformats.org/drawingml/2006/chart}pt/{http://schemas.openxmlformats.org/drawingml/2006/chart}v")]
        assert values == ["12", "18"], values
        assert any(name.startswith("ppt/embeddings/") and name.endswith(".xlsx") for name in package.namelist())
    record("native chart workbook and table values preserved")
    cli("native data delivery audit", ["delivery-check", str(data_output)])
    original_data = data_output.read_bytes()
    data_import = work / "data-roundtrip"
    cli("import native chart and table", ["import-pptx", str(data_import), "--source", str(data_output)])
    source = next((data_import / "authoring-svg-flat").glob("*.svg"))
    def update_data(match):
        payload = json.loads(match.group(2))
        if "series" in payload:
            payload["series"][0]["values"] = [24, 36]
        elif payload.get("schema") == "ppt-master.semantic-table.v2":
            for row, value in zip(payload["rows"][1:], ("24", "36")):
                row[1]["paragraphs"][0]["runs"][0]["text"] = value
        return match.group(1) + json.dumps(payload) + match.group(3)
    source.write_text(re.sub(r'(<metadata\b[^>]*>)(.*?)(</metadata>)', update_data, source.read_text(encoding="utf-8"), flags=re.S), encoding="utf-8")
    owner = data_export["engine"]
    for name, command in (
        ("refresh imported data previews", ["svg_authoring_view.py", str(data_import / "authoring-svg-flat"), "--refresh-summary"]),
        ("roundtrip data capacity gate", ["svg_quality_checker.py", str(data_import), "--roundtrip", "--json"]),
    ):
        remaining = args.global_timeout - (time.monotonic() - started)
        assert remaining > 0, "Global smoke timeout exceeded"
        result = run_command([owner["python"], "-B", str(Path(owner["nativeScripts"]) / command[0]), *command[1:]], cwd=work, timeout=min(remaining, 50), isolate_process_group=True)
        assert result.ok, f"{name}: {result.stderr[-2000:]} {result.stdout[-2000:]}"
        record(name)
    edited_data = work / "edited-data.pptx"
    receipt = cli("roundtrip native data edit", ["export-roundtrip", str(data_import), "--native-data", "--output", str(edited_data)])
    assert "--native-charts-and-tables" in receipt["argv"]
    with zipfile.ZipFile(edited_data) as package:
        chart = next(name for name in package.namelist() if name.startswith("ppt/charts/chart") and name.endswith(".xml"))
        chart_xml = ET.fromstring(package.read(chart))
        values = [n.text for n in chart_xml.findall(".//{http://schemas.openxmlformats.org/drawingml/2006/chart}numCache/{http://schemas.openxmlformats.org/drawingml/2006/chart}pt/{http://schemas.openxmlformats.org/drawingml/2006/chart}v")]
        assert values == ["24", "36"], values
        table = ET.fromstring(package.read("ppt/slides/slide1.xml"))
        texts = [n.text for n in table.findall(".//a:tbl//a:t", NS)]
        assert all(value in texts for value in ("24", "36")), texts
    assert data_output.read_bytes() == original_data
    record("edited chart and table values with unchanged original")
    cli("edited data delivery audit", ["delivery-check", str(edited_data)])
    result = {"status": "PASS", "checks": checks, "durationSeconds": round(time.monotonic()-started, 2), "workDir": str(work), "output": str(output), "visualInspection": "NOT_PERFORMED_BY_THIS_SCRIPT"}
    (work / "smoke-result.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default="")
    parser.add_argument("--work-dir", default="", help="Retain evidence in a new or empty directory")
    parser.add_argument("--global-timeout", type=float, default=420)
    args = parser.parse_args()
    try:
        if args.work_dir:
            work = Path(args.work_dir).resolve()
            if work.exists() and any(work.iterdir()):
                raise ValueError("Evidence directory must be new or empty.")
            work.mkdir(parents=True, exist_ok=True)
            result = run_checks(args, work)
        else:
            with tempfile.TemporaryDirectory(prefix="brain-pptx-smoke-") as directory:
                result = run_checks(args, Path(directory))
                result["workDir"] = "temporary fixtures cleaned up"
                result.pop("output", None)
        print(json.dumps(result, indent=2))
        return 0
    except (AssertionError, ValueError, OSError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
