#!/usr/bin/env python3
"""DTM-22 protective computation: bounded, side-effect-free research prototype.

Three labeled logical phases are NOT evidence for time travel or preservation
of a conscious individual. No subprocesses, network, file writes, or deployment.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

MAX_CERTIFICATE_BYTES = 24_576
GENESIS_ANCHOR = "DTM22-PROTECTION-v0.1"


class Rejected(ValueError):
    """Model-level rejection, not a certification of real-world safety."""


@dataclass(frozen=True)
class State:
    worldline: int = 22
    time: int = 100
    cookies: tuple[int, int, int] = (3, 0, 0)
    revision: int = 0


def state_data(s: State) -> dict:
    return {"worldline": s.worldline, "time": s.time,
            "phases": [[s.worldline, i, s.time, n]
                       for i, n in enumerate(s.cookies)],
            "revision": s.revision}


def validate_state(s: State) -> None:
    if not isinstance(s, State) or type(s.worldline) is not int or s.worldline != 22:
        raise Rejected("worldline_id_mismatch")
    if type(s.time) is not int or s.time < 0:
        raise Rejected("invalid_time_label")
    if type(s.revision) is not int or s.revision < 0:
        raise Rejected("invalid_revision")
    if (type(s.cookies) is not tuple or len(s.cookies) != 3 or
            any(type(x) is not int or x < 0 for x in s.cookies)):
        raise Rejected("invalid_cookie_allocation")
    if sum(s.cookies) != 3:
        raise Rejected("cookie_conservation_failed")


def canonical(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def checkpoint_hash(previous: str, action: str, s: State) -> str:
    payload = {"previous": previous, "action": action, "state": state_data(s)}
    return hashlib.sha256(canonical(payload)).hexdigest()


@dataclass(frozen=True)
class Checkpoint:
    state: State
    previous: str
    action: str
    digest: str


class Guardian:
    """Validated state transitions. Rejections never change committed state."""

    def __init__(self, initial: State | None = None):
        s = State() if initial is None else initial
        validate_state(s)
        h = checkpoint_hash(GENESIS_ANCHOR, "genesis", s)
        self.history = [Checkpoint(s, GENESIS_ANCHOR, "genesis", h)]
        self.rejections: list[str] = []

    @property
    def state(self) -> State:
        return self.history[-1].state

    def verify_history(self) -> bool:
        previous = GENESIS_ANCHOR
        for index, record in enumerate(self.history):
            validate_state(record.state)
            if record.previous != previous:
                raise Rejected("history_link_mismatch")
            if record.action != ("genesis" if index == 0 else record.action):
                raise Rejected("genesis_action_mismatch")
            if record.digest != checkpoint_hash(previous, record.action, record.state):
                raise Rejected("history_digest_mismatch")
            if index and record.state.revision != self.history[index - 1].state.revision + 1:
                raise Rejected("revision_gap")
            previous = record.digest
        return True

    def _commit(self, proposal: State, action: str) -> dict:
        self.verify_history()
        current = self.state
        try:
            validate_state(proposal)
            if proposal.worldline != current.worldline or proposal.time != current.time:
                raise Rejected("identity_or_time_changed")
            if proposal.revision != current.revision + 1:
                raise Rejected("nonmonotone_revision")
        except Rejected as exc:
            self.rejections.append(str(exc))
            return {"status": "DENIED", "reason": str(exc),
                    "head": self.history[-1].digest,
                    "state": state_data(self.state)}
        previous = self.history[-1].digest
        digest = checkpoint_hash(previous, action, proposal)
        self.history.append(Checkpoint(proposal, previous, action, digest))
        return {"status": "COMMITTED", "action": action,
                "head": digest, "state": state_data(self.state)}

    def apply(self, action: str) -> dict:
        """Known actions only; no arbitrary program execution or side effects."""
        self.verify_history()
        s = self.state
        if action == "split":
            candidate = replace(s, cookies=(1, 1, 1), revision=s.revision + 1)
        elif action == "hold":
            candidate = replace(s, revision=s.revision + 1)
        else:
            self.rejections.append("action_not_allowed")
            return {"status": "DENIED", "reason": "action_not_allowed",
                    "head": self.history[-1].digest, "state": state_data(s)}
        return self._commit(candidate, action)

    def test_fault(self, kind: str) -> dict:
        """Deliberate in-memory fault injection for regression testing only."""
        s = self.state
        if kind == "drop":
            candidate = replace(s, cookies=(1, 1, 0), revision=s.revision + 1)
        elif kind == "worldline":
            candidate = replace(s, worldline=23, revision=s.revision + 1)
        elif kind == "negative":
            candidate = replace(s, cookies=(4, -1, 0), revision=s.revision + 1)
        else:
            return self.apply("__unknown__")
        return self._commit(candidate, "test_fault_" + kind)

    def restore(self, index: int) -> dict:
        """Restore *logical bytes/state*, not past physical events or persons."""
        self.verify_history()
        if type(index) is not int or not (0 <= index < len(self.history)):
            self.rejections.append("missing_checkpoint")
            return {"status": "DENIED", "reason": "missing_checkpoint",
                    "head": self.history[-1].digest,
                    "state": state_data(self.state)}
        s = self.history[index].state
        proposal = replace(s, revision=self.state.revision + 1)
        return self._commit(proposal, "restore_" + str(index))


def _fraction(value: object) -> Fraction:
    if not isinstance(value, str) or len(value) > 128:
        raise Rejected("invalid_rational")
    try:
        f = Fraction(value)
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise Rejected("invalid_rational") from exc
    return f


def validate_tm009_certificate(data: dict) -> dict:
    """Verify internal algebra and G257 consistency of exact TM-009 output.

    This is NOT proof of origin/authenticity: anyone can re-encode JSON.
    """
    if type(data) is not dict or data.get("system") != "UGTM-UCP-EXACT":
        raise Rejected("wrong_certificate_kind")
    if data.get("model_only") is not True or data.get("physical_chronon_proven") is not False:
        raise Rejected("scientific_status_mismatch")
    if data.get("U3") is not True or data.get("FI_theta_interior_limit") != "2":
        raise Rejected("incomplete_model_checks")
    q = _fraction(data.get("tau_squared"))
    if q < 0 or _fraction(data.get("boost_tau_squared")) != q:
        raise Rejected("lorentz_interval_mismatch")
    n = math.isqrt(q.numerator)
    d = math.isqrt(q.denominator)
    sqrt_q = str(Fraction(n, d)) if n * n == q.numerator and d * d == q.denominator else "sqrt(" + str(q) + ")"
    if data.get("proper_time") != sqrt_q:
        raise Rejected("proper_time_mismatch")
    values = data.get("P")
    if type(values) is not list or len(values) != 3:
        raise Rejected("invalid_probability_vector")
    p = tuple(_fraction(x) for x in values)
    if any(x < 0 for x in p) or sum(p) != 1 or p[0] <= 0 or p[1]**2 != 4 * p[0] * p[2]:
        raise Rejected("three_state_invariant_failed")
    if _fraction(data.get("FI_u_interior_limit")) != 8 * p[0]:
        raise Rejected("fisher_identity_failed")
    amps = data.get("amplitudes")
    if type(amps) is not list or len(amps) != 3 or type(amps[1]) is not str or not amps[1].startswith("sqrt(2)*"):
        raise Rejected("invalid_amplitudes")
    a, b, c = _fraction(amps[0]), _fraction(amps[1][8:]), _fraction(amps[2])
    if min(a, b, c) < 0 or (a*a, 2*b*b, c*c) != p:
        raise Rejected("amplitude_probability_mismatch")
    entropy = ("0" if p == (1, 0, 0) else
               "3/2" if p == (Fraction(1,4), Fraction(1,2), Fraction(1,4)) else
               "-(" + "+".join(str(x) + "*log2(" + str(x) + ")" for x in p if x) + ")")
    if data.get("H_bits") != entropy:
        raise Rejected("entropy_expression_mismatch")
    digits = data.get("godel257")
    if type(digits) is not str or not digits.isascii() or not digits.isdecimal() or len(digits) > 4000:
        raise Rejected("invalid_godel_certificate")
    payload = dict(data)
    payload.pop("godel257", None)
    encoded = canonical(payload)
    code = 1
    for value in encoded:
        code = 257 * code + value + 1
    if str(code) != digits:
        raise Rejected("godel_roundtrip_mismatch")
    return {"status": "VERIFIED_MODEL_CERTIFICATE",
            "scope": "algebraic_internal_consistency_only",
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "probabilities": list(map(str, p))}


def read_certificate(path: Path) -> dict:
    if path.stat().st_size > MAX_CERTIFICATE_BYTES:
        raise Rejected("certificate_too_large")
    with path.open("rb") as f:
        raw = f.read(MAX_CERTIFICATE_BYTES + 1)
    if len(raw) > MAX_CERTIFICATE_BYTES:
        raise Rejected("certificate_too_large")
    try:
        obj = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        raise Rejected("invalid_json") from exc
    return validate_tm009_certificate(obj)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fault", choices=("drop", "negative", "worldline"),
                    help="Demonstrate a deliberately rejected simulated transition")
    ap.add_argument("--restore", action="store_true",
                    help="Demonstrate restoring the initial logical checkpoint")
    ap.add_argument("--certificate", type=Path,
                    help="Read and inspect an explicitly selected TM-009 JSON report")
    args = ap.parse_args()
    g = Guardian()
    results = [g.apply("split")]
    if args.fault:
        results.append(g.test_fault(args.fault))
    if args.restore:
        results.append(g.restore(0))
    report = {"system": "DTM22-PROTECTIVE-COMPUTATION", "worldline_axiom_only": True,
              "transitions": results, "state": state_data(g.state),
              "chain_valid": g.verify_history(), "checkpoints": len(g.history),
              "rejections": g.rejections, "physical_protection_proven": False,
              "executed_external_commands": False}
    if args.certificate is not None:
        try:
            report["tm009_certificate"] = read_certificate(args.certificate)
        except (Rejected, OSError) as exc:
            report["tm009_certificate"] = {"status": "DENIED",
                                          "reason": str(exc)}
    print(json.dumps(report, separators=(",", ":"), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
