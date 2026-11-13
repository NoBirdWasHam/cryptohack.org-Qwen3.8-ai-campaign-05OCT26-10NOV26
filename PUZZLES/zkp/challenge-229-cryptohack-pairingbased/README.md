# Pairing-Based Cryptography  ·  `pairingbased`
- **Category:** zkp · **Points:** 50 · **Solved:** 2026-10-12 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/pairingbased/
- **Flag:** `see FLAGS mirror` (provenance in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** solved: bit b -> zG=e(yG,bias*xG), bias=1 iff b=1; test zG==e(yG,xG) per bit (py_ecc)

**Skills exercised:** —
**Concepts:** —
**Scripts here:** `generate.py`, `probe.py`, `solve.py`

Full record: [AAR.md](AAR.md)
