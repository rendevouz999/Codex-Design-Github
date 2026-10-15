"""Project-scoped PPTX canvas contract; generic formats keep their own defaults."""
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from config import CANVAS_FORMATS
from slide_roster import discover_slide_svgs
from svg_to_pptx.canvas_contract import (
    parse_project_viewbox, require_consistent_project_viewboxes,
    require_powerpoint_slide_size,
)

CONTRACT_FILE = "pptx_canvas.json"
DEFAULT_FORMAT = "ppt169onscreen"
SCHEMA = "codex-design.pptx-canvas.v1"


def new_contract(format_key=None, size_inches=None):
    if format_key and size_inches:
        raise ValueError("Choose --format or --size-inches, not both.")
    if size_inches:
        try:
            width, height = (Decimal(value) * 96 for value in size_inches)
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("PPTX inches must be two finite positive numbers.") from exc
        viewbox = parse_project_viewbox(f"0 0 {width} {height}")
        selected = None
    else:
        selected = format_key or DEFAULT_FORMAT
        if selected not in CANVAS_FORMATS:
            raise ValueError(f"Unknown PPTX canvas format: {selected}")
        viewbox = parse_project_viewbox(CANVAS_FORMATS[selected]["viewbox"])
    emu = require_powerpoint_slide_size(viewbox)
    return {"schema": SCHEMA, "outputFormat": "pptx", "format": selected,
            "viewBox": viewbox.canonical, "widthEmu": emu[0], "heightEmu": emu[1],
            "selection": "explicit" if format_key or size_inches else "standing-user-default"}


def read_contract(project):
    path = Path(project) / CONTRACT_FILE
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != SCHEMA or data.get("outputFormat") != "pptx":
        raise ValueError(f"Invalid PPTX canvas contract: {path}")
    if not isinstance(data.get("viewBox"), str):
        raise ValueError("PPTX canvas viewBox must be a string.")
    viewbox = parse_project_viewbox(data["viewBox"])
    emu = require_powerpoint_slide_size(viewbox)
    if (data.get("widthEmu"), data.get("heightEmu")) != emu:
        raise ValueError("PPTX canvas viewBox and physical size disagree.")
    selected = data.get("format")
    if selected is not None and (not isinstance(selected, str) or selected not in CANVAS_FORMATS or
            parse_project_viewbox(CANVAS_FORMATS[selected]["viewbox"]) != viewbox):
        raise ValueError("PPTX canvas format and viewBox disagree.")
    return data


def write_contract(project, contract):
    path = Path(project) / CONTRACT_FILE
    with path.open("x", encoding="utf-8") as stream:
        json.dump(contract, stream, indent=2)
        stream.write("\n")


def check_source_canvas(project, source_dir="svg_output"):
    contract = read_contract(project)
    if contract:
        require_consistent_project_viewboxes(
            discover_slide_svgs(Path(project) / source_dir),
            expected_viewbox=contract["viewBox"], expected_label=CONTRACT_FILE)
    return contract


def check_pptx_canvas(pptx_path, contract):
    with ZipFile(pptx_path) as package:
        root = ET.fromstring(package.read("ppt/presentation.xml"))
    size = root.find("{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
    if size is None:
        raise ValueError("PPTX has no p:sldSz.")
    actual = int(size.attrib["cx"]), int(size.attrib["cy"])
    expected = contract["widthEmu"], contract["heightEmu"]
    if actual != expected:
        raise ValueError(f"PPTX slide size mismatch: expected {expected} EMU, got {actual}.")
    if expected == (9144000, 5143500) and size.get("type") != "screen16x9":
        raise ValueError("On-screen Show (16:9) requires p:sldSz type=screen16x9.")
    return {"status": "PASS", "widthEmu": actual[0], "heightEmu": actual[1], "type": size.get("type")}
