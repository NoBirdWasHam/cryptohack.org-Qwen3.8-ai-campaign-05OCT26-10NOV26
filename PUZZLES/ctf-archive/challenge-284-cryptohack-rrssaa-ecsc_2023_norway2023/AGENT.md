---
record: agent-aar
puzzle: challenge-284-cryptohack-rrssaa-ecsc_2023_norway2023
category: ctf-archive
url: https://cryptohack.org/challenges/rrssaa-ecsc_2023_norway2023/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-284-cryptohack-rrssaa-ecsc_2023_norway2023/flag.txt"
flag_sha256: 11b79fe2651a57f1e03b93f74434610feef6f910e7be9fd2dec074e6490673f3
skills: []
human_twin: AAR.md
---

# AGENT — RRSSAA (ECSC 2023 Norway) — challenge-284
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
N = product of 126 RSA-style primes, where the i-th prime comes from a fresh
`random.Random()` seeded with `secrets.randbelow(2**i)`, i = 2..127, drawing
`_randbelow(2**256) | 1` until prime. e = 65537, flag = 128 bytes.
Two flaws stack:
1. For small i the seed space is tiny (seed < 2^i) → those primes are reproducible by
   re-seeding MT19937 and replaying the draw loop.
2. The flag (1024 bits) is far smaller than N (~32k bits), so you don't need the full
   factorization: ~5 prime factors with product P > 2^1024 suffice. Since P | N,
   m^e ≡ c (mod P), gcd(e, φ(P)) = 1, and m < P, RSA-decrypt mod P gives m exactly.

## reusable-rules
- Brute-forcing per-index (seed < 2^i, break on first N % p == 0) fails: seed 0's prime
  divides N and masks every index's real seed. Fix = one global seed scan, no break.
- Partial factorization + partial CRT works whenever message ≪ modulus — check message
  size before attempting full factorization.

## anti-patterns / limits
- Brute-forcing per-index (seed < 2^i, break on first N % p == 0) fails: seed 0's prime
  divides N and masks every index's real seed. Fix = one global seed scan, no break.
- Partial factorization + partial CRT works whenever message ≪ modulus — check message
  size before attempting full factorization.

## artifacts [OBSERVED]
- code: RRSSAA.py, solve.py
- data/logs: flag_rrssaa-ecsc_2023_norway2023.txt, output.txt, run2.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
