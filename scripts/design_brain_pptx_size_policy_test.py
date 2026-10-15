"""Regression checks for the PPTX-only physical-size default and source preservation.

Run with the installed presentation Python. Fixtures live in temporary directories;
the existing native size-proof deck is read only when present.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT / "skills/presentation-deck"
NATIVE = CAP / "runtime/native"
sys.path[:0] = [str(NATIVE), str(CAP / "runtime"), str(ROOT / "scripts")]

from config import CANVAS_FORMATS
from design_brain_process_utils import run_command
from pptx_size_policy import (
    CONTRACT_FILE, DEFAULT_FORMAT, check_pptx_canvas,
    check_source_canvas, new_contract, read_contract, write_contract,
)
from project_management.cli import ProjectManager
from project_utils import get_project_info
from routing import route_pptx

_spec = importlib.util.spec_from_file_location("pptx_size_wrapper_under_test", CAP / "runtime/presentation.py")
presentation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(presentation)


class PptxSizePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="codex-pptx-size-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name).resolve()
        self.owner = {"root": str(CAP), "nativeScripts": str(NATIVE),
                      "pythonCommand": [sys.executable]}

    def project(self, name="deck_20261012", contract=True):
        path = self.work / name
        (path / "svg_output").mkdir(parents=True)
        if contract:
            write_contract(path, new_contract())
        return path

    def svg(self, project, viewbox="0 0 960 540", name="01_slide.svg"):
        path = project / "svg_output" / name
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"><text x="30" y="50">Editable fixture</text></svg>', encoding="utf-8")
        return path

    def cli_init(self, project, *options):
        result = run_command(
            [sys.executable, "-B", str(CAP / "runtime/presentation.py"),
             "--python", sys.executable, "--timeout", "20", "init", str(project), *options],
            cwd=ROOT, timeout=35, isolate_process_group=True,
            env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"},
        )
        self.assertFalse(result.timedOut, result.stderrExcerpt)
        self.assertEqual(result.returncode, 0, result.stdout[-5000:] + result.stderr[-5000:])
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["designReadiness"], "NOT_EVALUATED")
        return receipt

    def test_actual_default_and_quick_init_persist_exact_canvas(self):
        for mode in ("default", "quick"):
            with self.subTest(mode=mode):
                project = self.work / f"{mode}_20261012"
                receipt = self.cli_init(project, "--mode", mode)
                contract = read_contract(project)
                self.assertEqual(contract["format"], DEFAULT_FORMAT)
                self.assertEqual(contract["viewBox"], "0 0 960 540")
                self.assertEqual((contract["widthEmu"], contract["heightEmu"]), (9144000, 5143500))
                self.assertEqual(contract["selection"], "standing-user-default")
                self.assertEqual(receipt["pptxCanvas"], contract)
                self.assertTrue((project / "svg_output").is_dir())
                self.assertEqual(get_project_info(str(project))["format"], DEFAULT_FORMAT)
                self.assertEqual((project / "README.md").exists(), mode == "default")

    def test_actual_explicit_registered_override(self):
        project = self.work / "registered_20261012"
        self.cli_init(project, "--format", "ppt169onscreen")
        contract = read_contract(project)
        self.assertEqual(contract["format"], "ppt169onscreen")
        self.assertEqual(contract["viewBox"], "0 0 960 540")
        self.assertEqual((contract["widthEmu"], contract["heightEmu"]), (9144000, 5143500))
        self.assertEqual(contract["selection"], "explicit")

    def test_old_pptx_presets_are_removed_and_rejected(self):
        for old in ("ppt169", "ppt43"):
            with self.subTest(format=old):
                self.assertNotIn(old, CANVAS_FORMATS)
                with self.assertRaises(ValueError):
                    new_contract(old)
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    presentation.parser().parse_args(["init", str(self.work / "old_20261012"), "--format", old])

    def test_actual_explicit_custom_override(self):
        project = self.work / "custom_20261012"
        self.cli_init(project, "--size-inches", "11", "6.25")
        contract = read_contract(project)
        self.assertIsNone(contract["format"])
        self.assertEqual(contract["viewBox"], "0 0 1056 600")
        self.assertEqual((contract["widthEmu"], contract["heightEmu"]), (10058400, 5715000))
        self.assertEqual(get_project_info(str(project))["format"], "custom")
        self.svg(project, contract["viewBox"])
        self.assertEqual(check_source_canvas(project), contract)

    def test_plain_directory_name_supports_registered_spec_scaffold(self):
        project = self.project()
        manager = ProjectManager(self.work)
        for artifact in ("design_spec", "spec_lock"):
            path = Path(manager.scaffold_artifact(str(project), artifact))
            self.assertIn("0 0 960 540", path.read_text(encoding="utf-8"))
        self.assertEqual(get_project_info(str(project))["canvas_info"]["width"], 960)

    def test_invalid_or_conflicting_explicit_size_rejected(self):
        for dimensions in (("0", "5"), ("-10", "5"), ("NaN", "5"),
                           ("Infinity", "5"), ("57", "5"), ("0.5", "5"), ("bad", "5")):
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                new_contract(size_inches=dimensions)
        with self.assertRaises(ValueError):
            new_contract("ppt169onscreen", ("10", "5.625"))
        with self.assertRaises(ValueError):
            new_contract("missing-preset")

    def test_invalid_and_mismatched_project_contracts_rejected(self):
        project = self.project(contract=False)
        baseline = new_contract()
        cases = [[], {}, {**baseline, "schema": "unknown"},
                 {**baseline, "outputFormat": "html"},
                 {**baseline, "widthEmu": 12192000},
                 {**baseline, "format": "ppt169"},
                 {**baseline, "format": "unknown"},
                 {**baseline, "viewBox": "0 0 1280 720"},
                 {**baseline, "viewBox": 960}]
        for case in cases:
            with self.subTest(case=case):
                (project / CONTRACT_FILE).write_text(json.dumps(case), encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_contract(project)

    def test_contract_write_refuses_overwrite(self):
        project = self.project()
        before = (project / CONTRACT_FILE).read_bytes()
        with self.assertRaises(FileExistsError):
            write_contract(project, new_contract(size_inches=("11", "6.25")))
        self.assertEqual((project / CONTRACT_FILE).read_bytes(), before)

    def test_wrong_svg_canvas_rejected_before_check_and_export(self):
        project = self.project()
        self.svg(project, "0 0 1280 720")
        with self.assertRaises(ValueError):
            check_source_canvas(project)
        for action in ("check", "export"):
            argv = [action, str(project), "--mode", "quick"]
            if action == "export":
                argv += ["--output", str(self.work / "wrong.pptx")]
            with self.subTest(action=action), self.assertRaises(ValueError):
                presentation.prepare(presentation.parser().parse_args(argv), self.owner)
        self.assertFalse((self.work / "wrong.pptx").exists())

    def test_mixed_source_canvases_rejected(self):
        project = self.project()
        self.svg(project)
        self.svg(project, "0 0 1280 720", "02_wrong.svg")
        with self.assertRaises(ValueError):
            check_source_canvas(project)

    def test_wrong_template_canvas_rejected_before_preview(self):
        project = self.project()
        (project / "templates").mkdir()
        (project / "templates/01_layout.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720"/>',
            encoding="utf-8",
        )
        args = presentation.parser().parse_args([
            "template-preview", str(project), "--output", str(self.work / "wrong-template.pptx")])
        with self.assertRaises(ValueError):
            presentation.prepare(args, self.owner)
        self.assertFalse((self.work / "wrong-template.pptx").exists())

    def test_real_native_proof_has_exact_ooxml_size_without_mutation(self):
        proof = ROOT / "output/pptx-size-reference-check-20261012/On_Screen_Show_16x9_10x5.625_Size_Proof.pptx"
        if not proof.is_file():
            self.skipTest("Local verified proof is not present in this checkout")
        before = hashlib.sha256(proof.read_bytes()).hexdigest()
        result = check_pptx_canvas(proof, new_contract())
        self.assertEqual(result, {"status": "PASS", "widthEmu": 9144000,
                                  "heightEmu": 5143500, "type": "screen16x9"})
        self.assertEqual(hashlib.sha256(proof.read_bytes()).hexdigest(), before)

    def test_ooxml_wrong_size_type_or_missing_size_rejected(self):
        bodies = [
            '<p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>',
            '<p:sldSz cx="9144000" cy="5143500" type="custom"/>',
            '',
        ]
        for index, body in enumerate(bodies):
            target = self.work / f"invalid-{index}.pptx"
            with ZipFile(target, "w") as package:
                package.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">' + body + '</p:presentation>')
            with self.subTest(index=index), self.assertRaises(ValueError):
                check_pptx_canvas(target, new_contract())

    def test_preexisting_project_without_contract_keeps_legacy_canvas(self):
        project = self.project("legacy_ppt169_20261012", contract=False)
        self.svg(project, "0 0 1280 720")
        self.assertIsNone(check_source_canvas(project))
        self.assertEqual(get_project_info(str(project))["format"], "unknown")
        for action in ("check", "export"):
            argv = [action, str(project), "--mode", "quick"]
            if action == "export":
                argv += ["--output", str(self.work / "legacy.pptx")]
            presentation.prepare(presentation.parser().parse_args(argv), self.owner)
        self.assertFalse((project / CONTRACT_FILE).exists())

    def test_import_and_roundtrip_do_not_apply_new_default(self):
        source = self.work / "source.pptx"
        source.write_bytes(b"read-only path selection fixture")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        project = self.work / "imported"
        args = presentation.parser().parse_args(["import-pptx", str(project), "--source", str(source)])
        command, resolved, _ = presentation.prepare(args, self.owner)
        self.assertIn("--roundtrip", command)
        self.assertEqual(resolved, project)
        self.assertFalse(project.exists())
        (project / "authoring-svg-flat").mkdir(parents=True)
        args = presentation.parser().parse_args(["export-roundtrip", str(project), "--output", str(self.work / "edited.pptx")])
        command, _, _ = presentation.prepare(args, self.owner)
        self.assertIn("--roundtrip", command)
        self.assertFalse((project / CONTRACT_FILE).exists())
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_generic_project_init_remains_size_neutral(self):
        manager = ProjectManager(self.work)
        project = Path(manager.init_project("generic_20261012", quick_generate=True))
        self.assertIsNone(read_contract(project))
        self.assertEqual(get_project_info(str(project))["format"], "unknown")

    def test_other_formats_and_web_stage_remain_unchanged(self):
        expected = {"wechat": (900, 383), "xiaohongshu": (1242, 1660),
                    "moments": (1080, 1080), "story": (1080, 1920),
                    "banner": (1920, 1080), "a4": (1240, 1754)}
        for key, dimensions in expected.items():
            with self.subTest(format=key):
                self.assertEqual((CANVAS_FORMATS[key]["width"], CANVAS_FORMATS[key]["height"]), dimensions)
        schema = json.loads((CAP / "resources/web-deck/deck-plan-schema.json").read_text(encoding="utf-8"))
        stage = schema["$defs"]["stage"]["properties"]
        self.assertEqual((stage["width"]["const"], stage["height"]["const"]), (1920, 1080))
        self.assertEqual(route_pptx("ubah PPTX ke HTML")["artifact"], "web")
        for task in ("buat Google Slides", "buat Keynote", "buat Figma slides"):
            with self.subTest(task=task):
                self.assertEqual(route_pptx(task)["artifact"], "other-slides")


if __name__ == "__main__":
    unittest.main(verbosity=2)
