---
record: agent-aar
puzzle: challenge-16-cryptohack-lwe-missing-modulus
category: post-quantum
url: https://cryptohack.org/challenges/lwe-missing-modulus/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-16-cryptohack-lwe-missing-modulus/flag.txt"
flag_sha256: 55022b7453cb7815e02532f71a38a63b843a82524a599d3c79e16efd5f9cc049
skills: []
human_twin: AAR.md
---

# AGENT — Missing Modulus (challenge-180-cryptohack-lwe-missing-modulus)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Column lattice for no-modulus LWE: basis rows `[M[:,j], 0]` (j=1..512) + `[0..0, 1]`, target `(b, 0)`, residual `(-e, 0)`. LLL+Babai in 513 dim (fpylll; `closest_vector "proved"` capped at dim 256, so Babai) recovered `(M*S, 0)` with ||e||=84, max|e|=13. Solved `M @ S = w` exactly (float64 + round, integer-verified). Flag chars: `r = b - A*S` (per sample), pick m with |r - m*delta| <= 15.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First fetch pass recovered only 38/46 flag chars; 8 chars were re-fetched (listener flakiness, not math).
- fpylll `closest_vector(..., "proved")` caps at dimension 256, so the 513-dim solve used float Babai; the ||e|| << lattice-scale gap compensated for the missing proof.
- No other failed attempts are recorded in the run logs.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Listener server source cached at `_pq/13412.py`; data `_pq/_mm_data.json`; solvers `_pq/mm_solve*.py`, fetcher `_pq/mm_fetch.py`. No third-party solutions/writeups consulted (self-solve rule).
