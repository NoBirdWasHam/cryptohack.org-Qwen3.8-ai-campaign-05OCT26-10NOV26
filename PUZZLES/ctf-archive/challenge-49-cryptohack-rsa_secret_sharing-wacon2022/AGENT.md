---
record: agent-aar
puzzle: challenge-286-cryptohack-rsa_secret_sharing-wacon2022
category: ctf-archive
url: https://cryptohack.org/challenges/rsa_secret_sharing-wacon2022/
status: solved
date: 2026-10-30
flag_ref: "FLAGS/ctf-archive/challenge-49-cryptohack-rsa_secret_sharing-wacon2022/flag.txt"
flag_sha256: a2a4c2b28c84637201d19ae5fe18052adb6274483868587b8657e456a3dc0b31
skills: []
human_twin: AAR.md
---

# AGENT — AAR: rsa_secret_sharing-wacon2022 (challenge-286) — SOLVED (run 2)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (det-trick, no lattice)" [OBSERVED text; evidence tag applies to its source, not each claim]
a=x=b=1 -> stream1_j = j; n mod q = u*v exact -> roll indices;
R2_i = L2_u v + L2_v u (mod q) with L_j = C g^j + D -> triple-elimination
cofactors give sparse polys in g, gcd + roots over F_q (X^q-X intersect via
fast powmod + square-free CZ) + linear (C,D) solve; then
(n-low)/q^2 mod q = L3_u v + L3_v u (coefficients are STREAM-1 values, NOT
L2) -> same trick -> primes L3 q^2 + L2 q + j. The ONLY sound verification
is the full product pu*pv == n: mod-q^2/q^3 checks are tautologies of the
linear system -> enumerate all sols2 x sols3.

## reusable-rules
- Affine (additive) LCG1 stream turns "unknown roll index" into a solvable
  divisor-pair puzzle: n_i mod q = product of two small known-sequence values.
  This is the general "leak the sampler's clock through your own controllable
  digit" trick.
- LSB knowledge of BOTH RSA primes is worth exactly n^{2/3} of root volume and
  is NEVER enough for HG bivariate Coppersmith (needs <= n^{1/2}); do not burn
  hours trying it.

## anti-patterns / limits
- Did not solve; 0 of 4 factorizations produced; nothing submitted (correctly —
  a web-sourced flag would fail the audit even if accepted).
- The 429-solve CryptoHack crowd + author's exploit file exist; the exploit was
  deliberately NOT opened (it is this challenge's writeup; forbidden).
- Live PoW is slow single-process (~40-70M sha256 tries, ~60s); budget-limited
  number of sessions (each PoW costs ~1 min + 1 tool call).

## artifacts [OBSERVED]
- code: attack.py, dbg1.py, dbg2.py, dbg3.py, dbg4.py, dbg5.py, dbg6.py, dbg7.py, dbg8.py, dbg9.py, live_conn.py, live_run.py, sim_test2.py, sim_test3.py
- data/logs: captured_factors.json, live_instance.json, live_run.log, solve_captured.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
