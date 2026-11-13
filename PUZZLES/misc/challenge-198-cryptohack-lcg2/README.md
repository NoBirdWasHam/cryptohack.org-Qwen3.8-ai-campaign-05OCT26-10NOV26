# Trust Games  ·  `lcg2`
- **Category:** misc · **Points:** 150 · **Solved:** 2026-10-12 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/lcg2/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** solved: B8 lattice CVP recovers 48-bit LCG state from 8 top-bytes; key[0:8]=forward w1 (pt[8:16]), key[8:16]=backward k9 (IV[0:8]); a odd=>invertible. 50/50 local, live OK.

**Skills exercised:** —
**Concepts:** [`lattice-reduction`](../../../TAGS/lattice-reduction.md)
**Scripts here:** `diag.py`, `local_check.py`, `solve.py`, `test_lcg2.py`

Full record: [AAR.md](AAR.md)
