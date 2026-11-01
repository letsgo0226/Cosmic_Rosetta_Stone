import unittest
from pocket import encode, decode, simulate

class PocketTests(unittest.TestCase):
    def test_roundtrip(self):
        for data in (b'', b'\0\xff', '三顆貓餅乾'.encode()):
            self.assertEqual(decode(encode(data)), data)
    def test_invalid_encoding(self):
        with self.assertRaises(ValueError):
            decode(257)
    def test_halt(self):
        p = {'rules': [[0, '1', 1, '1', 'R'], [1, '_', 2, '_', 'N']], 'tape': '1'}
        self.assertEqual(simulate(p, 10)['steps'], 2)
        self.assertEqual(simulate(p, 10)['status'], 'HALT')
    def test_limit_not_nontermination_proof(self):
        p = {'rules': [[0, '_', 0, '1', 'R']]}
        self.assertEqual(simulate(p, 4)['status'], 'LIMIT')
    def test_duplicate_rule(self):
        p = {'rules': [[0, '_', 0, '_', 'N'], [0, '_', 1, '_', 'N']]}
        with self.assertRaises(ValueError):
            simulate(p)

if __name__ == '__main__':
    unittest.main()
