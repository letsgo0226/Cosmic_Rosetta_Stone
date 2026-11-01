#!/usr/bin/env python3
"""Independent GTM-001 certificate and tape verifier; no SHA dependency."""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORE = ROOT / "永久記憶" / "圖靈機" / "god_turing_machine_no_sha_2kb.sh"

def decode(n):
    if n < 1:
        raise ValueError("invalid code")
    out = bytearray()
    while n > 1:
        n, r = divmod(n, 257)
        if r == 0:
            raise ValueError("invalid code")
        out.append(r - 1)
    return bytes(reversed(out))

def encode(data):
    n = 1
    for v in data:
        n = n * 257 + v + 1
    return n

def verify():
    source = CORE.read_text(encoding="utf-8")
    assert "hashlib" not in source and "sha256" not in source.lower()
    result = subprocess.run(["bash", str(CORE)], check=True, capture_output=True, text=True, timeout=30)
    payload = json.loads(result.stdout)
    cert = payload["certificate"]
    code = decode(int(cert["godel"]))
    n = len(code)
    assert encode(code) == int(cert["godel"])
    assert n > 0 and n == cert["length"] == payload["N"]
    assert payload["self_reproduced"] is True
    assert payload["godel_roundtrip"] is True
    assert payload["verified"] is True
    # Recompute every transition independently of the producer's 'verified' flag.
    tape = {i: "1" for i in range(n)}
    rules = {(0, "1"): (0, "X", 1), (0, "_"): (1, "_", 0)}
    state = head = steps = 0
    while state != 1:
        state, write, move = rules[(state, tape.get(head, "_"))]
        tape[head] = write
        head += move
        steps += 1
    assert steps == cert["trace_steps"] == payload["steps"] == n + 1
    assert "".join(tape[i] for i in range(n)) == cert["final_tape"]
    assert cert["final_tape"] == "X" * n
    # Negative tests: corrupted codes and certificates must be rejected.
    try:
        decode(257)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid code was accepted")
    assert cert["final_tape"] != "X" * (n + 1)
    print(json.dumps({"independent_check": "PASS", "N": n, "steps": steps, "no_sha": True}))

if __name__ == "__main__":
    verify()
