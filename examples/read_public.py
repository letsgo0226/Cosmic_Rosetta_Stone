#!/usr/bin/env python3
"""Keyless public Rosetta777 reader for AI agents; Python standard library only.

Usage: python3 examples/read_public.py --search love --limit 5
This program reads public, read-only JSON; it needs network access, not API keys.
"""
import argparse
import json
import re
import sys
from urllib.request import Request, urlopen

BASE = 'https://letsgo0226.github.io/Cosmic_Rosetta_Stone/'
VIDEO_ID = re.compile(r'[A-Za-z0-9_-]{11}\Z')


def get_json(url, opener=urlopen):
    if not url.startswith(BASE):
        raise ValueError('Only the known public Rosetta777 origin is allowed')
    request = Request(url, headers={'User-Agent': 'Rosetta777PublicReader/1.0'})
    with opener(request, timeout=15) as response:
        raw = response.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError('JSON response is unexpectedly large')
    return json.loads(raw)


def g257(text):
    n = 1
    for b in text.encode('utf-8'):
        n = 257*n + b + 1
    return hex(n)


def read_public(opener=urlopen):
    manifest = get_json(BASE + 'data/manifest.json', opener=opener)
    access = manifest.get('access', {})
    if access.get('authentication') != 'none' or access.get('api_key_required') is not False:
        raise ValueError('Unexpected authentication or API key requirement')
    url = manifest.get('links', {}).get('index')
    if url != BASE + 'data/index.json':
        raise ValueError('Unexpected index location')
    index = get_json(url, opener=opener)
    core = index.get('core') or {}
    checks = core.get('checks') or {}
    if set(checks) != {'G257', 'U2', 'Brainfuck', 'ATGC'} or not all(checks.values()):
        raise ValueError('Core checks missing or not all passing')
    videos = index.get('videos')
    if not isinstance(videos, list) or index.get('count') != len(videos):
        raise ValueError('Video count mismatch')
    if manifest.get('kernel_sha256') != core.get('sha256'):
        raise ValueError('Kernel hash disagrees with manifest')
    if manifest.get('count') != len(videos) or manifest.get('generated_at') != index.get('generated_at'):
        raise ValueError('Manifest differs from index')
    if (manifest.get('coverage'), manifest.get('sync_status')) != (
            index.get('coverage'), index.get('sync_status')):
        raise ValueError('Manifest coverage/status differs from index')
    for video in videos:
        vid = video.get('id')
        if not isinstance(vid, str) or not VIDEO_ID.fullmatch(vid):
            raise ValueError('Invalid public YouTube ID')
        if video.get('g257') != g257(vid):
            raise ValueError('Video G257 address mismatch')
        if not isinstance(video.get('title'), str):
            raise ValueError('Video title is not text')
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--search', default='', help='Case-insensitive title or ID substring')
    parser.add_argument('--limit', type=int, default=10, help='Return 1 to 100 matches')
    args = parser.parse_args()
    if not 1 <= args.limit <= 100:
        parser.error('--limit must be between 1 and 100')
    try:
        index = read_public()
    except Exception as exc:
        print(f'Read failed: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    q = args.search.casefold()
    matches = [v for v in index['videos'] if q in v['title'].casefold() or q in v['id'].casefold()]
    result = {
        'source': BASE + 'data/index.json',
        'sync_status': index['sync_status'],
        'coverage': index['coverage'],
        'generated_at': index['generated_at'],
        'available_count': index['count'],
        'matching_count': len(matches),
        'results': matches[:args.limit],
        'note': 'Titles and IDs are public metadata only; not a transcript.'
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
