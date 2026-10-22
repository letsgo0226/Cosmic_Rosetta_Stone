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


    def test_recent_rss_from_official_channel_page(self):
        from scripts.build_pages import fetch_recent_rss
        channel = 'UC' + 'a' * 22
        urls = []
        feed = (
            '<feed xmlns="http://www.w3.org/2005/Atom" '
            'xmlns:yt="http://www.youtube.com/xml/schemas/2015">'
            f'<yt:channelId>{channel}</yt:channelId>'
            '<entry><yt:videoId>AAAAAAAAAAA</yt:videoId>'
            '<title>Official Recent Video</title></entry></feed>'
        )
        def opener(request, timeout):
            url = request.full_url
            urls.append(url)
            if '/@777alaje' in url:
                return FakeResponse(f'<script>"externalId":"{channel}"</script>'.encode())
            return FakeResponse(feed.encode())
        found, videos = fetch_recent_rss('777alaje', opener=opener)
        self.assertEqual(found, channel)
        self.assertEqual([v['id'] for v in videos], ['AAAAAAAAAAA'])
        self.assertEqual(len(urls), 2)
        self.assertTrue(urls[1].startswith('https://www.youtube.com/feeds/videos.xml?'))

    def test_rss_feed_mismatch_is_rejected(self):
        from scripts.build_pages import fetch_recent_rss
        channel = 'UC' + 'a' * 22
        def opener(request, timeout):
            if '/@' in request.full_url:
                return FakeResponse(f'<meta itemprop="channelId" content="{channel}">'.encode())
            return FakeResponse(b'<feed xmlns:yt="http://www.youtube.com/xml/schemas/2015"><yt:channelId>UCdifferent</yt:channelId></feed>')
        with self.assertRaises(ValueError):
            fetch_recent_rss('777alaje', opener=opener)

    def test_rss_index_without_api_key(self):
        with tempfile.TemporaryDirectory() as d:
            channel = 'UC' + 'a' * 22
            items = [{'id': 'BBBBBBBBBBB', 'title': 'Love', 'g257': hex(g257(b'BBBBBBBBBBB'))}]
            x = build(d, handle='777alaje', rss_fetcher=lambda handle: (channel, items))
            self.assertEqual((x['sync_status'], x['coverage'], x['count']),
                             ('rss_recent', 'recent_only', 1))
            self.assertEqual(x['channel_id'], channel)
            self.assertEqual(json.loads((pathlib.Path(d)/'data/index.json').read_text())['count'], 1)

    def test_rss_failure_is_visible_not_faked(self):
        with tempfile.TemporaryDirectory() as d:
            def failure(handle):
                raise ValueError('blocked')
            x = build(d, handle='777alaje', rss_fetcher=failure)
            self.assertEqual((x['sync_status'], x['coverage'], x['count']),
                             ('rss_unavailable', 'none', 0))

    def test_api_channel_handle_resolution(self):
        from scripts.build_pages import resolve_api_channel
        channel = 'UC' + 'a' * 22
        requests = []
        def opener(url, timeout):
            requests.append(url)
            return FakeResponse(json.dumps({'items': [{'id': channel}]}).encode())
        self.assertEqual(resolve_api_channel('777alaje', 'fake', opener=opener), channel)
        self.assertIn('forHandle=777alaje', requests[0])
        with tempfile.TemporaryDirectory() as d:
            x = build(d, key='fake', handle='777alaje',
                      api_resolver=lambda h, k: channel,
                      fetcher=lambda c, k: [{'id':'AAAAAAAAAAA','title':'Episode','g257':'0x2'}])
            self.assertEqual(x['sync_status'], 'api_completed')
            self.assertEqual(x['coverage'], 'public_uploads')
            self.assertEqual(x['count'], 1)

    def test_invalid_rss_handle_rejected(self):
        from scripts.build_pages import fetch_recent_rss
        with self.assertRaises(ValueError):
            fetch_recent_rss('evil/../../../bad')


if __name__=='__main__':
    unittest.main()
