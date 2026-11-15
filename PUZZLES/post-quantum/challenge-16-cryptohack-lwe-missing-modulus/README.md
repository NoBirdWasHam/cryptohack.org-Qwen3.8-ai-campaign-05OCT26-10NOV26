# Missing Modulus  ·  `lwe-missing-modulus`
- **Category:** post-quantum · **Points:** 80 · **Solved:** 2026-10-13 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/lwe-missing-modulus/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** LWE **without modulus on the noise**: b = A*S + m*delta + e over the reals (e ~ N(0, 3.8) scalar per sample), n=512, q=6007, delta=23 (socket 13412).

**Skills exercised:** —
**Concepts:** [`lattice-reduction`](../../../TAGS/lattice-reduction.md), [`ntru-lwe`](../../../TAGS/ntru-lwe.md), [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** —

Full record: [AAR.md](AAR.md)
