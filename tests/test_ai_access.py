import io
import json
import pathlib
import tempfile
import unittest

from scripts.build_pages import build, g257
from examples.read_public import BASE, read_public, get_json


class MockResponse(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, typ, exc, tb):
        self.close()


def generated_fixture(folder):
    channel = 'UCLoHjca5L0KJ3i14MvhcroA'
    items = [{'id':'ABCDEFGHIJK','title':'Recent Love Video',
              'g257':hex(g257(b'ABCDEFGHIJK'))}]
    return build(folder, handle='777alaje',
                 rss_fetcher=lambda h:(channel, items))


def mock_public_fetch(folder):
    def opener(request, timeout):
        url=request.full_url
        prefix=BASE+'data/'
        if not url.startswith(prefix):
            raise ValueError('unexpected URL')
        file=pathlib.Path(folder)/'data'/url[len(prefix):]
        return MockResponse(file.read_bytes())
    return opener


class AIAccessTests(unittest.TestCase):
    def test_discovery_files_are_generated_without_keys(self):
        with tempfile.TemporaryDirectory() as d:
            generated_fixture(d)
            manifest = json.loads((pathlib.Path(d)/'data/manifest.json').read_text())
            schema = json.loads((pathlib.Path(d)/'data/index.schema.json').read_text())
            llms = (pathlib.Path(d)/'llms.txt').read_text()
            self.assertEqual(manifest['count'], 1)
            self.assertEqual(manifest['coverage'], 'recent_only')
            self.assertEqual(manifest['access']['authentication'], 'none')
            self.assertIs(manifest['access']['api_key_required'], False)
            self.assertEqual(schema['properties']['schema']['const'], 'rosetta777.static.v1')
            self.assertIn('data/index.json', llms)
            self.assertNotIn('Bearer <', llms)
            self.assertNotIn('YT_KEY=', json.dumps(manifest))

    def test_ai_reader_validates_public_data(self):
        with tempfile.TemporaryDirectory() as d:
            generated_fixture(d)
            index = read_public(opener=mock_public_fetch(d))
            self.assertEqual(index['count'], 1)
            self.assertEqual(index['videos'][0]['title'], 'Recent Love Video')

    def test_ai_reader_rejects_modified_g257(self):
        with tempfile.TemporaryDirectory() as d:
            generated_fixture(d)
            path = pathlib.Path(d)/'data/index.json'
            data=json.loads(path.read_text())
            data['videos'][0]['g257']='0x1'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'G257'):
                read_public(opener=mock_public_fetch(d))

    def test_ai_reader_rejects_changed_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            generated_fixture(d)
            path=pathlib.Path(d)/'data/manifest.json'
            data=json.loads(path.read_text())
            data['links']['index']='https://example.com/forged.json'
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'Unexpected index'):
                read_public(opener=mock_public_fetch(d))

    def test_ai_reader_rejects_inconsistent_count(self):
        with tempfile.TemporaryDirectory() as d:
            generated_fixture(d)
            path=pathlib.Path(d)/'data/index.json'
            data=json.loads(path.read_text())
            data['count']=999
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'count mismatch'):
                read_public(opener=mock_public_fetch(d))

    def test_fetcher_restricts_approved_host(self):
        with self.assertRaisesRegex(ValueError, 'known public'):
            get_json('https://example.org/public-index.json')


if __name__ == '__main__':
    unittest.main()
