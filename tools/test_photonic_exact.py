#!/usr/bin/env python3
"""Deterministic exact-encoding tests for the UGTM-UCP 2 KB companion.

These tests verify specified mathematical identities, not empirical physics.
"""
from pathlib import Path
from fractions import Fraction
import subprocess
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
EXACT = ROOT / 'machines/UGTM_UCP_Exact_Encoding_2KB.sh'
PHOTONIC = ROOT / 'machines/Photonic_Singularity_Universal_God_Turing_Machine.sh'
ARCHIVE = ROOT / '永久記憶/圖靈機/Photonic_Singularity_Universal_God_Turing_Machine.sh'
LOADER = ROOT / 'tools/load_research_machine.py'


def execute(*args):
    data = subprocess.check_output(['bash', str(EXACT), *args], cwd=ROOT, text=True, timeout=12)
    return json.loads(data)


def main():
    assert len(EXACT.read_bytes()) == 1318
    assert len(PHOTONIC.read_bytes()) == 1934
    assert PHOTONIC.read_bytes() == ARCHIVE.read_bytes()
    blob = PHOTONIC.read_bytes()
    sha = hashlib.sha1(b'blob ' + str(len(blob)).encode() + b'\0' + blob).hexdigest()
    assert sha == '051af140a8560e340e215631926da32d1afba3bb'
    message = json.loads(subprocess.check_output(['python3', str(LOADER)], cwd=ROOT, text=True, timeout=12))
    assert message['verified'] and message['execution'] == 'not_run'

    cases = [
        (('10', '.6', '.3', '1'), '64', '8', ['1/4', '1/2', '1/4'], '3/2', '2'),
        (('10', '-.6', '.3', '1/2'), '64', '8', ['16/25', '8/25', '1/25'], None, '128/25'),
        (('0', '0', '0', '0'), '0', '0', ['1', '0', '0'], '0', '8'),
        (('1', '.9', '-.7', '2'), '19/100', 'sqrt(19/100)', ['1/25', '8/25', '16/25'], None, '8/25'),
        (('13/2', '-1/2', '1/3', '3/4'), '507/16', 'sqrt(507/16)', ['256/625', '288/625', '81/625'], None, '2048/625'),
    ]
    for args, tau2, tau, p, h, fi in cases:
        r = execute(*args)
        assert r['tau_squared'] == tau2 == r['boost_tau_squared']
        assert r['proper_time'] == tau
        assert r['P'] == p
        assert sum(Fraction(x) for x in r['P']) == 1
        assert r['FI_u_interior_limit'] == fi
        assert r['FI_theta_interior_limit'] == '2'
        assert r['U3'] is True
        assert r['physical_chronon_proven'] is False
        if h is not None:
            assert r['H_bits'] == h
        else:
            assert 'log2' in r['H_bits']
        assert r['godel257'].isdigit()
    print('PASS: loader integrity, archive identity, and 5 exact arithmetic cases')


if __name__ == '__main__':
    main()
