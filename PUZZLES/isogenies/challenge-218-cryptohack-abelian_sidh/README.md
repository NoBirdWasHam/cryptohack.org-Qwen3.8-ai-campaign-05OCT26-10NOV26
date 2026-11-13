# Abelian SIDH  ·  `abelian_sidh`
- **Category:** isogenies · **Points:** 90 · **Solved:** 2026-10-21 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/abelian_sidh/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** p = 2^216·3^137·q − 1 (q 256-bit), E: y²=x³+x over F_{p²}, G = random·(2^216·3^137).

**Skills exercised:** —
**Concepts:** [`isogeny`](../../../TAGS/isogeny.md), [`ecdh-dh`](../../../TAGS/ecdh-dh.md), [`aes-gcm`](../../../TAGS/aes-gcm.md), [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
