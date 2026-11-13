# No Difference  ·  `no_difference`
- **Category:** hashes · **Points:** 175 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/no_difference/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The hash's SBOX is NOT injective (rows satisfy S[x]=S[x^0x0F] plus cross-row duplicates).

**Skills exercised:** —
**Concepts:** [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `solve.py`, `solve2.py`

Full record: [AAR.md](AAR.md)
