# Edwards Goes Degenerate  ·  `degenerate`
- **Category:** ecc · **Points:** 100 · **Solved:** 2026-11-02 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/degenerate/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** two public keys (xbit, y), AES-CBC flag under sha1(str(shared_secret))[:16].

**Skills exercised:** —
**Concepts:** [`ecdh-dh`](../../../TAGS/ecdh-dh.md), [`aes-gcm`](../../../TAGS/aes-gcm.md), [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md)
**Scripts here:** `card2.gp`, `fac.gp`, `facp1.gp`, `fo.gp`, `solve.py`

Full record: [AAR.md](AAR.md)
