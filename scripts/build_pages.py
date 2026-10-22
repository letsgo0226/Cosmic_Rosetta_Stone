#!/usr/bin/env python3
"""Build a public, read-only Rosetta777 index with optional official YouTube sources."""
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
import xml.etree.ElementTree as ET

CORE = Path(__file__).resolve().parents[1] / 'rosetta777_rosetta_plain_2kb.sh'
SITE_HTML = Path(__file__).resolve().parents[1] / 'site/index.html'
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}\Z')
CHANNEL_ID = re.compile(r'UC[A-Za-z0-9_-]{22}\Z')
HANDLE = re.compile(r'[A-Za-z0-9_.-]{3,30}\Z')
ATOM = '{http://www.w3.org/2005/Atom}'
YT = '{http://www.youtube.com/xml/schemas/2015}'


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


def record(vid, title):
    return {'id': vid, 'title': str(title)[:500],
            'g257': hex(g257(vid.encode('ascii')))}


def resolve_api_channel(handle, key, opener=urllib.request.urlopen):
    """Resolve a YouTube @handle via Google's supported Data API endpoint."""
    if not HANDLE.fullmatch(handle):
        raise ValueError('Invalid channel handle')
    params = urllib.parse.urlencode({'part': 'id', 'forHandle': handle, 'key': key})
    url = 'https://www.googleapis.com/youtube/v3/channels?' + params
    try:
        with opener(url, timeout=15) as response:
            obj = json.load(response)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'YouTube channels lookup HTTP {e.code}') from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError('YouTube channels lookup unavailable') from None
    ids = [x.get('id', '') for x in obj.get('items', [])]
    if len(ids) != 1 or not CHANNEL_ID.fullmatch(ids[0]):
        raise ValueError('Could not resolve a unique canonical channel ID')
    return ids[0]


def fetch_videos(channel, key, opener=urllib.request.urlopen, max_pages=100):
    """Complete public uploads index through the official YouTube Data API."""
    if not CHANNEL_ID.fullmatch(channel):
        raise ValueError('YT_ID must be a validated UC-prefixed channel ID')
    seen_tokens, seen_ids, page_token, videos = set(), set(), '', []
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
            raise RuntimeError(f'YouTube API returned HTTP {e.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError('YouTube API unavailable') from None
        for item in obj.get('items', []):
            snippet = item.get('snippet') or {}
            vid = (snippet.get('resourceId') or {}).get('videoId', '')
            if not VIDEO_ID.fullmatch(vid) or vid in seen_ids:
                continue
            seen_ids.add(vid)
            videos.append(record(vid, snippet.get('title', '')))
        page_token = obj.get('nextPageToken') or ''
        if not page_token:
            return videos
        if page_token in seen_tokens:
            raise RuntimeError('YouTube pagination repeated a token')
        seen_tokens.add(page_token)
    raise RuntimeError('YouTube playlist exceeds the 100-page safety bound')



def verified_feed_records(root, channel):
    """Verify a video's owner using either feed or per-entry canonical IDs."""
    if root.tag != ATOM + 'feed':
        raise ValueError('Unexpected Atom feed root')
    entries = root.findall(ATOM + 'entry')
    root_channel = root.findtext(YT + 'channelId') or ''
    atom_id = root.findtext(ATOM + 'id') or ''
    owners = [e.findtext(YT + 'channelId') or '' for e in entries]
    if root_channel and root_channel != channel:
        raise ValueError('Root channel ID does not match expected channel')
    if atom_id.startswith('yt:channel:') and atom_id != 'yt:channel:' + channel:
        raise ValueError('Atom channel ID does not match expected channel')
    if any(owner and owner != channel for owner in owners):
        raise ValueError('Video entry belongs to another channel')
    if not (root_channel == channel or atom_id == 'yt:channel:' + channel
            or channel in owners):
        raise ValueError('RSS feed has no matching canonical channel identity')
    videos, seen = [], set()
    for entry in entries:
        vid = entry.findtext(YT + 'videoId') or ''
        if VIDEO_ID.fullmatch(vid) and vid not in seen:
            videos.append(record(vid, entry.findtext(ATOM + 'title') or ''))
            seen.add(vid)
    if not videos:
        raise ValueError('Official RSS returned no public videos')
    return videos



def fetch_recent_rss(handle, opener=urllib.request.urlopen):
    """Best-effort public RSS; only the latest ~15, not a complete history.

    Channel handle resolution is based on YouTube's *public HTML*, not a stable
    API. If YouTube changes or blocks it, callers should show a sync warning.
    """
    if not HANDLE.fullmatch(handle):
        raise ValueError('Invalid channel handle')
    # Older channels sometimes expose their pre-handle username through the
    # official YouTube RSS feed. Trust it ONLY if YouTube's channel title matches
    # the requested handle, the canonical ID is valid, and videos are present.
    legacy_url = ('https://www.youtube.com/feeds/videos.xml?'
                  + urllib.parse.urlencode({'user': handle}))
    legacy_request = urllib.request.Request(
        legacy_url, headers={'User-Agent': 'Rosetta777PublicIndex/1.0'})
    try:
        with opener(legacy_request, timeout=15) as response:
            legacy_root = ET.fromstring(response.read(2000000))
        legacy_entries = legacy_root.findall(ATOM + 'entry')
        legacy_id = (legacy_root.findtext(YT + 'channelId') or
                     (legacy_entries[0].findtext(YT + 'channelId') if legacy_entries else '') or
                     (legacy_root.findtext(ATOM + 'id') or '').removeprefix('yt:channel:'))
        legacy_title = legacy_root.findtext(ATOM + 'title') or ''
        channel_name = re.sub(r'[^a-z0-9]', '', legacy_title.casefold())
        handle_name = re.sub(r'[^a-z0-9]', '', handle.casefold())
        if CHANNEL_ID.fullmatch(legacy_id) and channel_name == handle_name:
            return legacy_id, verified_feed_records(legacy_root, legacy_id)
    except (urllib.error.URLError, TimeoutError, ValueError, ET.ParseError, OSError):
        pass  # Legacy username lookup may not be supported; try current @handle.

    url = 'https://www.youtube.com/@' + urllib.parse.quote(handle)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; Rosetta777PublicIndex/1.0)'})
    with opener(req, timeout=15) as response:
        html = response.read(4000000).decode('utf-8', errors='replace')
    candidates = [
        r'"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
        r'<meta\s+itemprop="channelId"\s+content="(UC[A-Za-z0-9_-]{22})"',
        r'"channelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"'
    ]
    channel = None
    for pattern in candidates:
        match = re.search(pattern, html)
        if match:
            channel = match.group(1)
            break
    if channel is None:
        raise ValueError('Official public channel page did not expose a canonical ID')
    feed = 'https://www.youtube.com/feeds/videos.xml?' + urllib.parse.urlencode({'channel_id': channel})
    request = urllib.request.Request(feed, headers={'User-Agent': 'Rosetta777PublicIndex/1.0'})
    with opener(request, timeout=15) as response:
        xml = response.read(2000000)
    root = ET.fromstring(xml)
    return channel, verified_feed_records(root, channel)


