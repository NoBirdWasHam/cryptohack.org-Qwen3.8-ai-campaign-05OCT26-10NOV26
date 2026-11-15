# Megalomaniac 2  ·  `mega2`
- **Category:** web · **Points:** 120 · **Solved:** 2026-10-23 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/mega2/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** The login oracle (`send_challenge`) AES-ECB-decrypts an attacker-chosen `share_key_enc`

**Skills exercised:** —
**Concepts:** [`rsa`](../../../TAGS/rsa.md), [`coppersmith`](../../../TAGS/coppersmith.md), [`lattice-reduction`](../../../TAGS/lattice-reduction.md), [`crt`](../../../TAGS/crt.md), [`aes-gcm`](../../../TAGS/aes-gcm.md), [`padding-oracle`](../../../TAGS/padding-oracle.md)
**Scripts here:** `dbg1.py`, `dbg10.py`, `dbg11.py`, `dbg2.py`, `dbg3.py`, `dbg4.py`, `dbg5.py`, `dbg6.py`, `dbg7.py`, `dbg8.py`, `dbg9.py`, `solve_mega2.py`, `solve_mega2_v2.py`, `test_offline_v2.py`

Full record: [AAR.md](AAR.md)
