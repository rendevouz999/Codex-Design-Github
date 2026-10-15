"""Synthetic, offline inspection-integrity regressions; no visual-quality verdict."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

sys.dont_write_bytecode = True
from PIL import Image
import design_brain_visual_inspect as vi

TEST_ROOT = next((p / 'engineer' / 'test-tmp' for p in Path(__file__).resolve().parents if p.name == 'visual-inspection-upgrade_20261013'), None)
if TEST_ROOT:
    TEST_ROOT.mkdir(parents=True, exist_ok=True)


class Fixture:
    def __init__(self, count=1, size=(48, 27), artifact=None):
        self.tmp = tempfile.TemporaryDirectory(prefix='visual-test-', dir=TEST_ROOT)
        self.root = Path(self.tmp.name).resolve()
        if TEST_ROOT:
            assert self.root.is_relative_to(TEST_ROOT.resolve())
        self.artifact = Path(artifact).resolve() if artifact else self.root / 'fixture.pptx'
        if artifact:
            assert self.artifact.is_file(), 'Caller must supply an existing fixture artifact; it is never overwritten'
        else:
            xml = '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldIdLst>'
            xml += ''.join(f'<p:sldId id="{n}" />' for n in range(count)) + '</p:sldIdLst></p:presentation>'
            with ZipFile(self.artifact, 'w') as z:
                z.writestr('ppt/presentation.xml', xml)
        self.image = self.root / 'source.png'
        img = Image.new('RGBA', size)
        img.putdata([(x % 255, (x * 7) % 255, (x * 13) % 255, 255) for x in range(size[0] * size[1])]); img.save(self.image)
        self.inventory = None
        if artifact:
            names = vi.pptx_frames(self.artifact) or ['slide-001']
            self.inventory = self.root / 'render-inventory.json'
            self.inventory.write_text(json.dumps({'artifact_sha256': vi.file_ref(self.artifact)['sha256'],
                'method': 'Synthetic offline test raster; no actual artifact rendering or visual inspection claimed.',
                'frames': [{'id': name, 'image': vi.file_ref(self.image)} for name in names]}))
        self.manifest = self.root / 'inspection.json'; self.views = self.root / 'views'
        self.prepare()

    def prepare(self, frame_id='slide-001', **extra):
        return vi.prepare(self.image, self.artifact, frame_id, self.views, self.manifest,
                          render_method='Synthetic offline fixture raster; no native product rendering claimed.', inventory=self.inventory, **extra)

    def read(self):
        return vi.load(self.manifest)

    def write(self, m):
        self.manifest.write_text(json.dumps(m, indent=2), encoding='utf-8')

    def crop(self, view_id='overview', name='detail', requested=None, edge=80, frame_id='slide-001'):
        frame = next(f for f in self.read()['frames'] if f['id'] == frame_id)
        v = next(v for v in frame['views'] if v['id'] == view_id)
        requested = requested or [0, 0, max(1, v['size_px'][0] // 2), max(1, v['size_px'][1] // 2)]
        return vi.crop(self.manifest, frame_id, view_id, requested, name, edge)

    def approve_fixture(self):
        m = self.read(); m['reviews'] = []
        timestamp = datetime(2026, 10, 13, tzinfo=timezone.utc)
        for f in m['frames']:
            views = {v['id']: v for v in f['views']}
            detail_id = next(v['id'] for v in f['views'] if v['kind'] == 'detail')
            for c in [c for c in m['checks'] if c['frame_id'] == f['id']]:
                for role in ['engineer', 'main']:
                    sequence = ['overview', detail_id, 'overview'] if c['requires_detail'] else ['overview']
                    actual = [{'view_id': name, 'sha256': views[name]['file']['sha256'], 'tool': 'view_image',
                               'actually_viewed': True, 'viewed_at': (timestamp + timedelta(seconds=i)).isoformat(),
                               'evidence_note': 'Synthetic test attestation only, not an actual product review.'}
                              for i, name in enumerate(sequence)]
                    m['reviews'].append({'role': role, 'frame_id': f['id'], 'artifact_sha256': m['artifact']['sha256'],
                                         'source_sha256': f['source']['sha256'], 'check_id': c['id'], 'check_sha256': vi.digest(c),
                                         'view_ids': list(set(sequence)), 'actual_views': actual, 'verdict': 'pass',
                                         'observation': 'Synthetic fixture observation: colored source pixels and crop boundaries agree.'})
        m['main_approval'] = {'verdict': 'accept', 'artifact_sha256': m['artifact']['sha256'],
                              'check_set_sha256': vi.digest(m['checks']), 'reason': 'Synthetic regression acceptance only; no product-quality claim.'}
        self.write(m)

    def verify(self, **kwargs):
        return vi.verify_manifest(self.manifest, expected_artifact=self.artifact, **kwargs)

    def write_receipt(self):
        """Test-only accepted integrity fixture; never a real inspection attestation."""
        for name in self.read()['coverage']['expected_frame_ids']:
            if name not in {f['id'] for f in self.read()['frames']}:
                self.prepare(name)
            frame = next(f for f in self.read()['frames'] if f['id'] == name)
            if not any(v['kind'] == 'detail' for v in frame['views']):
                self.crop(frame_id=name)
        self.approve_fixture()
        assert self.verify()['status'] == 'PASS'
        self.post_receipt = self.root / 'post-build.json'
        self.post_receipt.write_text(json.dumps({'finalStatus': 'READY',
            'auditPasses': {'pass3VisualLayoutQA': 'PASS'},
            'visualInspectionManifests': [vi.file_ref(self.manifest)],
            'scope': 'Synthetic TEST ONLY review attestations; not real source rendering or product acceptance.'}))
        return self.post_receipt

    def close(self):
        self.tmp.cleanup()


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def complete(self):
        self.f.crop(); self.f.approve_fixture()

    def test_generated_evidence_never_reviews_or_passes(self):
        m = self.f.read()
        self.assertEqual(m['status'], 'EVIDENCE_PREPARED'); self.assertEqual(m['reviews'], [])
        self.assertEqual(m['review_status'], 'UNVERIFIED'); self.assertEqual(self.f.verify()['status'], 'FAIL')

    def test_current_complete_receipt_pass_is_integrity_only(self):
        self.complete(); r = self.f.verify()
        self.assertEqual((r['status'], r['evidence_status'], r['review_status']), ('PASS', 'VERIFIED', 'MAIN_ACCEPTED'))
        self.assertIn('do not cryptographically prove', r['limitation'])

    def test_original_pixels_nested_mapping_independent_scales(self):
        other = Fixture(size=(3, 7))
        try:
            # A view rounding to2x4 has different independent X/Y scales.
            m = other.read(); v = m['frames'][0]['views'][0]
            v['size_px'] = [2, 4]
            Image.open(other.image).resize((2, 4), Image.Resampling.LANCZOS).save(v['file']['path'])
            v['file'] = vi.file_ref(v['file']['path']); other.write(m)
            a = other.crop(requested=[0, 1, 2, 3], edge=8)['view']
            self.assertEqual(a['source_box_px'], [0, 1, 3, 6])
            b = other.crop(view_id='detail', name='nested', requested=[1, 2, 4, 6], edge=9)['view']
            self.assertEqual(b['source_box_px'], [0, 2, 3, 5])
            vi.validate_evidence(other.read())
        finally:
            other.close()

    def test_exif_orientation_maps_display_original(self):
        image = self.f.root / 'oriented.jpg'; img = Image.new('RGB', (12, 8), '#7a22bb')
        exif = Image.Exif(); exif[274] = 6; img.save(image, exif=exif)
        artifact = self.f.root / 'single.bin'; artifact.write_bytes(b'one static screenshot')
        inventory = self.f.root / 'inventory.json'
        inventory.write_text(json.dumps({'artifact_sha256': vi.file_ref(artifact)['sha256'], 'method': 'Synthetic EXIF regression image', 'frames': [{'id': 'image-1', 'image': vi.file_ref(image)}]}))
        manifest = self.f.root / 'exif.json'
        vi.prepare(image, artifact, 'image-1', self.f.root / 'exifviews', manifest, inventory=inventory)
        self.assertEqual(vi.load(manifest)['frames'][0]['oriented_size_px'], [8, 12]); vi.validate_evidence(vi.load(manifest))

    def test_invalid_boxes_no_clipping(self):
        for requested in [[-1, 0, 5, 5], [0, 0, 99, 99], [5, 0, 1, 2], [0, 0, 0, 2], [True, 0, 2, 2], [0.0, 0, 2, 2]]:
            with self.subTest(box=requested), self.assertRaises(ValueError):
                self.f.crop(requested=requested)

    def test_whole_view_duplicate_is_not_detail(self):
        with self.assertRaises(ValueError):
            self.f.crop(requested=[0, 0, 48, 27])

    def test_stale_original_and_artifact_hashes(self):
        self.complete(); self.f.image.write_bytes(self.f.image.read_bytes() + b'new metadata')
        self.assertEqual(self.f.verify()['status'], 'FAIL')
        self.f.artifact.write_bytes(self.f.artifact.read_bytes() + b'changed source')
        self.assertEqual(self.f.verify()['evidence_status'], 'INVALID')

    def test_self_claimed_view_hash_cannot_hide_wrong_pixels(self):
        self.complete(); m = self.f.read(); v = m['frames'][0]['views'][1]
        Image.new('RGBA', v['size_px'], 'red').save(v['file']['path']); v['file'] = vi.file_ref(v['file']['path']); self.f.write(m)
        self.assertIn('pixels do not match', self.f.verify()['issues'][0])

    def test_stretched_or_letterboxed_view_rejected(self):
        self.f.crop(); m = self.f.read(); m['frames'][0]['views'][1]['size_px'] = [9, 90]; self.f.write(m)
        self.assertIn('Stretched/letterboxed', self.f.verify()['issues'][0])

    def test_incomplete_twenty_slide_artifact_cannot_pass(self):
        other = Fixture(count=20)
        try:
            other.crop(); other.approve_fixture()
            self.assertIn('every artifact frame', other.verify()['issues'][0])
            m = other.read(); m['coverage']['expected_frame_ids'] = ['slide-001']; other.write(m)
            self.assertIn('actual PPTX slide count', other.verify()['issues'][0])
        finally:
            other.close()

    def test_missing_checks_and_role_observation(self):
        self.complete(); original = self.f.read(); m = copy.deepcopy(original); m['checks'] = []; self.f.write(m)
        self.assertEqual(self.f.verify()['status'], 'FAIL')
        m = original; m['reviews'] = [r for r in m['reviews'] if r['role'] == 'engineer']; self.f.write(m)
        self.assertEqual(self.f.verify()['status'], 'FAIL')

    def test_missing_actual_view_and_wrong_sequence(self):
        self.complete(); m = self.f.read(); r = next(r for r in m['reviews'] if r['check_id'].endswith(':detail'))
        r['actual_views'][0]['actually_viewed'] = False; self.f.write(m)
        self.assertEqual(self.f.verify()['status'], 'FAIL')
        r['actual_views'][0]['actually_viewed'] = True; r['actual_views'] = r['actual_views'][1:]; self.f.write(m)
        self.assertIn('overview', self.f.verify()['issues'][0])

    def test_nonchronological_views(self):
        self.complete(); m = self.f.read(); r = next(r for r in m['reviews'] if len(r['actual_views']) > 1)
        r['actual_views'][1]['viewed_at'] = r['actual_views'][0]['viewed_at']; self.f.write(m)
        self.assertIn('chronological', self.f.verify()['issues'][0])

    def test_unresolved_critical_and_missing_main_approval(self):
        self.complete(); m = self.f.read(); m['reviews'][0]['verdict'] = 'unresolved'; self.f.write(m)
        self.assertEqual(self.f.verify()['review_status'], 'REVISE_REQUIRED')
        m['reviews'][0]['verdict'] = 'pass'; m['main_approval'] = None; self.f.write(m)
        self.assertEqual(self.f.verify()['status'], 'FAIL')

    def test_expected_target_path_hash_required(self):
        self.complete(); other = self.f.root / 'other.pptx'; other.write_bytes(self.f.artifact.read_bytes())
        self.assertEqual(vi.verify_manifest(self.f.manifest)['status'], 'FAIL')
        self.assertEqual(vi.verify_manifest(self.f.manifest, expected_artifact=other)['status'], 'FAIL')

    def test_render_method_required(self):
        self.complete(); m = self.f.read(); m['frames'][0]['render_binding']['method'] = ''; self.f.write(m)
        self.assertIn('provenance method', self.f.verify()['issues'][0])

    def test_no_overwrite_source_views_or_manifest_paths(self):
        self.f.crop(); before = vi.file_ref(self.f.image)
        with self.assertRaises(ValueError):
            self.f.crop(name='detail')
        self.assertEqual(before, vi.file_ref(self.f.image))
        with self.assertRaises(ValueError):
            vi.save_manifest(self.f.image, self.f.read())
        path = self.f.views / 'slide-001--blocked.png'; path.write_bytes(b'keep')
        with self.assertRaises(FileExistsError):
            self.f.crop(name='blocked')
        self.assertEqual(path.read_bytes(), b'keep')

    def test_atomic_manifest_failure_preserves_existing_bytes(self):
        before = self.f.manifest.read_bytes()
        with patch.object(vi.os, 'replace', side_effect=OSError('synthetic interruption')):
            with self.assertRaises(OSError):
                self.f.crop()
        self.assertEqual(before, self.f.manifest.read_bytes())
        self.assertEqual(list(self.f.root.glob('*.tmp')), [])

    def test_generated_square_output_resource_limit_before_allocate(self):
        with self.assertRaises(ValueError):
            vi.add_view({'id': 'square', 'views': []}, Image.new('RGBA', (8, 8)), self.f.root / 'too-big', 'detail', 'detail', [0, 0, 8, 8], 8192)
        self.assertFalse((self.f.root / 'too-big').exists())

    def test_invalid_json_and_zip_are_structured_failures(self):
        original = self.f.read()
        for value in [None, [], {}, {'schema_version': 1}]:
            self.f.manifest.write_text(json.dumps(value)); self.assertEqual(self.f.verify()['status'], 'FAIL')
        self.f.artifact.write_text('not a zip')
        original['artifact'] = vi.file_ref(self.f.artifact); self.f.write(original)
        self.assertEqual(self.f.verify()['status'], 'FAIL')
        cmd = [sys.executable, str(Path(vi.__file__)), 'verify', '--manifest', str(self.f.manifest), '--artifact', str(self.f.artifact), '--json']
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1); self.assertEqual(json.loads(proc.stdout)['status'], 'FAIL'); self.assertNotIn('Traceback', proc.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
