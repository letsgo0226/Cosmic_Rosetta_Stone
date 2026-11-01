#!/usr/bin/env python3
"""Bounded deterministic single-tape Turing machine simulator."""
import argparse
import json
from pathlib import Path

def encode(data: bytes) -> int:
    n = 1
    for byte in data:
        n = n * 257 + byte + 1
    return n

def decode(n: int) -> bytes:
    if not isinstance(n, int) or n < 1:
        raise ValueError('invalid Gödel code')
    out = []
    while n > 1:
        n, r = divmod(n, 257)
        if not r:
            raise ValueError('invalid Gödel code')
        out.append(r - 1)
    return bytes(reversed(out))

def simulate(program: dict, limit: int = 1000) -> dict:
    if not 0 <= limit <= 100000:
        raise ValueError('limit must be 0..100000')
    rules = {}
    for state, symbol, next_state, write, move in program['rules']:
        if move not in ('L', 'R', 'N') or len(symbol) != 1 or len(write) != 1:
            raise ValueError('invalid rule')
        key = (state, symbol)
        if key in rules:
            raise ValueError('nondeterministic duplicate rule')
        rules[key] = (next_state, write, move)
    tape = {i: c for i, c in enumerate(program.get('tape', '')) if c != '_'}
    head, state = program.get('head', 0), program.get('start', 0)
    for step in range(limit + 1):
        symbol = tape.get(head, '_')
        rule = rules.get((state, symbol))
        if rule is None:
            return {'status': 'HALT', 'steps': step, 'state': state, 'head': head,
                    'tape': sorted(tape.items())}
        if step == limit:
            return {'status': 'LIMIT', 'steps': step, 'state': state, 'head': head,
                    'tape': sorted(tape.items())}
        state, write, move = rule
        if write == '_':
            tape.pop(head, None)
        else:
            tape[head] = write
        head += {'L': -1, 'R': 1, 'N': 0}[move]
    raise AssertionError('unreachable')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('program', nargs='?', default='examples/halts.json')
    parser.add_argument('--limit', type=int, default=1000)
    args = parser.parse_args()
    program = json.loads(Path(args.program).read_text(encoding='utf-8'))
    data = json.dumps(program, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    assert decode(encode(data)) == data
    print(json.dumps({'machine': 'Three-Cat-Cookies-Master', 'godel_digits': len(str(encode(data))),
                      'result': simulate(program, args.limit), 'physical_actuality': 'UNPROVEN'},
                     ensure_ascii=False))

if __name__ == '__main__':
    main()
