# Let's Prove It Again  ·  `letsproveitagain`
- **Category:** zkp · **Points:** 175 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/letsproveitagain/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** Same Schnorr-over-flag setup as part 1 (`y = 2^FLAG mod p`, `r = (v - c·FLAG) mod (p-1)`), "fixed" by the intern in three ways that introduce a *better* flaw:

**Skills exercised:** —
**Concepts:** [`crt`](../../../TAGS/crt.md), [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
