---
record: agent-aar
puzzle: challenge-123-cryptohack-real_curves
category: ecc
url: https://cryptohack.org/challenges/real_curves/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/ecc/challenge-123-cryptohack-real_curves/flag.txt"
flag_sha256: ca38d56725bb20d21379ce377a01e4aa00aaef49fb29825efad761446110d108
skills: []
human_twin: AAR.md
---

# AGENT — 123-cryptohack-real_curves: Real Curve Crypto (CryptoHack, 200 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The "elliptic curve" is over **ℝ** (mpmath, dps=200), not a finite field: `y² = x³ − x`,
`P = N·G` with `N` = 128-bit AES key. The identity component of E(ℝ) is a **circle**
ℝ/ωℤ via the Weierstrass uniformization `x = ℘(u), y = −℘′(u)/2`, so the "DLP" is

    N·u_G − k·ω = u_P   (integers N < 2^128, k ≈ 0.4·N)

with ω the real period (= π/agm(1,√2) = 2.6220575542921198…; square period lattice, CM by i).
u_G and ω are computable to arbitrary precision (gx is an exact dyadic float); u_P is
recoverable from (px,py) to ~155–160 digits (the source's dps=200 double-and-add adds
error ≈ 2^127·10^-200 ≈ 10^-157 in u — measured empirically on a synthetic instance).
That precision surplus (≈155 digits ≫ 39 digits of secret) is the leak: the relation is
a **CVP with a huge gap**, not a hard DLP.

## reusable-rules
- "DLP over ℝ" on an elliptic curve = inhomogeneous Diophantine approximation
  ‖N·α − β‖ < ε on the circle. It is hard only when ε ≲ 1/N; when the data precision
  ε⁻¹ exceeds ~N², Kannan embedding solves it. (My initial 2D-CVP hardness analysis was
  wrong because I fixed the wrong target window; correct scaling makes the true vector
  the unique closest one.)
- Always recover the **sign of y** when inverting ℘: u and ω−u are the two points sharing
  an x; a wrong branch silently destroys the lattice relation.
- Measure numerical error empirically (dps=200 vs dps=500 rerun) before trusting a
  precision-budget argument.
- PARI `elllog(E,[x,y])` errored ("too few arguments") on this build; quadrature +
  `pi/agm(1,sqrt(2))` for the period worked fine.

## anti-patterns / limits
- Significant early effort went into a wrong hardness proof (concluding the instance was
  generic-hard); small-N brute force (N < 2·10^6) and the CF of α (no huge partial
  quotients) ruled out shortcuts before the lattice framing was fixed.
- The attack's success margin depends on the source's rounding error (~10^-157); with
  dps ≈ 120 instead of 200 the same lattice would fail (ε·2^P would exceed det^⅓).

## artifacts [OBSERVED]
- code: elog.py, prep.gp, solve.py
- data/logs: ab.txt, flag_real_curves.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/), ECC category, slug `real_curves`, contributed by jschnei
- **NOT consulted:** `/challenges/real_curves/solutions/`, /solves/, third-party writeups (no-cheat rule)
