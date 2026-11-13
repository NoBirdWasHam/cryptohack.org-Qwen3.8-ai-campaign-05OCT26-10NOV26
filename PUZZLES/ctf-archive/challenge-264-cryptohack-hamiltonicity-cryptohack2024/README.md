# Hamiltonicity (CryptoHack)  ·  `hamiltonicity-cryptohack2024`
- **Category:** ctf-archive · **Points:** 0 · **Solved:** 2026-10-25 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/hamiltonicity-cryptohack2024/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** Per-round Fiat–Shamir challenge bit depends **only on the prover's commitment matrix A** (the graph openings / permutation are not hashed). Pedersen commitments are re-randomizable: `c·h2^r'` opens to the same message wi…

**Skills exercised:** —
**Concepts:** [`fiat-shamir-forgery`](../../../TAGS/fiat-shamir-forgery.md), [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `example.py`, `solve.py`

Full record: [AAR.md](AAR.md)