def build(out, channel='', key='', fetcher=fetch_videos, core=CORE,
          handle='', rss_fetcher=fetch_recent_rss, api_resolver=resolve_api_channel):
    meta = kernel_check(core)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    records, status, coverage = [], 'not_configured', 'none'
    resolved_channel = channel or None
    if key:
        if not resolved_channel and handle:
            resolved_channel = api_resolver(handle, key)
        if not resolved_channel:
            raise ValueError('Set YT_ID or YT_HANDLE with YT_KEY')
        records = fetcher(resolved_channel, key)
        status, coverage = 'api_completed', 'public_uploads'
    elif handle:
        try:
            resolved_channel, records = rss_fetcher(handle)
            status, coverage = 'rss_recent', 'recent_only'
        except (ValueError, RuntimeError, urllib.error.URLError, TimeoutError, ET.ParseError, OSError) as exc:
            # Expected restricted connectivity is not a reason to publish fake records.
            print('RSS recent sync unavailable:', type(exc).__name__, str(exc) if isinstance(exc, ValueError) else '')
            status, coverage = 'rss_unavailable', 'none'
    elif channel:
        status = 'missing_key'
    out = Path(out)
    (out / 'data').mkdir(parents=True, exist_ok=True)
    payload = {'schema': 'rosetta777.static.v1', 'generated_at': now,
               'sync_status': status, 'coverage': coverage,
               'channel_handle': '@' + handle if handle else None,
               'channel_id': resolved_channel,
               'core': meta, 'count': len(records), 'videos': records}
    (out / 'data' / 'index.json').write_text(
        json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8')
    (out / 'data' / 'check.json').write_text(
        json.dumps(meta, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(SITE_HTML, out / 'index.html')
    (out / '.nojekyll').write_text('', encoding='utf-8')
    return payload


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default='public')
    args = parser.parse_args()
    result = build(args.out, os.environ.get('YT_ID', ''), os.environ.get('YT_KEY', ''),
                   handle=os.environ.get('YT_HANDLE', ''))
    print(f"Core checks passed; sync={result['sync_status']}; videos={result['count']}")
