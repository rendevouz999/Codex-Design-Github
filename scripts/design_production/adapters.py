"""Narrow tool adapters. All executable names and paths are controller-owned."""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import struct
import time
import zipfile
from xml.etree import ElementTree as ET

from .contracts import ArtifactManifest, DesignQAReport, Empty, ReadInput, UnitContent
from .policy import ROOT, canonical_hash, digest, input_path, within
from .profiles import PROFILES
from design_brain_process_utils import kill_process_tree

CAP = ROOT / "skills/presentation-deck/runtime"
MODELS = {"read_input": ReadInput, "discover_capabilities": Empty, "write_unit": UnitContent,
          "build_artifact": Empty, "render_preview": Empty, "technical_qa": Empty}


class AuthorizedAdapters:
    def __init__(self, task, directory: Path, cancel_path: Path):
        self.task, self.directory, self.cancel_path = task, directory, cancel_path
        self.calls = 0
        self.agent_count = 0
        self.deadline = time.monotonic() + task.timeout_seconds
        self.units = {u.id: u for u in task.units}
        self.inputs = {r.id: r for r in task.inputs}
        self.manifests: list[ArtifactManifest] = []
        self.qa = DesignQAReport(status="UNVERIFIED", checks=[], issues=["QA not executed"], evidence=[])
        self.lock = asyncio.Lock()
        self.tool_events = []
        self.last_error = ""
        self.built = False
        self.rendered = False
        self.contents: dict[str, UnitContent] = {}
        self.cached = {}
        self.pptx_source = None
        # Inspect/edit/render copies declared editable unit sources; original bytes never change.
        for ref in task.inputs:
            if ref.role == "editable_source":
                source = self.checked_input(ref.id)
                if source.suffix.lower() == '.pptx':
                    if task.artifact_type != 'presentation' or not task.presentation or task.presentation.structure != 'preserve' or self.pptx_source:
                        raise ValueError('One PPTX source requires an explicit preserve contract')
                    self.pptx_source = source
                    continue
                content = UnitContent.model_validate_json(source.read_bytes())
                self.validate_unit(content)
                if content.unit_id in self.contents:
                    raise ValueError('Multiple editable sources target the same unit')
                self.contents[content.unit_id] = content
        if task.presentation and task.presentation.structure == 'preserve' and not self.pptx_source:
            raise ValueError('Preserve mode requires a hash-authorized PPTX source')

    def check(self):
        within(self.directory, ROOT / "output")
        if self.cancel_path.exists():
            raise asyncio.CancelledError("Main requested cancellation")
        if time.monotonic() >= self.deadline:
            raise TimeoutError("Production job deadline exceeded")

    def checked_input(self, key):
        if key not in self.inputs:
            raise ValueError("Input ID is outside assignment")
        ref = self.inputs[key]
        path = input_path(ref.path)
        if digest(path) != ref.sha256:
            raise ValueError("Authoritative input hash changed")
        return path

    def manifest(self, path, role, editable=False, units=None):
        path = within(path, self.directory)
        entry = ArtifactManifest(path=str(path), sha256=digest(path), format=path.suffix.lstrip('.'),
            unit_ids=units if units is not None else list(self.units), editable=editable, role=role)
        self.manifests.append(entry)
        return entry

    def validate_unit(self, content):
        if content.unit_id not in self.units:
            raise ValueError("Unit ID is outside assignment")
        unit = self.units[content.unit_id]
        preserving = self.task.presentation and self.task.presentation.structure == 'preserve'
        if preserving:
            if content.nodes or content.stories:
                raise ValueError('Existing PPTX only accepts bounded slide-local text edits')
            return
        if content.edits or not content.nodes:
            raise ValueError('New units require nodes; PPTX edits require preserve mode')
        if content.stories and not self.task.editorial:
            raise ValueError('Stories require an editorial contract')
        if len({n.id for n in content.nodes}) != len(content.nodes):
            raise ValueError("Duplicate node ID")
        for node in content.nodes:
            if (node.chart or node.table or node.native_placeholder or node.layer != 'slide') and self.task.artifact_type != 'presentation':
                raise ValueError('Native presentation metadata is not allowed in this profile')
            if (node.native_placeholder or node.layer != 'slide') and (not self.task.presentation or self.task.presentation.structure != 'structured'):
                raise ValueError('Placeholder/layer requires structured presentation contract')
            if node.story_id and not self.task.editorial:
                raise ValueError('Linked text frame requires editorial contract')
            if node.x + node.width > unit.width or node.y + node.height > unit.height:
                raise ValueError("Node exceeds assigned canvas")
            if node.placeholder and node.kind != "text":
                raise ValueError("Placeholders must be editable text clues")
            if node.kind == "text" and (not node.text.strip() or node.font_size > node.height):
                raise ValueError("Text needs content and a sufficient line box")

    async def invoke(self, name, arguments):
        async with self.lock:
            self.check()
            if name not in self.task.allowed_tools or name not in MODELS:
                raise ValueError("Tool is forbidden by assignment policy")
            self.calls += 1
            if self.calls > self.task.max_tool_calls:
                raise ValueError("Tool execution limit exceeded")
            args = MODELS[name].model_validate(arguments)
            for ref in self.inputs:
                self.checked_input(ref)
            key = canonical_hash([name, args.model_dump()])
            if key in self.cached:
                return self.cached[key]
            if name == "read_input":
                source = self.checked_input(args.input_id)
                if source.suffix.lower() == '.pptx':
                    from .pptx_support import source_inventory
                    value = source_inventory(source, self.task.units)
                elif source.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                    value = {"sha256": digest(source), "bytes": source.stat().st_size,
                             "limitation": "Raster reference needs Main visual interpretation in creative_constraints"}
                else:
                    if source.stat().st_size > 100_000:
                        raise ValueError("Text input exceeds 100 KB tool response limit")
                    value = {"input_id": args.input_id, "content": source.read_text(encoding="utf-8-sig"), "untrusted_reference_data": True}
            elif name == "discover_capabilities":
                value = PROFILES
            elif name == "write_unit":
                if self.task.operation in {"render", "qa"}:
                    raise ValueError("Read-only production stage cannot change source units")
                if self.built:
                    raise ValueError("Built artifacts are immutable; request a Main revision")
                self.validate_unit(args)
                self.contents[args.unit_id] = args
                value = {"unit_id": args.unit_id, "accepted": True}
                self.cached.clear()  # Subsequent reads/builds must observe this version.
            elif name == "build_artifact":
                value = await self.build()
            elif name == "render_preview":
                value = await self.render()
            else:
                value = self.verify().model_dump()
            self.tool_events.append({"tool": name, "arguments_sha256": key, "success": True})
            self.cached[key] = value
            return value

    async def process(self, command, seconds=60):
        """No shell; bounded output, environment, deadline, and owned process-tree cancellation."""
        self.check()
        remaining = min(seconds, self.deadline - time.monotonic())
        log = within(self.directory / f"adapter-{len(self.tool_events)}-{time.monotonic_ns()}.log", self.directory)
        # Native tools never inherit provider credentials, arbitrary Python paths, or Node injection flags.
        names = ("SystemRoot", "WINDIR", "PATH", "TEMP", "TMP", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)")
        env = {k: v for k, v in os.environ.items() if k.upper() in {n.upper() for n in names}}
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        scratch = within(self.directory / "scratch", self.directory)
        scratch.mkdir(exist_ok=True)
        env.update(TEMP=str(scratch), TMP=str(scratch), TMPDIR=str(scratch))
        start = time.monotonic()
        with log.open("wb") as stream:
            kwargs = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
            proc = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                    stdout=stream, stderr=stream, shell=False, **kwargs)
            try:
                while proc.poll() is None:
                    self.check()
                    if time.monotonic() - start > remaining or log.stat().st_size > 2_000_000:
                        raise TimeoutError("Native adapter exceeded time/output limit")
                    await asyncio.sleep(.1)
                if proc.returncode:
                    self.last_error = f"Native adapter failed (exit {proc.returncode}); inspect {log.name}"
                    raise RuntimeError(self.last_error)
            except BaseException:
                kill_process_tree(proc)
                proc.wait(timeout=10)
                raise
        self.manifest(log, "evidence", units=[])
        return log

    def svg(self, content):
        from .content_svg import svg_content
        return svg_content(content, self.units[content.unit_id], self.task.presentation)

    async def build(self):
        if self.built:
            return {"artifacts": [m.model_dump() for m in self.manifests]}
        if set(self.contents) != set(self.units):
            raise ValueError("Every assigned unit must have editable content")
        if self.pptx_source:
            from .pptx_support import build_preserving
            await build_preserving(self)
            self.built = True
            return {'artifacts': [m.model_dump() for m in self.manifests]}
        for key in self.units:
            content = self.contents[key]
            for suffix, data in ((".json", content.model_dump_json(indent=2)), (".svg", self.svg(content))):
                path = within(self.directory / (key + suffix), self.directory)
                with path.open("x", encoding="utf-8") as stream:
                    stream.write(data)
                self.manifest(path, "deliverable" if suffix == ".svg" and self.task.output_format == "svg" else "source", True, [key])
        order = self.directory / "unit-order.json"
        with order.open("x", encoding="utf-8") as stream:
            json.dump([key + ".svg" for key in self.units], stream)
        if self.task.editorial:
            from .editorial import reflow
            await reflow(self)
        if self.task.output_format == 'html':
            from .web_deck import build_web
            build_web(self)
        if self.task.output_format == "pptx":
            (self.directory / 'native-contract.json').write_text(json.dumps(self.task.presentation.model_dump() if self.task.presentation else None), encoding='utf-8')
            python = ROOT / (".venv-presentation/Scripts/python.exe" if os.name == "nt" else ".venv-presentation/bin/python")
            if not python.is_file():
                raise ValueError("Native presentation environment is missing")
            await self.process([str(python), "-B", str(CAP / "native/capability_integrity.py")], 20)
            await self.process([str(python), "-B", str(Path(__file__).with_name("native_export.py")), str(self.directory)], 60)
            self.manifest(self.directory / "design.pptx", "deliverable", True)
            if self.task.presentation and self.task.presentation.reusable_template:
                self.manifest(self.directory/'template-receipt.json','evidence')
                self.manifest(self.directory/'template-preview.pptx','source',True)
                for root in ('authored-template','applied-template'):
                    for path in (self.directory/root).rglob('*'):
                        if path.is_file():
                            self.manifest(path,'source',True)
        self.built = True
        self.cached.pop(canonical_hash(["technical_qa", {}]), None)
        return {"artifacts": [m.model_dump() for m in self.manifests]}

    async def render(self):
        if not self.built:
            raise ValueError("Build assigned units before rendering")
        if self.rendered:
            return {"rendered": True}
        if self.task.output_format == 'html':
            from .web_deck import render_web
            await render_web(self)
            self.rendered = True
            return {'rendered': True}
        node = shutil.which("node")
        if not node:
            raise ValueError("Node/Playwright preview integration is unavailable")
        if not self.pptx_source:
            await self.process([node, str(Path(__file__).with_name("render_svg.mjs")), str(self.directory)], 60)
            for key in self.units:
                self.manifest(self.directory / (key + ".png"), "preview", units=[key])
            self.manifest(self.directory / "render-checks.json", "evidence")
        if self.task.output_format == "pptx":
            python = ROOT / (".venv-presentation/Scripts/python.exe" if os.name == "nt" else ".venv-presentation/bin/python")
            await self.process([str(python), "-B", str(CAP / "design_brain_pptx_render_contact_sheet.py"),
                "--input", str(self.directory / "design.pptx"), "--output-dir", str(self.directory / "native-preview"), "--json"], 90)
            receipt = json.loads((self.directory / "native-preview/render-summary.json").read_text())
            expected_count = len(self.units)
            if self.pptx_source:
                from .pptx_support import source_inventory
                expected_count = source_inventory(self.pptx_source, self.task.units)['slide_count']
            if receipt["slideCount"] != expected_count or not receipt["sourcePreserved"]:
                raise ValueError("Native slide render count/source preservation failed")
            self.manifest(self.directory / "native-preview/render-summary.json", "evidence")
            for path in receipt["slides"]:
                self.manifest(Path(path), "preview")
        self.rendered = True
        self.cached.pop(canonical_hash(["technical_qa", {}]), None)
        return {"rendered": True, "previews": [m.model_dump() for m in self.manifests if m.role == "preview"]}

    def verify(self):
        checks, issues = [], []
        for ref in self.inputs:
            self.checked_input(ref)
        checks.append("Authoritative input hashes unchanged")
        if not self.built or not self.rendered:
            self.qa = DesignQAReport(status="UNVERIFIED", checks=checks, issues=["Build/render evidence is incomplete"], evidence=self.manifests[:])
            return self.qa
        for manifest in self.manifests:
            path = within(Path(manifest.path), self.directory)
            if digest(path) != manifest.sha256:
                issues.append("Artifact hash changed: " + path.name)
        checks.append("Artifact hashes read back")
        if self.task.output_format == 'html' or self.pptx_source:
            if self.task.output_format == 'html':
                from .web_deck import verify_web
                extra_checks, extra_issues = verify_web(self)
            else:
                from .pptx_support import verify_preserving
                extra_checks, extra_issues = verify_preserving(self)
            self.qa = DesignQAReport(status='FAIL' if issues + extra_issues else 'PASS', checks=checks+extra_checks, issues=issues+extra_issues, evidence=[m for m in self.manifests if m.role in {'preview','evidence'}])
            return self.qa
        rendered = json.loads((self.directory / "render-checks.json").read_text())
        if {item["unit"] for item in rendered} != set(self.units) or len(rendered) != len(self.units):
            issues.append("Rendered unit coverage mismatch")
        for item in rendered:
            unit = self.units[item["unit"]]
            if (item["width"], item["height"]) != (unit.width, unit.height):
                issues.append("Rendered dimensions mismatch")
            if item["overflow"]:
                issues.append(f"Rendered bounds overflow: {item['unit']}: {item['overflow']}")
            png = (self.directory / (item["unit"] + ".png")).read_bytes()
            if png[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", png[16:24]) != (unit.width, unit.height):
                issues.append("Preview pixels do not match assigned dimensions")
            source = ET.fromstring((self.directory / (unit.id + ".svg")).read_text(encoding="utf-8"))
            nodes = self.contents[unit.id].nodes
            if [n.get("id") for n in source] != [n.id for n in nodes]:
                issues.append("Editable SVG layer IDs/order mismatch")
        checks.extend(["Browser render at assigned dimensions", "Editable node IDs, layer count, declared typography and text-clue placeholders preserved in source", "Rendered SVG geometry/text bounds measured"])
        if self.task.editorial:
            from .editorial import verify_flow
            flow_checks, flow_issues = verify_flow(self)
            checks.extend(flow_checks)
            issues.extend(flow_issues)
        if self.task.output_format == "pptx":
            with zipfile.ZipFile(self.directory / "design.pptx") as archive:
                document = ET.fromstring(archive.read("ppt/presentation.xml"))
                size = document.find("{http://schemas.openxmlformats.org/presentationml/2006/main}sldSz")
                first = next(iter(self.units.values()))
                if size is None or (int(size.get("cx", 0)), int(size.get("cy", 0))) != (first.width*9525, first.height*9525):
                    issues.append("Native PowerPoint canvas size mismatch")
                slides = [n for n in archive.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
                if len(slides) != len(self.units):
                    issues.append("Native slide count mismatch")
                for index, key in enumerate(self.units, 1):
                    xml = ET.fromstring(archive.read(f"ppt/slides/slide{index}.xml"))
                    ns = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main", "a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
                    if xml.findall(".//p:pic", ns) and not any(n.native_placeholder == 'picture' for n in self.contents[key].nodes):
                        issues.append("Raster/image flattening found in native slide")
                    actual = ''.join(n.text or '' for n in xml.findall(".//a:t", ns))
                    expected = [n.text for n in self.contents[key].nodes if n.kind == "text" and n.layer == 'slide']
                    if any(t not in actual for t in expected):
                        issues.append("Native editable text missing")
                    if not xml.findall(".//p:sp", ns) and not xml.findall('.//p:graphicFrame',ns):
                        issues.append("Native editable shape tree missing")
            checks.append("Native PowerPoint render plus OOXML editable text/shapes (no picture flattening)")
            from .pptx_support import verify_native
            native_checks, native_issues = verify_native(self)
            checks.extend(native_checks)
            issues.extend(native_issues)
        self.qa = DesignQAReport(status="FAIL" if issues else "PASS", checks=checks, issues=issues,
            evidence=[m for m in self.manifests if m.role in {"preview", "evidence"}])
        return self.qa
