#!/usr/bin/env python
"""Run the internally owned Codex Design presentation capability."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
import uuid
from xml.etree import ElementTree as ET
from zipfile import BadZipFile

from routing import route_pptx
from design_brain_process_utils import run_command, resolve_python_invocation

ROOT = Path(__file__).resolve().parents[3]
CAP = ROOT / "skills/presentation-deck"

sys.path.insert(0, str(CAP / "runtime/native"))
from pptx_size_policy import (new_contract, read_contract, write_contract,
                              check_source_canvas, check_pptx_canvas)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def resolve_path(value: str, base: Path = ROOT) -> Path:
    path = Path(value).expanduser()
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def fingerprint(path: Path) -> dict:
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}


def invoke(argv: list[str], timeout: float = 30):
    return run_command(argv, cwd=ROOT, timeout=timeout, env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}, isolate_process_group=True)


def checked(argv: list[str], timeout: float = 30):
    result = invoke(argv, timeout)
    if not result.ok:
        reason = "timeout" if result.timedOut else f"exit {result.returncode}"
        raise ValueError(f"{reason}: {result.stderrExcerpt or result.stdoutExcerpt or result.command}")
    return result


def engine(args) -> dict:
    """Resolve internal package identity and a working interpreter."""
    meta = load_json(CAP / 'capability.json')
    local_python = ROOT / '.venv-presentation' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    candidate = args.python or os.environ.get('BRAIN_DESIGN_PPTX_PYTHON') or (str(local_python) if local_python.is_file() else None)
    selected = resolve_python_invocation(candidate)
    prefix = list(selected.commandPrefix)
    checked([*prefix, '-B', str(CAP / 'runtime/native/capability_integrity.py')])
    return {'root': str(CAP), 'nativeScripts': str(CAP / 'runtime/native'),
            'owner': meta['id'], 'version': meta['version'],
            'integritySha256': fingerprint(CAP / 'provenance/integrity.json')['sha256'],
            'python': selected.executable, 'pythonCommand': prefix}


def safe_output(path: Path, owner: dict) -> Path:
    capability_root = Path(owner["root"])
    if path == ROOT or path.is_relative_to(capability_root):
        raise ValueError("Output must be outside the capability installation and cannot be the plugin root.")
    if path.is_relative_to(ROOT):
        relative = path.relative_to(ROOT)
        allowed = relative.parts and relative.parts[0] in {"output", "reports", "exports"}
        if not allowed:
            raise ValueError("Inside the plugin, use output/, reports/, or exports/ for projects and results.")
    return path


def existing_project(value: str, owner: dict) -> Path:
    path = safe_output(resolve_path(value, Path.cwd()), owner)
    if not path.is_dir():
        raise ValueError(f"Project directory missing: {path}")
    return path


def generation_project(path: Path):
    if not (path / "svg_output").is_dir() or (path / "authoring-svg-flat").exists():
        raise ValueError("Generate requires svg_output/ and cannot use a round-trip workspace.")


def new_file(value: str, owner: dict) -> Path:
    path = safe_output(resolve_path(value, Path.cwd()), owner)
    if path.exists():
        raise ValueError(f"Output already exists; choose a new filename: {path}")
    if path.suffix.lower() != ".pptx":
        raise ValueError("PPTX output must end in .pptx.")
    return path


def prepare(args, owner: dict) -> tuple[list[str], Path | None, Path | None]:
    scripts = Path(owner["nativeScripts"])
    project = None
    output = None
    action = args.action
    if action == "init":
        project = safe_output(resolve_path(args.project, Path.cwd()), owner)
        if project.exists():
            raise ValueError(f"Project already exists: {project}")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*_\d{8}", project.name):
            raise ValueError("Use a project name ending _YYYYMMDD to create the exact requested directory.")
        tail = ["project_manager.py", "init", project.name, "--dir", str(project.parent)]
        canvas = new_contract(args.format, args.size_inches)
        if canvas["format"]:
            tail += ["--format", canvas["format"]]
        if args.mode == "quick":
            tail += ["--quick-generate"]
    elif action == "import-pptx":
        source = resolve_path(args.source, Path.cwd())
        if not source.is_file() or source.suffix.lower() != ".pptx":
            raise ValueError("Import requires an existing .pptx source file.")
        project = safe_output(resolve_path(args.project, Path.cwd()), owner)
        if project.exists():
            raise ValueError(f"Import target already exists: {project}")
        tail = ["pptx_to_svg.py", str(source), "-o", str(project), "--inheritance-mode", "both", "--roundtrip"]
    elif action in {"template-check", "template-preview", "apply-template"}:
        project = existing_project(args.project, owner)
        if action == "template-check":
            tail = ["svg_quality_checker.py", str(project / "templates"), "--template-mode", "--json"]
        elif action == "template-preview":
            check_source_canvas(project, "templates")
            output = new_file(args.output, owner)
            tail = ["template_preview_pptx.py", str(project), "-o", str(output)]
        else:
            generation_project(project)
            roots = [resolve_path(value, Path.cwd()) for value in args.root]
            if any(not value.is_dir() for value in roots):
                raise ValueError("Every template root must be an existing workspace.")
            tail = ["apply_template.py", str(project)]
            for value in roots:
                tail += ["--root", str(value)]
            if args.dry_run:
                tail += ["--dry-run"]
    elif action == "delivery-check":
        source = resolve_path(args.source, Path.cwd())
        if not source.is_file():
            raise ValueError(f"PPTX missing: {source}")
        tail = ["pptx_delivery_check.py", str(source)]
    else:
        project = existing_project(args.project, owner)
        if action == "export-roundtrip":
            if not (project / "authoring-svg-flat").is_dir() or (project / "svg_output").exists():
                raise ValueError("Round-trip export requires authoring-svg-flat/; do not mix Generate artifacts.")
            output = new_file(args.output, owner)
            tail = ["svg_to_pptx.py", str(project), "--roundtrip", "-o", str(output)]
            if args.native_data:
                tail += ["--native-charts-and-tables"]
        else:
            generation_project(project)
            if action in {"check", "export"}:
                check_source_canvas(project)
            if action == "import-sources":
                sources = [resolve_path(s, Path.cwd()) for s in args.sources]
                if any(not s.exists() for s in sources):
                    raise ValueError("Every imported source must be a local existing file or directory.")
                if any(s == project or project.is_relative_to(s) or s.is_relative_to(project) for s in sources):
                    raise ValueError("Sources must be outside the project being populated.")
                tail = ["project_manager.py", "import-sources", str(project), *map(str, sources), "--copy"]
            elif action == "check":
                tail = ["svg_quality_checker.py", str(project), "--canonical-authoring", "--stage", "final", "--json"]
                if args.mode == "quick":
                    tail += ["--quick-generate"]
            elif action == "stamp-data":
                tail = ["stamp_native_fallbacks.py", str(project / "svg_output"), "--write"]
            elif action == "export":
                output = new_file(args.output, owner)
                tail = ["svg_to_pptx.py", str(project), "-o", str(output)]
                if args.mode == "quick":
                    tail += ["--quick-generate"]
                if args.native_data:
                    tail += ["--native-charts-and-tables"]
            elif action == "finalize":
                tail = ["finalize_svg.py", str(project)]
            elif action == "notes":
                tail = ["total_md_split.py", str(project)]
            elif action == "validate":
                tail = ["project_manager.py", "validate", str(project)]
            else:
                raise ValueError(f"Unknown operation: {action}")
    return [*owner["pythonCommand"], "-B", str(scripts / tail[0]), *tail[1:]], project, output


def save_receipt(project: Path, receipt: dict) -> Path:
    directory = project / "validation/brain-design"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{receipt['action']}-{uuid.uuid4().hex}.json"
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--python", default="", help="Capability Python executable; no shell flags")
    p.add_argument("--timeout", type=float, default=120, help="Per-operation process-tree timeout in seconds (max 600)")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("doctor", help="Read-only package identity and entry-point checks")
    route = sub.add_parser("route", help="Choose artifact and PPTX workflow without loading native modules")
    route.add_argument("--task", required=True)
    route.add_argument("--source-pptx", default="")
    for action in ("init", "import-sources", "check", "stamp-data", "export", "finalize", "notes", "validate", "import-pptx", "export-roundtrip"):
        cmd = sub.add_parser(action)
        cmd.add_argument("project")
        if action in {"init", "check", "export"}:
            cmd.add_argument("--mode", choices=("default", "quick"), default="default")
        if action == "init":
            canvas = cmd.add_mutually_exclusive_group()
            canvas.add_argument("--format", choices=("ppt169onscreen", "wechat", "xiaohongshu", "moments", "story", "banner", "a4"), help="Explicit preset override; native PPTX defaults to 10 x 5.625 inches")
            canvas.add_argument("--size-inches", nargs=2, metavar=("WIDTH", "HEIGHT"), help="Explicit custom PPTX size")
        if action == "import-sources":
            cmd.add_argument("sources", nargs="+")
        if action == "import-pptx":
            cmd.add_argument("--source", required=True)
        if action in {"export", "export-roundtrip"}:
            cmd.add_argument("--output", required=True, help="New .pptx path; overwriting is refused")
        if action in {"export", "export-roundtrip"}:
            cmd.add_argument("--native-data", action="store_true", help="Opt into native Chart/Table objects")
    for action in ("template-check", "template-preview", "apply-template"):
        cmd = sub.add_parser(action)
        cmd.add_argument("project")
        if action == "template-preview":
            cmd.add_argument("--output", required=True)
        if action == "apply-template":
            cmd.add_argument("--root", action="append", required=True)
            cmd.add_argument("--dry-run", action="store_true")
    delivery = sub.add_parser("delivery-check", help="Read-only OOXML delivery audit")
    delivery.add_argument("source")
    return p


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = parser().parse_args()
    try:
        if not 0 < args.timeout <= 600:
            raise ValueError("Timeout must be greater than 0 and at most 600 seconds.")
        if args.action == "route":
            print(json.dumps(route_pptx(args.task, args.source_pptx), ensure_ascii=False, indent=2))
            return 0
        owner = engine(args)
        if args.action == "doctor":
            checks = []
            for script in ("project_manager.py", "svg_quality_checker.py", "svg_to_pptx.py", "pptx_to_svg.py", "pptx_delivery_check.py", "template_preview_pptx.py", "apply_template.py"):
                result = invoke([*owner["pythonCommand"], "-B", str(Path(owner["nativeScripts"]) / script), "--help"], min(args.timeout, 30))
                checks.append({"tool": script, "exitCode": result.returncode, "timedOut": result.timedOut, "stderr": result.stderrExcerpt})
            ready = all(row["exitCode"] == 0 and not row["timedOut"] for row in checks)
            print(json.dumps({"status": "READY" if ready else "DEPENDENCY_ERROR", "engine": owner, "checks": checks, "scope": "Core CLI loading only; export, visual quality, audio/video and optional dependencies require their own checks."}, indent=2))
            return 0 if ready else 1
        argv, project, output = prepare(args, owner)
        inputs = []
        if project and project.is_dir():
            for folder in ("svg_output", "authoring-svg-flat"):
                inputs.extend(fingerprint(p) for p in sorted((project / folder).glob("*.svg")))
        if getattr(args, "source", None):
            inputs.append(fingerprint(resolve_path(args.source, Path.cwd())))
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
        result = invoke(argv, args.timeout)
        if result.ok and args.action == "init":
            write_contract(project, new_contract(args.format, args.size_inches))
        receipt = {"schema": "design-brain.presentation-operation.v2", "action": args.action, "timestamp": datetime.now(timezone.utc).isoformat(), "engine": owner, "argv": argv, "exitCode": result.returncode, "timedOut": result.timedOut, "killedPids": result.killedPids, "status": "PASS" if result.ok else "UNKNOWN" if result.timedOut else "FAIL", "inputs": inputs, "output": fingerprint(output) if output and output.is_file() else None, "stdout": result.stdout[-64000:], "stderr": result.stderr[-16000:], "designReadiness": "NOT_EVALUATED"}
        canvas = read_contract(project) if project and args.action != "export-roundtrip" else None
        if canvas:
            receipt["pptxCanvas"] = canvas
            if result.ok and output:
                try:
                    receipt["sizeCheck"] = check_pptx_canvas(output, canvas)
                except (ValueError, OSError, KeyError, ET.ParseError, BadZipFile) as exc:
                    receipt.update(status="FAIL", sizeCheck={"status": "FAIL", "error": str(exc)})
        if project and project.is_dir():
            receipt["receipt"] = str(save_receipt(project, receipt))
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 1 if receipt["status"] != "PASS" else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
