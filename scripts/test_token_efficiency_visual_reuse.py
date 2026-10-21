"""Synthetic evidence only; these checks do not claim actual visual acceptance."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from zipfile import ZipFile
from test_design_brain_visual_inspect import Fixture
import design_brain_visual_inspect as vi

class ReuseTests(unittest.TestCase):
    def setup_pair(self):
        old = Fixture(count=2); self.addCleanup(old.tmp.cleanup)
        with ZipFile(old.artifact, 'w') as z:
            z.writestr('ppt/presentation.xml', '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><p:sldIdLst><p:sldId id="1" r:id="rId1"/><p:sldId id="2" r:id="rId2"/></p:sldIdLst></p:presentation>')
            z.writestr('ppt/_rels/presentation.xml.rels', '<Relationships><Relationship Id="rId1" Target="slides/slide1.xml"/><Relationship Id="rId2" Target="slides/slide2.xml"/></Relationships>')
            z.writestr('ppt/slides/slide1.xml', '<slide>one</slide>')
            z.writestr('ppt/slides/slide2.xml', '<slide>two</slide>')
        old.manifest = old.root/'original-inspection.json'; old.views = old.root/'original-views'
        context = old.root/'review-context.json'; context.write_text('{"brief":"fixture","policy":"v1","renderer":"fixture"}')
        old.prepare(review_context=context); old.prepare('slide-002', review_context=context)
        old.crop(); old.crop(frame_id='slide-002'); old.approve_fixture()
        target = old.root/'changed.pptx'
        with ZipFile(old.artifact) as src, ZipFile(target,'w') as out:
            for name in src.namelist(): out.writestr(name, '<slide>changed</slide>' if name == 'ppt/slides/slide2.xml' else src.read(name))
        new = Fixture(artifact=target); self.addCleanup(new.tmp.cleanup)
        new.prepare('slide-002', review_context=context)
        new.crop(); new.crop(frame_id='slide-002')
        return old, new
    def test_reuse_only_unchanged_dependencies_and_no_final_approval(self):
        old,new = self.setup_pair()
        result = vi.reuse_reviews(old.manifest,new.manifest)
        self.assertEqual(result['reused_frames'], ['slide-001'])
        self.assertEqual(result['review_required_frames'], ['slide-002'])
        self.assertIsNone(new.read()['main_approval'])
        self.assertEqual(new.verify()['status'], 'FAIL')
        reused = copy.deepcopy(new.read()['reviews'])
        new.approve_fixture(); payload = new.read()
        payload['reviews'] = reused + [r for r in payload['reviews'] if r['frame_id']=='slide-002']; new.write(payload)
        self.assertEqual(new.verify()['status'], 'PASS')
        payload['reviews'][0]['observation'] += ' forged edit'; new.write(payload)
        self.assertEqual(new.verify()['status'], 'FAIL')
    def test_shared_part_change_invalidates_dependencies(self):
        old,new = self.setup_pair()
        before = vi.frame_dependency_digest(new.artifact, 'slide-001')
        with ZipFile(new.artifact, 'a') as z:
            z.writestr('ppt/theme/theme1.xml', '<theme>different</theme>')
        self.assertNotEqual(before, vi.frame_dependency_digest(new.artifact, 'slide-001'))
    def test_cross_slide_dependency_disables_reuse(self):
        old,new = self.setup_pair()
        with ZipFile(new.artifact, 'a') as z:
            z.writestr('ppt/slides/_rels/slide1.xml.rels', '<Relationships><Relationship Id="zoom" Target="slide2.xml"/></Relationships>')
        self.assertIsNone(vi.frame_dependency_digest(new.artifact, 'slide-001'))
    def test_missing_relationships_disables_reuse(self):
        fixture = Fixture(); self.addCleanup(fixture.tmp.cleanup)
        self.assertIsNone(vi.frame_dependency_digest(fixture.artifact, 'slide-001'))
    def test_no_context_no_reuse(self):
        old,new = self.setup_pair(); p=new.read(); p.pop('review_context');new.write(p)
        self.assertEqual(vi.reuse_reviews(old.manifest,new.manifest)['reused_frames'], [])

    def test_own_notes_backlink_is_not_a_cross_slide_dependency(self):
        old, new = self.setup_pair()
        with ZipFile(new.artifact, 'a') as archive:
            archive.writestr('ppt/slides/_rels/slide1.xml.rels',
              '<Relationships><Relationship Id="n1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide1.xml"/></Relationships>')
            archive.writestr('ppt/notesSlides/notesSlide1.xml', '<notes>own slide one</notes>')
            archive.writestr('ppt/notesSlides/_rels/notesSlide1.xml.rels',
              '<Relationships><Relationship Id="b1" Target="../slides/slide1.xml"/></Relationships>')
        digest = vi.frame_dependency_digest(new.artifact, 'slide-001')
        self.assertIsNotNone(digest)
        changed = new.root / 'notes-changed.pptx'
        with ZipFile(new.artifact) as source, ZipFile(changed, 'w') as output:
            for name in source.namelist():
                value = source.read(name)
                if name == 'ppt/notesSlides/notesSlide1.xml':
                    value = value.replace(b'own slide one', b'changed owned note')
                output.writestr(name, value)
        self.assertNotEqual(digest, vi.frame_dependency_digest(changed, 'slide-001'))

    def test_origin_cache_is_operation_scoped_and_rechecks_inputs(self):
        old, new = self.setup_pair()
        vi.reuse_reviews(old.manifest, new.manifest)
        carried = copy.deepcopy(new.read()['reviews'])
        new.approve_fixture()
        payload = new.read()
        payload['reviews'] = carried + [row for row in payload['reviews'] if row['frame_id'] == 'slide-002']
        new.write(payload)
        with patch.object(vi, 'validate_evidence', wraps=vi.validate_evidence) as observed:
            self.assertEqual(new.verify()['status'], 'PASS')
            self.assertEqual(observed.call_count, 2, 'Target plus one shared origin; no repeated full origin checks')
        origin_view = Path(old.read()['frames'][0]['views'][0]['file']['path'])
        origin_view.write_bytes(origin_view.read_bytes() + b'synthetic drift')
        self.assertEqual(new.verify()['status'], 'FAIL', 'Next operation must reject drifted origin')

if __name__ == '__main__': unittest.main()
