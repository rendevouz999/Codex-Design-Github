import argparse
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import design_brain_context_packet as cp
import design_brain_modules as modules

ROOT = Path(__file__).resolve().parents[1]
class LoadingTests(unittest.TestCase):
    def test_dual_mode_contains_web_sources(self):
        result = modules.build_selection(task='Create both PPTX and HTML web deck')
        self.assertIn('skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md', result['sourceFiles'])
    def test_review_does_not_reload_planning_catalogs(self):
        args = argparse.Namespace(task='Review PPTX presentation', template_type='', niche='',
            target_buyer='', visual_mood='', role='main', stage='review', reference=False,
            naming=False, review=True)
        reads = cp.packet_sources(args, cp.infer_triggers(args))
        self.assertIn('.design-brain/VISUAL_INSPECTION_PROTOCOL.md', reads)
        # Current owner contract keeps the complete fresh-session guide.
        self.assertIn('PRESENTATION_TEMPLATE_GUIDE.md', reads)
        self.assertFalse(any('seed-packs' in path for path in reads))
        self.assertNotIn('.design-brain/DESIGN_SOUL.md', reads)
    def test_cli_uses_review_stage_owner(self):
        run = subprocess.run([sys.executable, str(ROOT/'scripts/design_brain_context_packet.py'), '--task', 'Review PPTX presentation', '--stage', 'review', '--review', '--dry-run'], text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        required = run.stdout.split('## Required Source-Of-Truth Reads',1)[1].split('## Design-Anything Module Selection',1)[0]
        self.assertIn('.design-brain/VISUAL_INSPECTION_PROTOCOL.md', required)
        self.assertNotIn('seed-packs', required)
        self.assertNotIn('.design-brain/DESIGN_SOUL.md', required)
    def test_path_condition_dedup(self):
        self.assertEqual(cp.unique(['a.md when needed', 'a.md']), ['a.md'])
    def test_hook_paths_are_atomic(self):
        temporary = tempfile.TemporaryDirectory(prefix='hook path ')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / ('long folder ' * 9).strip()
        # Windows test hosts may forbid symlink creation. Use physical policy files
        # while retaining the exact root-with-spaces routing obligation.
        for rel in ('.design-brain/PRESENTATION_SCOPE.json', 'skills/presentation-deck/resources/routing.json'):
            target = root / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)
        run = subprocess.run(['node', str(ROOT/'hooks/brain-design-route.mjs')], input=json.dumps({'prompt':'create a PowerPoint presentation'}), text=True, capture_output=True, env=dict(os.environ, CLAUDE_PLUGIN_ROOT=str(root)))
        self.assertEqual(run.returncode, 0)
        self.assertIn('Read first:', run.stdout)
        self.assertIn('PPTX_IMAGE_SELECTION_POLICY.md', run.stdout)
        self.assertIn('PLUGIN_ROOT:', run.stdout)
        self.assertIn(root.as_posix(), run.stdout)
        self.assertIn('/skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md', run.stdout)
if __name__ == '__main__': unittest.main()
