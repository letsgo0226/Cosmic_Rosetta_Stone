#!/usr/bin/env python3
"""Regression tests for TM-009's exact-symbolic active research entry.

These checks establish specific finite rational identities and byte-identity,
not numerical certainty about physics or a general halting procedure.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib
import json
import math
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / 'tools/load_research_machine.py'
EXACT = ROOT / 'machines/UGTM_UCP_Exact_Encoding_2KB.sh'
EXACT_ARCHIVE = ROOT / '永久記憶/圖靈機/UGTM_UCP_Exact_Encoding_2KB.sh'
LEGACY = ROOT / 'machines/Photonic_Singularity_Universal_God_Turing_Machine.sh'
LEGACY_ARCHIVE = ROOT / '永久記憶/圖靈機/Photonic_Singularity_Universal_God_Turing_Machine.sh'
MANIFEST = ROOT / 'deployment/research_machine_loader.json'

CASES = [
    ('10', '.6', '.3', '1'),
    ('10', '-.6', '.3', '1/2'),
    ('0', '0', '0', '0'),
    ('1', '.9', '-.7', '2'),
    ('13/2', '-1/2', '1/3', '3/4'),
    ('3', '0', '.3', '.4'),
    ('7/3', '-1/5', '1/8', '5/7'),
    ('100', '99/100', '-99/100', '1/11'),
    ('1', '0', '0', '1'),
    ('0', '0', '0', '1/3'),
]


def git_blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def verify_registry():
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    assert manifest['registry_id'] == 'TM-009'
    assert manifest['entrypoint'] == 'machines/UGTM_UCP_Exact_Encoding_2KB.sh'
    assert manifest['archive'] == '永久記憶/圖靈機/UGTM_UCP_Exact_Encoding_2KB.sh'
    assert manifest['previous_entrypoint'] == 'machines/Photonic_Singularity_Universal_God_Turing_Machine.sh'
    assert manifest['production_deployment_unchanged'] is True
    for file, archive, size, sha in (
        (EXACT, EXACT_ARCHIVE, 1318, 'f8b2e2978b7de898b226d8014fbac0e7614a4589'),
        (LEGACY, LEGACY_ARCHIVE, 1934, '051af140a8560e340e215631926da32d1afba3bb'),
    ):
        b = file.read_bytes()
        assert len(b) == size and git_blob_sha(b) == sha
        assert archive.read_bytes() == b
    view = json.loads(subprocess.check_output(
        ['python3', str(LOADER)], text=True, cwd=ROOT, timeout=15
    ))
    assert view['verified'] is True
    assert view['execution'] == 'not_run'
    assert view['entrypoint'] == manifest['entrypoint']


def verify_case(args):
    raw = subprocess.check_output(['bash', str(EXACT), *args], text=True, cwd=ROOT, timeout=15)
    obj = json.loads(raw)
    T, v, f, u = map(F, args)
    q = T*T*(1-v*v)
    prob = [F(1,1)/(1+u*u)**2, 2*u*u/(1+u*u)**2, u**4/(1+u*u)**2]
    assert obj['tau_squared'] == obj['boost_tau_squared'] == str(q)
    n, d = math.isqrt(q.numerator), math.isqrt(q.denominator)
    tau = str(F(n,d)) if n*n == q.numerator and d*d == q.denominator else 'sqrt('+str(q)+')'
    assert obj['proper_time'] == tau
    assert list(map(F, obj['P'])) == prob and sum(prob) == 1
    assert obj['FI_u_interior_limit'] == str(8/(1+u*u)**2)
    assert obj['FI_theta_interior_limit'] == '2'
    assert obj['U3'] is True and obj['physical_chronon_proven'] is False
    assert obj['H_bits'] == ('0' if u == 0 else '3/2') if u in (F(0), F(1)) else 'log2(' in obj['H_bits']
    copy = dict(obj)
    supplied = int(copy.pop('godel257'))
    encoded = json.dumps(copy, sort_keys=True, separators=(',', ':')).encode()
    num = 1
    for value in encoded:
        num = num*257+value+1
    assert supplied == num


def main():
    verify_registry()
    for args in CASES:
        verify_case(args)
    active = json.loads(subprocess.check_output(
        ['python3', str(LOADER), '--run', '10', '0.6', '0.3', '1'],
        text=True, cwd=ROOT, timeout=15
    ))
    assert active['proper_time'] == '8'
    assert active['P'] == ['1/4', '1/2', '1/4']
    for args in (
        ('-1', '0', '0', '1'),
        ('1', '1', '0', '1'),
        ('1', '0', '-1', '1'),
        ('1', '0', '0', '-1'),
    ):
        result = subprocess.run(['bash', str(EXACT), *args], cwd=ROOT,
                                capture_output=True, timeout=15)
        assert result.returncode != 0, args
    print('PASS: 10 exact cases; 4 invalid-input checks; active loader; two archived identities')


if __name__ == '__main__':
    main()
