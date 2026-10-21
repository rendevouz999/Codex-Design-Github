"""Offline projection regressions; no live service calls."""
import unittest
import design_brain_memory_adapter_test as fixtures

class ProjectionTests(fixtures.AdapterTests):
    def test_exact_legacy_revision_remains_readable(self):
        fixtures.module.local.init(self.root, 'main')
        fixtures.module.local.put(self.root, self.record, 0, 'main')
        rows = self.reader.read(self.record['id'], 1)['records']
        self.assertEqual([(r['origin'], r['revision']) for r in rows], [('local-legacy', 1)])
        self.assertEqual(rows[0]['content'], self.record['content'])
    def test_summary_default_full_explicit(self):
        self.record['content'] = 'Important decision. ' * 100
        self.save()
        row = self.reader.search()['remote']['records'][0]
        self.assertNotIn('content', row)
        self.assertLessEqual(len(row['excerpt']), 240)
        self.assertEqual(row['content_chars'], len(self.record['content']))
        self.assertEqual(row['full_read']['origin'], 'supabase')
        self.assertEqual(row['review_status'], 'rejected')
        full = self.reader.search(projection='full')['remote']['records'][0]
        self.assertEqual(full['content'], self.record['content'])
        self.assertEqual(self.reader.read('layout-case')['records'][0]['content'], self.record['content'])

if __name__ == '__main__': unittest.main()
