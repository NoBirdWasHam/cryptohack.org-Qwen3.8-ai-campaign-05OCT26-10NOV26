---
record: agent-aar
puzzle: challenge-209-cryptohack-secret_exponents
category: isogenies
url: https://cryptohack.org/challenges/csidh_secret_exponents/
status: solved
date: 2026-10-15
flag_ref: "FLAGS/isogenies/challenge-209-cryptohack-secret_exponents/flag.txt"
flag_sha256: f8bf41177a5f5e808a7ccb648b51080b031f15ca8018d91a576263d6cc626eb6
skills: []
human_twin: AAR.md
---

# AGENT — csidh_secret_exponents (CryptoHack Isogenies, 60 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Walk (Python engine, step-by-step)" [OBSERVED text; evidence tag applies to its source, not each claim]
```
step 1: l=3 gen=(178,52)  -> (182, 64)  j=356
step 2: l=3 gen=(199,366) -> (292,243)  j=180
step 3: l=5 gen=(308,238) -> (  0,303)  j=  0
step 4: l=5 gen=( 84,125) -> (133,360)  j=356
step 5: l=5 gen=( 27,111) -> ( 85,223)  j=396
step 6: l=7 gen=(233,389) -> (394,188)  j=396
step 7: l=7 gen=(112,106) -> (374,311)  j=407
step 8: l=7 gen=( 84,408) -> (335, 86)  j=356
step 9: l=7 gen=(186,186) -> (196,398)  j= 48   <- final
```

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- The "#E-prime = #E/ℓ" naive F_p point-count expectation is a red herring that
  nearly caused "fixing" a correct Vélu codomain (image = 84-point subgroup of a
  420-point curve).
- This PARI build's ellisogeny point map is broken (non-homomorphic); only its
  codomain coefficients are trustworthy — supersedes an earlier corpus lesson.
- Scratch helper used a wrong j_mont formula; corrected to
  256(A²−3)³/(A²−4).
- PARI parser friction (my() inside for-bodies, ellj on raw ph[1], etc.).

## artifacts [OBSERVED]
- code: velu_engine.py
- data/logs: crosscheck.log, walk.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PARI/GP ellisogeny — independent chain, codomain coefficients only.
- In-house ground truth: server-verified challenges 206 (special_isogenies) and
  210 (prime_power) from this same corpus.
- Standard Vélu / Montgomery-conversion math; no third-party writeups or solution
  pages consulted (run log).
