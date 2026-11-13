# Cofactor Cofantasy  ·  `cofactor`
- **Category:** maths · **Points:** 150 · **Solved:** 2026-10-12 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/cofactor/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** solved: NO factoring. phi given -> Q=phi>>16 (odd part of 16 safe primes). g^Q order 2; h^Q in {1,gQ} iff h in <g> (uniform false-positive 2^-15). 344 bit-queries, 76s.

**Skills exercised:** —
**Concepts:** —
**Scripts here:** `factorN.gp`, `solve.py`

Full record: [AAR.md](AAR.md)
