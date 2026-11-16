# # AAR — d-phi-enc (HackTM CTF 2023)  ·  `challenge-34-cryptohack-d-phi-enc-hacktm_ctf2023`
- **Category:** misc · **Solved:** 2026-11-02 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/d-phi-enc-hacktm_ctf2023/
- **Flag:** flag file (sha256 verified) (provenance + sha256 in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** RSA with e=3 leaks `enc_phi = phi^3 mod n` and `enc_d = d^3 mod n`. Since

**Skills exercised:** —
**Concepts:** [rsa](../../../TAGS/rsa.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** `solve.py`

Full record: [AAR.md](AAR.md)
