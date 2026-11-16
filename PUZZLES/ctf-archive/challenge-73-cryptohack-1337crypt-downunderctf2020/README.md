# crypt (DownUnderCTF) — CryptoHack archive challenge-13396  ·  `challenge-73-cryptohack-1337crypt-downunderctf2020`
- **Category:** misc · **Solved:** 2026-11-05 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/1337crypt-downunderctf2020/
- **Flag:** flag file (sha256 verified) (provenance + sha256 in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** RSA-modulus n = pq (1337-bit primes), hint = int(D*(sqrt(p)+sqrt(q))) with D = 63^14 (~2^84),

**Skills exercised:** `bivariate-coppersmith-hint-factoring`
**Concepts:** [rsa](../../../TAGS/rsa.md), [coppersmith](../../../TAGS/coppersmith.md), [lattice-reduction](../../../TAGS/lattice-reduction.md), [crt](../../../TAGS/crt.md), [groebner-sat](../../../TAGS/groebner-sat.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** `dbg.py`, `dbg2.py`, `dbg3.py`, `dbg4.py`, `dbg5.py`, `dbg_mini.py`, `dbg_port.py`, `diag.gp`, `diag2.gp`, `red.gp`, `red2.gp`, `redB.gp`, `redK2.gp`, `redU.gp`, `solve.py`, `solve2.py`, `solve3.py`, `solve4.py`, `solve4_part1.py`, `solve_coppersmith_port.py`, `solve_v1_old.py`, `test_mini.py`, `test_mini2.py`, `tiny.gp`

Full record: [AAR.md](AAR.md)
