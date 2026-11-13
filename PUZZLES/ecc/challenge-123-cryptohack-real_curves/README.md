# Real Curve Crypto  ·  `real_curves`
- **Category:** ecc · **Points:** 200 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/real_curves/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The "elliptic curve" is over **ℝ** (mpmath, dps=200), not a finite field: `y² = x³ − x`,

**Skills exercised:** —
**Concepts:** [`lattice-reduction`](../../../TAGS/lattice-reduction.md), [`aes-gcm`](../../../TAGS/aes-gcm.md), [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md)
**Scripts here:** `prep.gp`, `solve.py`

Full record: [AAR.md](AAR.md)
