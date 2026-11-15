---
record: agent-aar
puzzle: challenge-213-cryptohack-five_iso_csidh_twist
category: isogenies
url: https://cryptohack.org/challenges/five_iso_csidh_twist/
status: solved
date: 2026-10-15
flag_ref: "FLAGS/isogenies/challenge-15-cryptohack-five_iso_csidh_twist/flag.txt"
flag_sha256: 29e4967913b0cd86c82ee3c187e5aec668f94518e50b1c4891488f016e161724
skills: []
human_twin: AAR.md
---

# AGENT — five_iso_csidh_twist (CryptoHack Isogenies, 70 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Backward step on the 3-isogeny graph from E_0: y²=x³+x mod 419, via the quadratic twist:
1. E^t = twist(E_0, d=2): y²=x³+4x (d nonsquare; b=0 stays 0; #E^t=420).
2. P=(63,347) order-3 point on E^t; Vélu 3-isogeny → F: y²=x³+309x+326.
3. Untwist F with d=2 → G: y²=x³+398x+94 (the landed "backward" curve).
4. Montgomery A of G (principal sqrt): A = 261 (420/420 point-mapping verified).
Cross-check: forward 3-walk is a 27-cycle (palindromic j-seq); forward-26 ≡ backward-1,
landing in the same j=356 class as G (E_1 = y²=x³+182x+64, PARI-verified, A=158=−261).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First attempt assumed the 3-isogeny graph cycle length equals ℓ ("backward 1 =
  forward 2", A = 410): refuted instantly by the j-check (356 ≠ 180). Observed
  cycle lengths at p = 419: ℓ = 3 → 27, 5 → 9, 7 → 27. Never assume k = ℓ; run
  the forward walk to find k, and use the statement's k−1-forward test.

## artifacts [OBSERVED]
- code: flagA.py, solve_twist.py, velu_engine.py, walk3.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Quadratic twist swapping the two Galois-conjugate rational kernels: standard
  supersingular-curve theory (textbook level).
- Earlier server-verified AARs in this corpus (prime_power, secret_exponents) for
  the cycle data and the A sign-pair convention.
- No third-party writeups or solution pages consulted (run log).
