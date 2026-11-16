---
record: agent-aar
puzzle: challenge-8-cryptohack-three_isogenies
category: isogenies
url: https://cryptohack.org/challenges/three_isogenies/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/isogenies/challenge-8-cryptohack-three_isogenies/flag.txt"
flag_sha256: 0452816ab53f9ec334da41f3a5a1172971e6414bc8e215420a295e44f0341d9d
skills: [ctf-isogenies]
human_twin: AAR.md
---

# AGENT — three_isogenies (CryptoHack Isogenies, 35 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Method" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Verified K ∈ E and 3K = O with an independent Python group-law implementation
   ([2]K = (483728976, 243099857880) = −K, consistent).
2. **PARI `ellisogeny`** (per `ctf-isogenies` skill): codomain
   y² = x³ + 417919813652 x + 36118389888 (mod p); j = `ellinit(ph[1])[13]` = [flag — recorded in FLAGS/isogenies/challenge-8-cryptohack-three_isogenies/flag.txt].
3. **Independent Python cross-check** with the standard j-formula
   j = c4³/D, c4 = −48a, D = −16(4a³+27b²): exact match [flag — recorded in FLAGS/isogenies/challenge-8-cryptohack-three_isogenies/flag.txt].

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Nothing failed on this run (run log); the speed came from banking the
  two_isogenies lessons first: never trust a memorized Vélu codomain formula — let
  PARI produce the codomain and cross-check j with the closed formula.
- Note (knowledge retrieval, stated plainly): the walk itself was delegated to
  PARI's built-in Vélu rather than re-derived from scratch.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PARI/GP ellisogeny (authoritative codomain).
- Standard Vélu / j-formula textbook math.
- No third-party writeups or solution pages consulted (run log).
