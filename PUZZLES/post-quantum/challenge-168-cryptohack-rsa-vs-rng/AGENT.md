---
record: agent-aar
puzzle: challenge-168-cryptohack-rsa-vs-rng
category: post-quantum
url: https://cryptohack.org/challenges/rsa-vs-rng/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/misc/challenge-168-cryptohack-rsa-vs-rng/flag.txt"
flag_sha256: 323d9178ab937dfd086ae0babed652192482b5ddac9bd304b6709c0e49f41403
skills: []
human_twin: AAR.md
---

# AGENT — <!-- AAR -->
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
RSA primes P,Q are states of a public LCG mod 2^512 (A,B known) g steps apart: Q = A^g P + B(A^g-1)/(A-1). Substituting into P*Q = N gives a quadratic in P mod 2^512; Hensel-lift roots bit-by-bit for each gap g, test N % P == 0. Gap g=180 hit; factored N, decrypted ciphertext. See solve.py / solve.log.

Artifacts in this folder: `solve.py`, `solve.log`, `flag_rsa_vs_rng.txt`

## reusable-rules
When two RSA primes are related by a known polynomial (here LCG iterate composition), N=P*Q becomes a univariate equation mod 2^k — bit-by-bit Hensel lifting finds P without any facturbation of N; iterate over the unknown separation g.

## anti-patterns / limits
- Flag captured directly from the live listener; site auto-marks solved on listener capture.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_rsa_vs_rng.txt, solve.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "RSA vs RNG" (150 pts, slug `rsa-vs-rng`)
- **Interactive service:** socket.cryptohack.org (data challenge)
- **NOT consulted:** solutions pages, search-engine writeups (no-cheat rule)
