<!-- AAR -->
# AAR — challenge-168-cryptohack-rsa-vs-rng: RSA vs RNG (CryptoHack)

**Result:** SOLVED (account NoBirdWasHam; date 2026-10-21) — flag `[flag — recorded in FLAGS/misc/challenge-168-cryptohack-rsa-vs-rng/flag.txt]`
**Date:** 2026-10-21

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "RSA vs RNG" (150 pts, slug `rsa-vs-rng`)
- **Interactive service:** socket.cryptohack.org (data challenge)
- **NOT consulted:** solutions pages, search-engine writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/misc/challenge-168-cryptohack-rsa-vs-rng/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
RSA primes P,Q are states of a public LCG mod 2^512 (A,B known) g steps apart: Q = A^g P + B(A^g-1)/(A-1). Substituting into P*Q = N gives a quadratic in P mod 2^512; Hensel-lift roots bit-by-bit for each gap g, test N % P == 0. Gap g=180 hit; factored N, decrypted ciphertext. See solve.py / solve.log.

Artifacts in this folder: `solve.py`, `solve.log`, `flag_rsa_vs_rng.txt`

## Learning points
When two RSA primes are related by a known polynomial (here LCG iterate composition), N=P*Q becomes a univariate equation mod 2^k — bit-by-bit Hensel lifting finds P without any facturbation of N; iterate over the unknown separation g.

## Limitations
- Flag captured directly from the live listener; site auto-marks solved on listener capture.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
