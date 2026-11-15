---
record: agent-aar
puzzle: challenge-207-cryptohack-two_isogenies
category: isogenies
url: https://cryptohack.org/challenges/two_isogenies/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/isogenies/challenge-7-cryptohack-two_isogenies/flag.txt"
flag_sha256: 4f23da8798b631cf06454a9dd395063326f26b25d225d76752733190f41566dc
skills: [ctf-isogenies]
human_twin: AAR.md
---

# AGENT — two_isogenies (CryptoHack Isogenies, 30 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Method that worked" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **PARI/GP `ellisogeny`** (gp64 2.17.4, file-based `-f -q`):
   `bnfinit(t^2+1); i=Mod(t,t^2+1); E=ellinit([0,0,0,1,0],K); ph=ellisogeny(E,[i,0]);`
   → codomain **y² = x³ + 11x + 14i** (over Q(i)); j(E′) read from `ellinit(ph[1])[13]`
   = `Mod(287496, t²+1)` (base-field, 0·i part).
2. **Independent Python cross-check** (rational j formula for y²=x³+Ax+B):
   j = 6912·A³/(4A³+27B²), A=11, B=14i ⇒ B²=−196 ⇒ j = 9199872/32 = **287496**. Both methods
   agree exactly.
3. Non-singularity: discriminant −16(4·11³+27·(−196)) = −512 ≠ 0.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First submission 273636428973 (rejected): came from a mis-memorized codomain
  formula a′ = a−4r², b′ = b−8r³ (the x-only/Montgomery-style 2-isogeny, not this
  short-Weierstrass Vélu codomain). Wrong formula, not wrong arithmetic.
- Several turns burned hand-rolling a Vélu *point map* that "never landed": a
  correct map cannot land on a wrong codomain.

## artifacts [OBSERVED]
- code: solve.gp, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PARI/GP 2.17.4 ellisogeny (ground truth for the codomain).
- Standard Vélu formulas (textbook math; the mis-memorized variant was corrected
  against PARI).
- No CryptoHack solutions page or third-party writeup consulted for this challenge
  (run log).
