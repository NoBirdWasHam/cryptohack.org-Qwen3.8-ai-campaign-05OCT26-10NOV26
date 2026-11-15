# Elliptic Nodes  ·  `node`
- **Category:** ecc · **Points:** 150 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/node/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** 1. **Secret parameters aren't secret.** `source.py` hides `a, b` (`from secrets import a, b`), but both `G` and `Q = dG` satisfy `y² = x³ + ax + b (mod p)`. Two points ⇒ two linear equations in `(a, b)` ⇒ solve:

**Skills exercised:** —
**Concepts:** [`lattice-reduction`](../../../TAGS/lattice-reduction.md), [`ecdh-dh`](../../../TAGS/ecdh-dh.md), [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md), [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `check_singular.py`, `dl.gp`, `factor_pm1.gp`, `solve.py`

Full record: [AAR.md](AAR.md)
