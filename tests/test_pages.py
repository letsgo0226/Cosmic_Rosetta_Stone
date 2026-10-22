import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import io

from scripts.build_pages import build, fetch_videos, g257, kernel_check


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class PagesTests(unittest.TestCase):
    def test_kernel(self):
        info = kernel_check()
        self.assertEqual(info['bytes'], 2045)
        self.assertEqual(len(info['sha256']), 64)
        self.assertTrue(all(info['checks'].values()))

    def test_g257(self):
        self.assertEqual(g257(b''), 1)
        self.assertEqual(g257(b'\x00'), 257*1 + 1)

    def test_missing_credentials_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            x = build(d)
            self.assertEqual(x['sync_status'], 'not_configured')
            self.assertEqual(x['videos'], [])
            data = json.loads((pathlib.Path(d)/'data/index.json').read_text())
            self.assertEqual(data['count'], 0)
            self.assertNotIn('YT_KEY', (pathlib.Path(d)/'index.html').read_text())

    def test_paginated_public_video_index(self):
        requests = []
        def open_stub(url, timeout):
            requests.append(url)
            if 'pageToken=' in url:
                v = {'items':[{'snippet':{'resourceId':{'videoId':'BBBBBBBBBBB'},'title':'Episode 15 Caduceus'}}]}
            else:
                v = {'items':[{'snippet':{'resourceId':{'videoId':'AAAAAAAAAAA'},'title':'Love <script>alert(1)</script>'}}], 'nextPageToken':'p2'}
            return FakeResponse(json.dumps(v).encode())
        records=fetch_videos('UC'+'a'*22,'not-a-real-key',opener=open_stub)
        self.assertEqual([x['id'] for x in records],['AAAAAAAAAAA','BBBBBBBBBBB'])
        self.assertEqual(len(requests),2)
        self.assertIn('g257', records[0])

    def test_invalid_channel_rejected(self):
        with self.assertRaises(ValueError):
            fetch_videos('https://evil.example/','x')


if __name__=='__main__':
    unittest.main()
