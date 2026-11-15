# Let's Prove It  ·  `letsproveit`
- **Category:** zkp · **Points:** 120 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/letsproveit/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** Despite the "Sigma protocol" framing, this is a **Schnorr/Fiat-Shamir proof of knowledge of the flag as a discrete log**: `y = 2^FLAG mod p`, `t = 2^v`, `c = sha3_256(t^y^g)^2`, `r = (v - c·FLAG) mod (p-1)`. Two flaws co…

**Skills exercised:** —
**Concepts:** [`fiat-shamir-forgery`](../../../TAGS/fiat-shamir-forgery.md), [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md), [`number-theory`](../../../TAGS/number-theory.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
