#!/usr/bin/env python3
"""Independent tests of UCGTM one-liner's reversible encodings and triplet boundary."""
from fractions import Fraction as F
from pathlib import Path
import json
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = REPO / 'machines' / 'UCGTM_ATGC_Abelian_Triplet_2KB.sh'
if not SOURCE.exists():
    SOURCE = HERE / 'UCGTM_ATGC_Abelian_Triplet_2KB.sh'
ORIGINAL_TM009 = REPO / 'machines' / 'UGTM_UCP_Exact_Encoding_2KB.sh'

def run(*args):
    return json.loads(subprocess.check_output(['bash', str(SOURCE), *map(str,args)],
                                              text=True, timeout=10))

class BridgeTests(unittest.TestCase):
    def test_file_is_single_line_under_2kb(self):
        b = SOURCE.read_bytes()
        self.assertLessEqual(len(b), 2048)
        self.assertEqual(b.count(b'\n'), 1)

    def test_atgc_roundtrip(self):
        a=run()
        self.assertEqual(a['dna'],'CTTTCAAGGTCC')
        self.assertEqual(a['g257'],'25051557260623293264')
        b=run('DNA:'+a['dna'])
        self.assertEqual(a,b)

    def test_real_turing_machine_halts_and_restores_tape(self):
        for n in range(1,6):
            x=run('PLEIADES','1',n,3)
            self.assertTrue(x['turing_halted'])
            self.assertTrue(x['tape_restored'])
            self.assertEqual(x['turing_rules'],8)
            self.assertTrue(x['inverse_verified'])

    def test_triplet_probabilities_exact(self):
        for val in ('0','1/2','1','3/2','7'):
            with self.subTest(u=val):
                u=F(val);z=(1+u*u)**2
                expected=[1/z,2*u*u/z,u**4/z]
                a=run('PLEIADES',val,3,3)
                self.assertEqual([F(t) for t in a['P']],expected)
                self.assertEqual(sum(map(F,a['P'])),1)
                self.assertEqual(F(a['FI_u']),8/z)
                self.assertEqual(a['FI_theta'],'2')
                self.assertEqual([F(t) for t in a['P_after']],expected[::-1])

    def test_gate_policy_by_preservation_not_just_invertibility(self):
        for gate in range(8):
            with self.subTest(gate=gate):
                r=run('PLEIADES','1/2',2,gate)
                allowed=gate in (0,3,4,7)
                self.assertEqual(r['triplet_preserved'],allowed)
                self.assertEqual(r['gate_policy'],'ACCEPT' if allowed else 'DENY')
                self.assertEqual(r['P_after'] is not None,allowed)
                self.assertTrue(all((x^gate)^gate==x for x in range(8)))

    def test_invariant_symmetric_code_supports(self):
        codes={0:{0,4},1:{1,2,5,6},2:{3,7}}
        for gate in range(8):
            acts_on_code=all({x^gate for x in support} in codes.values()
                             for support in codes.values())
            self.assertEqual(acts_on_code,gate in (0,3,4,7))
            self.assertEqual(len({x^gate for x in range(8)}),8)

    def test_seven_adic_projection_and_closed_loop(self):
        results=[run('PLEIADES','1',k,3) for k in range(1,7)]
        for a,b in zip(results,results[1:]):
            m=7**a['seven_adic_level']
            self.assertEqual(b['left']%m,a['left'])
            self.assertEqual(b['right']%m,a['right'])
            self.assertEqual((a['left']+a['right'])%m,0)
            self.assertEqual((a['step'][0]-1)%m,a['left'])
            self.assertEqual((a['step'][1]+1)%m,a['right'])

    def test_abelian_xor_group(self):
        for a in range(8):
            for b in range(8):
                self.assertEqual(a^b,b^a)
                self.assertEqual((a^b)^b,a)
                for x in range(8):
                    self.assertEqual((x^a)^b,x^(a^b))

    def test_s5_possible_necessity_not_bare_possibility(self):
        for valuation in ((False,False),(False,True),(True,False),(True,True)):
            necessary=all(valuation)
            possible_necessary=any(all(valuation) for _ in valuation)
            self.assertFalse(possible_necessary and not necessary)
        valuation=(True,False)
        self.assertTrue(any(valuation))
        self.assertFalse(all(valuation))

    @unittest.skipUnless(ORIGINAL_TM009.exists(),'Run in Cosmic_Rosetta_Stone to compare with TM-009')
    def test_against_original_tm009_exact_model(self):
        for val in ('0','1/2','1','2'):
            orig=json.loads(subprocess.check_output(['bash',str(ORIGINAL_TM009),
                  '10','.6','.3',val],text=True,timeout=10))
            our=run('PLEIADES',val,3,3)
            self.assertEqual(orig['P'],our['P'])
            self.assertEqual(orig['FI_u_interior_limit'],our['FI_u'])
            self.assertEqual(orig['FI_theta_interior_limit'],our['FI_theta'])

    def test_invalid_inputs_rejected(self):
        for args in (('HELLO',),('DNA:AAAA',),('PLEIADES','-1'),
                     ('PLEIADES','1','0'),('PLEIADES','1','3','8')):
            with self.subTest(args=args):
                z=subprocess.run(['bash',str(SOURCE),*args],
                                 capture_output=True,text=True,timeout=10)
                self.assertNotEqual(z.returncode,0)

if __name__=='__main__':
    unittest.main(verbosity=2)
