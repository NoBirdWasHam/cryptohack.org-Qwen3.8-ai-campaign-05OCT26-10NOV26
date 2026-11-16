# AAR — rsatogether (CryptoHack ctf-archive, ECSC 2024 Italy)  ·  `challenge-18-cryptohack-rsatogether-ecsc_2024_italy20`
- **Category:** ctf-archive · **Solved:** 2026-10-29 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/rsatogether-ecsc_2024_italy20/
- **Flag:** mirrored + checksummed in `FLAGS/INDEX.jsonl` (provenance + sha256)

**Method (lead from the AAR):** staircase Shamir-over-phi oracle -> exact dim-1 kernel combination = exact multiple of phi -> Miller/Sabt factoring from any phi-multiple -> decrypt. Self-derived; solved-list 278->279.

**Skills exercised:** poly-ring-toolkit
**Concepts:** [rsa](../../../TAGS/rsa.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** `client.py`, `ctcheck.py`, `detgrowth.py`, `exp1.py`, `factor_from_phi_multiple.py`, `fetch_all.py`, `getct.py`, `grow.py`, `kernel.py`, `keyreuse.py`, `live1.py`, `live2.py`, `nullspace.py`, `rsatogether.sage`, `sim.py`, `sim2.py`, `solve.py`

Full record: [AAR.md](AAR.md)
