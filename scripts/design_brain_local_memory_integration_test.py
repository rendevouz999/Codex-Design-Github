"""Local-memory routing, distribution and update-preservation regressions."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
import design_brain_export_package as package
import design_brain_package_integrity as integrity
import install_design_brain as installer

ROOT = Path(__file__).resolve().parents[1]


class LocalMemoryIntegrationTests(unittest.TestCase):
    def test_live_store_and_notes_never_enter_public_package(self):
        for suffix in ("memory.sqlite3", "memory.sqlite3-wal", "memory.sqlite3-shm",
                       "memory.sqlite3-journal", "adapter.sqlite3", "adapter.sqlite3-journal",
                       "supabase-reader.secret.json", "supabase-writer.secret.json", "requests/policy.json", "README.md"):
            relative = ".design-brain/local-memory/" + suffix
            with self.subTest(path=relative):
                self.assertFalse(package.should_include(ROOT / relative, ROOT))
                self.assertTrue(integrity.forbidden_zip_reason(relative))
        self.assertTrue(package.should_include(ROOT / ".design-brain/LOCAL_MEMORY_POLICY.md", ROOT))
        self.assertTrue(package.should_include(ROOT / "scripts/design_brain_local_memory.py", ROOT))

    def test_installer_discovers_memory_implementation_but_not_runtime_data(self):
        managed = installer.manifest_managed_files(ROOT, set())
        targets = {entry.target for entry in managed}
        self.assertIn(".design-brain/LOCAL_MEMORY_POLICY.md", targets)
        self.assertIn("scripts/design_brain_local_memory.py", targets)
        self.assertIn("scripts/design_brain_memory_adapter.py", targets)
        self.assertIn("scripts/design_brain_memory_supabase.sql", targets)
        self.assertIn("capabilities/design-memory/capability.json", targets)
        self.assertIn("capabilities/design-memory/supabase.project.json", targets)
        self.assertFalse(any(path.startswith(".design-brain/local-memory/") for path in targets))

    def test_forced_update_preserves_existing_local_history(self):
        with tempfile.TemporaryDirectory(prefix="local-memory-install-") as temporary:
            base = Path(temporary)
            source, target = base / "source", base / "target"
            relative = ".design-brain/local-memory/memory.sqlite3"
            for root, value in ((source, b"other workspace history"), (target, b"existing owner history")):
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_bytes(value)
            outcome = installer.copy_managed_file(source, target, installer.ManagedFile(relative, relative),
                                                  force=True, dry_run=False, include_history=True)
            self.assertIn("PRESERVED", outcome)
            self.assertEqual((target / relative).read_bytes(), b"existing owner history")
            self.assertFalse(list((target / relative).parent.glob("*.bak-*")))

    def test_hook_reminds_local_read_update_without_routing_unrelated_prompt(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node not installed; hook runtime is unverified")
        environment = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(ROOT))
        for prompt, expected in (("buat template PowerPoint", True), ("berapa hasil 2 tambah 2", False)):
            with self.subTest(prompt=prompt):
                result = subprocess.run([node, str(ROOT / "hooks/brain-design-route.mjs")],
                                        input=json.dumps({"prompt": prompt}), text=True, capture_output=True,
                                        env=environment, timeout=8, check=True)
                if expected:
                    self.assertIn("LOCAL_MEMORY_POLICY.md", result.stdout)
                    self.assertIn("Main updates/readbacks", result.stdout)
                    self.assertIn("presentation-deck/workflows/native.md", result.stdout)
                    self.assertIn("reasoning_effort=xhigh", result.stdout)
                else:
                    self.assertEqual(result.stdout, "")
        startup = subprocess.run([node, str(ROOT / "hooks/brain-design-activate.mjs")],
                                 text=True, capture_output=True, env=environment, timeout=8, check=True)
        self.assertIn("LOCAL_MEMORY_POLICY.md", startup.stdout)
        self.assertIn("No Agent Core memory dependency", startup.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
