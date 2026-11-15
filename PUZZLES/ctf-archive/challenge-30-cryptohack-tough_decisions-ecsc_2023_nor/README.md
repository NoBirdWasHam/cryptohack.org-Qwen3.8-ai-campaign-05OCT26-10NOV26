# # AAR — tough_decisions (ECSC 2023 Norway, ctf-archive)  ·  `challenge-13400-cryptohack-tough_decisions-ecsc_2023_nor`
- **Category:** misc · **Solved:** 2026-10-30 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/tough_decisions-ecsc_2023_nor/
- **Flag:** flag file (sha256 verified) (provenance + sha256 in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** LWE samples `(a, a·s + e mod 256)` vs uniform `(a, uniform)`, key = 16 bytes, 6 samples

**Skills exercised:** —
**Concepts:** [ntru-lwe](../../../TAGS/ntru-lwe.md)
**Scripts here:** `dbg1.py`, `solve.py`, `solve2.py`

Full record: [AAR.md](AAR.md)
