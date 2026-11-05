#!/usr/bin/env python3
"""SMT model of the DTM22 guardian's guarded *logical* commit procedure.

Dependency: z3-solver==4.16.0.0
Scope: quantifier-free linear integer arithmetic over unbounded Ints.
A proof is a solver result UNSAT for an explicit counterexample formula.
This is NOT a machine-checked proof of CPython, SHA-256, I/O, or physics.
"""
from __future__ import annotations
import json
from z3 import (
    And, Bool, If, Implies, Int, IntVal, Not, Or, Solver,
    Z3_OP_UNINTERPRETED, is_true, sat, unsat,
)

def ints(prefix):
    return [Int(prefix + "_" + x) for x in ("w", "t", "r", "c0", "c1", "c2")]

def valid(s):
    w, t, r, a, b, c = s
    return And(w == 22, t >= 0, r >= 0,
               a >= 0, b >= 0, c >= 0, a+b+c == 3)

def same(s, t):
    return And(*(x == y for x, y in zip(s, t)))

def any_different(s, t):
    return Or(*(x != y for x, y in zip(s, t)))

def model():
    current, trial, snapshot = ints("current"), ints("proposal"), ints("snapshot")
    action = Int("action")  # split=1, hold=2, restore=3; other values forbidden
    snapshot_available = Bool("snapshot_available")
    w, t, r, a, b, c = current
    pw, pt, pr, pa, pb, pc = trial
    sw, st, sr, sa, sb, sc = snapshot

    effect = Or(
        And(action == 1, pa == 1, pb == 1, pc == 1),
        And(action == 2, pa == a, pb == b, pc == c),
        And(action == 3, snapshot_available, valid(snapshot),
            pa == sa, pb == sb, pc == sc)
    )
    # Abstracts _action_policy, validate_state, equality and revision checks.
    guard = And(valid(trial), pw == w, pt == t, pr == r+1, effect)
    after = [If(guard, new, old) for new, old in zip(trial, current)]
    return {
        "current": current, "proposal": trial, "snapshot": snapshot,
        "action": action, "snapshot_available": snapshot_available,
        "effect": effect, "guard": guard, "after": after
    }

def run_check(title, premises, counterexample, expected, witness=False):
    s = Solver()
    s.set(timeout=10000)
    s.add(*premises)
    s.add(counterexample)
    outcome = s.check()
    if outcome != expected:
        raise AssertionError(
            "{}: expected {}, got {} ({})".format(
                title, expected, outcome,
                s.reason_unknown() if outcome != sat else s.model()))
    result = {"name": title, "result": str(outcome),
              "expected": str(expected), "passed": True}
    if witness and outcome == sat:
        # A concrete model is included only for the deliberate falsification.
        result["sample_model"] = str(s.model())[:1600]
    return result

def prove():
    m = model()
    before, proposal, snapshot, after = (m[x] for x in (
        "current", "proposal", "snapshot", "after"))
    action, guard, available = (m[x] for x in (
        "action", "guard", "snapshot_available"))
    w, t, r, a, b, c = before
    pw, pt, pr, pa, pb, pc = proposal
    sw, st, sr, sa, sb, sc = snapshot
    evidence = []

    def theorem(name, *bad):
        evidence.append(run_check(name, [valid(before)], And(*bad), unsat))

    theorem("invariant_preservation", Not(valid(after)))
    theorem("rejected_transition_is_stutter", Not(guard),
            any_different(before, after))
    theorem("worldline_and_time_preservation",
            Or(after[0] != w, after[1] != t))
    theorem("accepted_revision_increment", guard, after[2] != r+1)
    theorem("accepted_action_is_allowlisted",
            guard, And(action != 1, action != 2, action != 3))
    theorem("split_effect_preserved", guard, action == 1,
            Or(after[3] != 1, after[4] != 1, after[5] != 1))
    theorem("hold_effect_preserved", guard, action == 2,
            Or(after[3] != a, after[4] != b, after[5] != c))
    theorem("restore_uses_approved_snapshot", guard, action == 3,
            Or(Not(available), after[3] != sa,
               after[4] != sb, after[5] != sc))
    theorem("unavailable_restore_is_denied",
            action == 3, Not(available), guard)
    theorem("invalid_candidate_is_denied",
            Not(valid(proposal)), guard)
    theorem("external_deploy_action_is_denied", action == 99, guard)
    theorem("negative_cookie_cannot_commit", pa < 0, guard)
    theorem("conservation_violation_cannot_commit",
            pa+pb+pc != 3, guard)

    # Existence checks prevent a vacuous proof where every operation is denied.
    for name, act, alloc in [
        ("split_witness", 1, (1, 1, 1)),
        ("hold_witness", 2, (a, b, c)),
    ]:
        prem = [valid(before), action == act, pw == w, pt == t,
                pr == r+1, pa == alloc[0], pb == alloc[1], pc == alloc[2]]
        evidence.append(run_check(name, prem, guard, sat))
    rest = [
        valid(before), valid(snapshot), available,
        action == 3, sw == w, st == t,
        pw == w, pt == t, pr == r+1,
        pa == sa, pb == sb, pc == sc
    ]
    evidence.append(run_check("restore_witness", rest, guard, sat))

    # A deliberately weakened guardian is demonstrably unsafe.
    # Merely preserving the sum 3 would permit (4,-1,0).
    weak_guard = And(pw == w, pt == t, pr == r+1,
                     pa+pb+pc == 3, action == 1)
    evidence.append(run_check(
        "weak_guard_has_counterexample",
        [valid(before), pa == 4, pb == -1, pc == 0,
         pw == w, pt == t, pr == r+1, action == 1],
        weak_guard, sat, witness=True
    ))
    return {
        "system": "DTM22-SMT-SAFETY",
        "logic": "QF_LIA",
        "semantics": "unbounded mathematical integers; guarded logical state transitions",
        "dependency": "z3-solver==4.16.0.0",
        "coverage": "public split/hold and history-approved restore; abstract guard, not full Python",
        "physical_safety_proven": False,
        "program_refinement_proven": False,
        "hash_authenticity_proven": False,
        "theorems": evidence,
        "summary": {"checked": len(evidence),
                    "unsat_safety_obligations": sum(x["result"] == "unsat" for x in evidence),
                    "sat_sanity_witnesses": sum(x["result"] == "sat" for x in evidence),
                    "all_matched_expected_results": all(x["passed"] for x in evidence)},
    }

if __name__ == "__main__":
    print(json.dumps(prove(), ensure_ascii=False, indent=2))
