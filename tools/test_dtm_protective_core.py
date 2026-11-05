#!/usr/bin/env python3
"""Regression tests: DTM-22 protective state invariants, denial, history, TM-009."""
from pathlib import Path
from dataclasses import replace
import importlib.util
import json
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools/dtm_protective_core.py"
EXACT = ROOT / "machines/UGTM_UCP_Exact_Encoding_2KB.sh"
spec = importlib.util.spec_from_file_location("dtm_protection", CORE)
dtm = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = dtm
spec.loader.exec_module(dtm)


def exact_report(*args):
    raw = subprocess.check_output(["bash", str(EXACT), *args], text=True,
                                  cwd=ROOT, timeout=15)
    return json.loads(raw)


class ProtectedDTMTests(unittest.TestCase):
    def test_default_is_valid_and_read_only(self):
        g = dtm.Guardian()
        self.assertTrue(g.verify_history())
        self.assertEqual(g.state.cookies, (3, 0, 0))
        self.assertEqual(g.state.worldline, 22)
        self.assertEqual(len(g.history), 1)
        self.assertEqual(g.history[0].action, "genesis")

    def test_safe_redistribution_and_history(self):
        g = dtm.Guardian()
        baseline = g.history[-1].digest
        response = g.apply("split")
        self.assertEqual(response["status"], "COMMITTED")
        self.assertEqual(g.state.cookies, (1, 1, 1))
        self.assertEqual(g.state.revision, 1)
        self.assertNotEqual(baseline, g.history[-1].digest)
        self.assertTrue(g.verify_history())

    def test_faults_fail_closed(self):
        for kind in ("drop", "negative", "worldline"):
            with self.subTest(kind=kind):
                g = dtm.Guardian()
                before = g.state, g.history[-1].digest
                response = g.test_fault(kind)
                self.assertEqual(response["status"], "DENIED")
                self.assertEqual((g.state, g.history[-1].digest), before)
                self.assertEqual(len(g.history), 1)
                self.assertTrue(g.verify_history())

    def test_unknown_action_does_not_run(self):
        g = dtm.Guardian()
        head = g.history[-1].digest
        response = g.apply("deploy")
        self.assertEqual(response["status"], "DENIED")
        self.assertEqual(g.history[-1].digest, head)
        self.assertEqual(g.state.cookies, (3, 0, 0))

    def test_restore_logical_snapshot_only(self):
        g = dtm.Guardian()
        g.apply("split")
        response = g.restore(0)
        self.assertEqual(response["status"], "COMMITTED")
        self.assertEqual(g.state.cookies, (3, 0, 0))
        self.assertEqual(g.state.revision, 2)
        self.assertEqual(len(g.history), 3)
        self.assertTrue(g.verify_history())

    def test_invalid_checkpoint(self):
        g = dtm.Guardian()
        response = g.restore(99)
        self.assertEqual(response["status"], "DENIED")
        self.assertEqual(len(g.history), 1)

    def test_detect_tampered_history(self):
        g = dtm.Guardian()
        g.apply("split")
        original = g.history[-1]
        g.history[-1] = replace(original, state=replace(original.state, cookies=(3, 0, 0)))
        with self.assertRaises(dtm.Rejected):
            g.verify_history()

    def test_internal_valid_but_unauthorized_commit_is_denied(self):
        # A syntactically valid state may still violate the action policy.
        g = dtm.Guardian()
        initial = g.state
        expected = replace(initial, cookies=(1, 1, 1), revision=1)
        for action in ("deploy", "hold", "restore_99"):
            with self.subTest(action=action):
                before_digest = g.history[-1].digest
                response = g._commit(expected, action)
                self.assertEqual(response["status"], "DENIED")
                self.assertEqual(g.state, initial)
                self.assertEqual(g.history[-1].digest, before_digest)
                self.assertEqual(len(g.history), 1)

    def test_hash_recalculation_does_not_bypass_action_policy(self):
        g = dtm.Guardian()
        g.apply("split")
        original = g.history[-1]
        # Attacker adjusts the action and recomputes the hash correctly.
        # The state would not be a legal "hold" transition.
        action = "hold"
        fake = replace(original, action=action,
                       digest=dtm.checkpoint_hash(original.previous, action,
                                                  original.state))
        g.history[-1] = fake
        with self.assertRaisesRegex(dtm.Rejected, "hold_effect_mismatch"):
            g.verify_history()

    def test_reject_bad_initial_state(self):
        for s in (
            dtm.State(worldline=23),
            dtm.State(cookies=(3, 1, -1)),
            dtm.State(cookies=(1, 1, 0)),
            dtm.State(time=-1),
        ):
            with self.subTest(s=s), self.assertRaises(dtm.Rejected):
                dtm.Guardian(s)

    def test_verify_real_exact_reports(self):
        for args in (
            ("10", ".6", ".3", "1"),
            ("10", "-.6", ".3", "1/2"),
            ("0", "0", "0", "0"),
            ("13/2", "-1/2", "1/3", "3/4"),
        ):
            with self.subTest(args=args):
                cert = exact_report(*args)
                result = dtm.validate_tm009_certificate(cert)
                self.assertEqual(result["status"], "VERIFIED_MODEL_CERTIFICATE")
                self.assertEqual(result["scope"], "algebraic_internal_consistency_only")

    def test_reject_corrupted_certificate(self):
        good = exact_report("10", ".6", ".3", "1")
        import copy
        trials = []
        bad = copy.deepcopy(good); bad["P"][1] = "1/3"; trials.append(bad)
        bad = copy.deepcopy(good); bad["godel257"] = "5"; trials.append(bad)
        bad = copy.deepcopy(good); bad["FI_u_interior_limit"] = "9"; trials.append(bad)
        bad = copy.deepcopy(good); bad["proper_time"] = "7"; trials.append(bad)
        bad = copy.deepcopy(good); bad["physical_chronon_proven"] = True; trials.append(bad)
        bad = copy.deepcopy(good); bad["H_bits"] = "0"; trials.append(bad)
        bad = copy.deepcopy(good); bad["amplitudes"][1] = "sqrt(2)*1/3"; trials.append(bad)
        for bad in trials:
            with self.subTest(bad=bad), self.assertRaises(dtm.Rejected):
                dtm.validate_tm009_certificate(bad)

    def test_cli_no_external_effects(self):
        raw = subprocess.check_output(["python3", str(CORE), "--fault", "drop", "--restore"],
                                      text=True, cwd=ROOT, timeout=15)
        data = json.loads(raw)
        self.assertTrue(data["chain_valid"])
        self.assertFalse(data["executed_external_commands"])
        self.assertFalse(data["physical_protection_proven"])
        self.assertEqual(data["transitions"][0]["status"], "COMMITTED")
        self.assertEqual(data["transitions"][1]["status"], "DENIED")
        self.assertEqual(data["transitions"][2]["status"], "COMMITTED")
        self.assertEqual(data["state"]["phases"][0][3], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
