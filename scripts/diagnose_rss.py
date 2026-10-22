#!/usr/bin/env python3
"""Read-only diagnostic of publicly exposed channel identity; no credentials."""
import re
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET

ATOM = '{http://www.w3.org/2005/Atom}'
YT = '{http://www.youtube.com/xml/schemas/2015}'
REGEX = re.compile(r'UC[A-Za-z0-9_-]{22}\Z')

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as res:
        return res.read(3000000)

def report_feed(label, raw):
    root = ET.fromstring(raw)
    atom_id = root.findtext(ATOM+'id')
    root_id = root.findtext(YT+'channelId')
    title = root.findtext(ATOM+'title')
    entries = root.findall(ATOM+'entry')
    owner = entries[0].findtext(YT+'channelId') if entries else None
    print(label, 'root=',root.tag, 'atomId=',repr(atom_id),
          'rootChannel=',repr(root_id), 'title=',repr(title)[:120],
          'entries=',len(entries),'firstEntryOwner=',repr(owner))
    return root_id or owner

try:
    page = fetch('https://www.youtube.com/@777alaje').decode('utf-8', errors='replace')
    print('handle-page size=',len(page),'titleTag=',repr(re.search(r'<title>([^<]{0,200})',page).group(1) if re.search(r'<title>([^<]{0,200})',page) else ''))
    ids=[]
    for pattern in [r'"externalId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"',
                    r'<meta\s+itemprop="channelId"\s+content="(UC[A-Za-z0-9_-]{22})"',
                    r'"channelId"\s*:\s*"(UC[A-Za-z0-9_-]{22})"']:
        m=re.search(pattern,page)
        print('html-ID-pattern',pattern[:28], 'found=',m.group(1) if m else None)
        if m:
            ids.append(m.group(1))
    if ids:
        try:
            report_feed('id-derived-feed',fetch('https://www.youtube.com/feeds/videos.xml?channel_id='+ids[0]))
        except (urllib.error.URLError, ET.ParseError, ValueError) as exc:
            print('id-derived-feed error type=',type(exc).__name__,'details=',str(exc)[:120])
except (urllib.error.URLError, ET.ParseError, ValueError) as exc:
    print('handle error=',type(exc).__name__,'details=',str(exc)[:120])

try:
    report_feed('legacy-user-feed',fetch('https://www.youtube.com/feeds/videos.xml?user=777alaje'))
except (urllib.error.URLError, ET.ParseError, ValueError) as exc:
    print('legacy-user-feed error=',type(exc).__name__,'details=',str(exc)[:120])
