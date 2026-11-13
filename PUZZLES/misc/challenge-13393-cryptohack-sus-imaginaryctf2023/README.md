# # AAR — sus (ImaginaryCTF 2023), CryptoHack archive #13393  ·  `challenge-13393-cryptohack-sus-imaginaryctf2023`
- **Category:** misc · **Solved:** 2026-11-08 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/sus-imaginaryctf2023/
- **Flag:** flag file (sha256 verified) (provenance + sha256 in `FLAGS/INDEX.jsonl`)

**Method (lead from the AAR):** Key structure: `q = p²+p+1` ⟺ `(2p+1)² ≡ −3 (mod q)`, `p³ ≡ 1 (mod q)`, `q−1 = p(p+1)`,

**Skills exercised:** `coppersmith-vanishing-sanity`, `poly-ring-toolkit`
**Concepts:** [rsa](../../../TAGS/rsa.md), [coppersmith](../../../TAGS/coppersmith.md), [lattice-reduction](../../../TAGS/lattice-reduction.md), [isogeny](../../../TAGS/isogeny.md), [dlp-index-calc](../../../TAGS/dlp-index-calc.md), [groebner-sat](../../../TAGS/groebner-sat.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** `batt.gp`, `batt2.gp`, `diag_toy.py`, `nval.gp`, `pfac.gp`, `probe1.py`, `probe2.py`, `run5_artifact_sweep.py`, `run5_pin_battery.py`, `solve_cyc.py`, `solve_toy.py`, `solve_toy2.py`, `solve_toy3.py`, `solve_toy4.py`, `solve_toy5.py`

Full record: [AAR.md](AAR.md)
