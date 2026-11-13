# Let's Decrypt Again  ·  `lets_decrypt_2`
- **Category:** rsa · **Points:** 175 · **Solved:** 2026-10-23 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/lets_decrypt_2/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The server verifies `pow(SIGNATURE, e, n) == PKCS1v15-digest(msg)` with **attacker-chosen

**Skills exercised:** —
**Concepts:** [`dlp-index-calc`](../../../TAGS/dlp-index-calc.md), [`groebner-sat`](../../../TAGS/groebner-sat.md)
**Scripts here:** `probe.py`, `solve.py`

Full record: [AAR.md](AAR.md)
