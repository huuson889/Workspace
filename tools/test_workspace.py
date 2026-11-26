import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('workspace_tool', Path(__file__).with_name('workspace.py'))
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkspaceSafetyTests(unittest.TestCase):
    def setUp(self):
        w.CACHE.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=w.CACHE)
        self.root = Path(self.temp.name)
        self.patches = [patch.object(w, 'ROOT', self.root),
                        patch.object(w, 'LOCK_PATH', self.root / 'workspace.lock.json')]
        for p in self.patches:
            p.start()
        p = self.root / 'Keepit-OCR/vendor/test.bin'
        p.parent.mkdir(parents=True)
        p.write_bytes(b'locked asset\x00\xff')
        self.asset = p
        self.data = {'schema': 1, 'sourceCommit': 'a' * 40,
                     'files': [{'path': 'Keepit-OCR/vendor/test.bin', 'group': 'ocr-assets',
                                'blob': w.blob_hash(p), 'bytes': p.stat().st_size}]}
        self.write_lock()

    def write_lock(self):
        w.LOCK_PATH.write_text(json.dumps(self.data))

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def test_git_blob_hash_not_plain_sha1(self):
        data = self.asset.read_bytes()
        self.assertEqual(w.blob_hash(self.asset), hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())
        self.assertNotEqual(w.blob_hash(self.asset), hashlib.sha1(data).hexdigest())

    def test_verify_materialized_asset(self):
        self.assertEqual(w.verify('ocr-assets'), (1, 0))

    def test_missing_asset_is_explicit(self):
        self.asset.unlink()
        with self.assertRaises(RuntimeError):
            w.verify('ocr-assets')
        self.assertEqual(w.verify('ocr-assets', missing_ok=True), (0, 1))

    def test_eviction_refuses_edited_asset(self):
        self.asset.write_bytes(b'user changes')
        with patch.object(w, 'ensure_repo'), patch.object(w, 'select') as select:
            with self.assertRaises(RuntimeError):
                w.evict('ocr-assets')
            select.assert_not_called()
        self.assertEqual(self.asset.read_bytes(), b'user changes')

    def test_eviction_refuses_untracked_work(self):
        extra = self.asset.with_name('new-model.bin')
        extra.write_bytes(b'uncommitted')
        with patch.object(w, 'ensure_repo'), patch.object(w, 'select') as select:
            with self.assertRaises(RuntimeError):
                w.evict('ocr-assets')
            select.assert_not_called()
        self.assertTrue(extra.exists())

    def test_lock_rejects_parent_traversal(self):
        self.data['files'][0]['path'] = '../outside'
        self.write_lock()
        with self.assertRaises(RuntimeError):
            w.lock()

    def test_lock_rejects_mutable_branch_as_pin(self):
        self.data['sourceCommit'] = 'main'
        self.write_lock()
        with self.assertRaises(RuntimeError):
            w.lock()


if __name__ == '__main__':
    unittest.main()
