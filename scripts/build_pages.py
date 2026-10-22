#!/usr/bin/env python3
"""Build public, read-only Rosetta777 JSON and HTML; never export credentials."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request

CORE = Path(__file__).resolve().parents[1] / 'rosetta777_rosetta_plain_2kb.sh'
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}\Z')
CHANNEL_ID = re.compile(r'UC[A-Za-z0-9_-]{22}\Z')


def g257(b: bytes) -> int:
    n = 1
    for v in b:
        n = 257 * n + v + 1
    return n


def kernel_check(core=CORE):
    b = core.read_bytes()
    if len(b) >= 2048 or b.count(b'\n') != 1 or not b.endswith(b'\n'):
        raise ValueError('Kernel must be one physical line and strictly under 2048 bytes')
    r = subprocess.run(['sh', str(core), 'check'], check=True, capture_output=True,
                       text=True, timeout=30)
    tests = json.loads(r.stdout)
    if tests != [True, True, True, True]:
        raise ValueError(f'Kernel check failed: {tests!r}')
    return {'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(),
            'checks': dict(zip(('G257', 'U2', 'Brainfuck', 'ATGC'), tests))}


def fetch_videos(channel, key, opener=urllib.request.urlopen, max_pages=100):
    if not CHANNEL_ID.fullmatch(channel):
        raise ValueError('YT_ID must be a validated UC-prefixed channel ID')
    seen_tokens = set()
    seen_ids = set()
    page_token = ''
    videos = []
    for _ in range(max_pages):
        params = {'part': 'snippet', 'maxResults': 50,
                  'playlistId': 'UU' + channel[2:], 'key': key}
        if page_token:
            params['pageToken'] = page_token
        url = 'https://www.googleapis.com/youtube/v3/playlistItems?' + urllib.parse.urlencode(params)
        try:
            with opener(url, timeout=15) as res:
                obj = json.load(res)
        except urllib.error.HTTPError as e:
            # NEVER echo e.url (it contains the API key).
            raise RuntimeError(f'YouTube API returned HTTP {e.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError('YouTube API unavailable') from None
        for item in obj.get('items', []):
            snippet = item.get('snippet') or {}
            vid = (snippet.get('resourceId') or {}).get('videoId', '')
            if not VIDEO_ID.fullmatch(vid) or vid in seen_ids:
                continue
            seen_ids.add(vid)
            videos.append({'id': vid, 'title': str(snippet.get('title', ''))[:500],
                           'g257': hex(g257(vid.encode('ascii')))})
        page_token = obj.get('nextPageToken') or ''
        if not page_token:
            return videos
        if page_token in seen_tokens:
            raise RuntimeError('YouTube pagination repeated a token')
        seen_tokens.add(page_token)
    raise RuntimeError('YouTube playlist exceeds the 100-page safety bound')


SITE_HTML = Path(__file__).resolve().parents[1] / 'site/index.html'

def build(out, channel='', key='', fetcher=fetch_videos, core=CORE):
    meta = kernel_check(core)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    records = []
    status = 'not_configured'
    if channel and key:
        records = fetcher(channel, key)
        status = 'completed'
    elif channel or key:
        status = 'missing_channel_or_key'
    out = Path(out)
    (out / 'data').mkdir(parents=True, exist_ok=True)
    payload = {'schema': 'rosetta777.static.v1', 'generated_at': now,
               'sync_status': status, 'channel_id': channel if channel else None,
               'core': meta, 'count': len(records), 'videos': records}
    (out / 'data' / 'index.json').write_text(json.dumps(payload, ensure_ascii=False,
                                      separators=(',', ':'))+'\n', encoding='utf-8')
    (out / 'data' / 'check.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8')
    shutil.copyfile(SITE_HTML, out / 'index.html')
    (out / '.nojekyll').write_text('', encoding='utf-8')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='public')
    args = parser.parse_args()
    obj = build(args.out, os.environ.get('YT_ID', ''), os.environ.get('YT_KEY', ''))
    print(f"Core checks passed; sync={obj['sync_status']}; videos={obj['count']}")
