"""Focused regressions for the former metadata-only visual PASS paths."""
import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PLUGIN = next(p for p in HERE.parents if (p / 'scripts' / 'design_brain_batch_similarity_audit.py').is_file())
sys.path.append(str(PLUGIN / 'scripts'))
from test_design_brain_visual_inspect import Fixture
from design_brain_post_build_audit import visual_audit


class PostBuildVisualTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def audit(self, **kwargs):
        return visual_audit(self.f.root, **kwargs)

    def test_nonempty_screenshot_directory_is_limited(self):
        self.assertEqual(self.audit(screenshot_dir=str(self.f.views))['status'], 'LIMITED')

    def test_empty_legacy_report_cannot_pass(self):
        (self.f.root / 'visual-qa.json').write_text('{}')
        self.assertEqual(self.audit()['status'], 'LIMITED')

    def test_array_null_malformed_legacy_reports_fail(self):
        for value in ['[]', 'null', '{broken']:
            with self.subTest(value=value):
                (self.f.root / 'visual-qa.json').write_text(value)
                self.assertEqual(self.audit()['status'], 'FAIL')

    def test_explicit_invalid_or_unreviewed_manifest_fails(self):
        self.assertEqual(self.audit(inspection=str(self.f.manifest), expected_artifact=str(self.f.artifact))['status'], 'FAIL')
        self.assertEqual(self.audit(inspection=str(self.f.root / 'missing.json'))['status'], 'FAIL')

    def test_current_observed_fixture_pass_and_bound_manifest_reference(self):
        self.f.crop(); self.f.approve_fixture()
        r = self.audit(inspection=str(self.f.manifest), expected_artifact=str(self.f.artifact))
        self.assertEqual(r['status'], 'PASS'); self.assertEqual(len(r['visualInspectionManifests']), 1)
        self.assertEqual(r['visualInspectionManifests'][0]['path'], str(self.f.manifest))
        self.assertIn('cannot prove actual seeing', r['limitation'])

    def test_stale_or_wrong_target_and_critical_unresolved_fail(self):
        self.f.crop(); self.f.approve_fixture(); m = self.f.read(); m['reviews'][0]['verdict'] = 'unresolved'; self.f.write(m)
        self.assertEqual(self.audit(inspection=str(self.f.manifest), expected_artifact=str(self.f.artifact))['status'], 'FAIL')
        self.assertEqual(self.audit(inspection=str(self.f.manifest), expected_artifact=str(self.f.image))['status'], 'FAIL')

    def test_legacy_critical_defect_still_blocks_current_manifest(self):
        self.f.crop(); self.f.approve_fixture()
        (self.f.root / 'visual-qa.json').write_text(json.dumps({'issues': [{'type': 'text overlap', 'severity': 'critical'}]}))
        self.assertEqual(self.audit(inspection=str(self.f.manifest), expected_artifact=str(self.f.artifact))['status'], 'FAIL')


if __name__ == '__main__':
    unittest.main(verbosity=2)
