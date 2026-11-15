# An Exceptional Twisted Mind  ·  `exceptional_twisted_mind`
- **Category:** ecc · **Points:** 125 · **Solved:** 2026-10-23 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/exceptional_twisted_mind/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The response is an x-coordinate mod p², not mod p — so it can be **lifted back to a full point** Q̃ = (r, ±√f(r)) mod p² (f(r) is a QR mod p² since r ≡ x of a genuine point mod p; sqrt via a^((p+1)/4) mod p then one Hens…

**Skills exercised:** —
**Concepts:** [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md)
**Scripts here:** `card3.gp`, `facm.gp`, `factcub.gp`, `factw.gp`, `probe.py`, `probe2.py`, `probe_live.py`, `roots.gp`, `solve.py`

Full record: [AAR.md](AAR.md)
