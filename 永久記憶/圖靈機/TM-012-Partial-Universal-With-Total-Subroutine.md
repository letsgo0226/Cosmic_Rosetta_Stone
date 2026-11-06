# TM-012 — Partial Universal Interpreter with a Certified Total Temporal Subroutine

**Registry ID:** TM-012  
**Registration date:** 2026-11-07  
**Status:** research architecture; not a Total Universal Turing machine.

## Formal role

TM-012 separates two computability-theoretic roles that cannot be conflated:

1. `bf` mode implements the eight Brainfuck operations `+-<>.,[]`. Under the ideal unbounded-memory semantics of Brainfuck, this is the partial universal branch. A program such as `+[]` does not halt.
2. `total` mode explicitly invokes the preserved TM-011 unary temporal-certificate core. For every promised input `1^N`, that subroutine halts after `N+1` transitions and returns a finite, contiguous, replayable trace.

Thus the architecture is:

```text
partial universal interpreter + certified total subroutine
```

It is not:

```text
total universal machine
```

The totality of one subroutine does not make the universal interpreter total.

## Canonical prototype

- [Strict physical one-line program](tm012_partial_universal_total_subroutine_2kb.sh)
- Maximum size: 2,048 bytes.
- `bash ... total 111` runs TM-011's certified unary branch.
- `bash ... bf PROGRAM INPUT` runs the Brainfuck branch; input is interpreted as UTF-8 bytes.
- The fixed Brainfuck self-test `++++++++[>++++++++++<-]>+++.` outputs hexadecimal `53` (`S`).

## Limits

The executable is hosted by finite Python hardware; the claim of universality applies to the ideal Brainfuck semantics with unbounded resources, not to physically unlimited execution. A timeout can establish only that a run has not halted within the chosen bound, not that it will never halt. No SHA, floating-point arithmetic, network, deployment, trading, physical time particle, physical singularity, or halting oracle is introduced.
