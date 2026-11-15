---
record: agent-aar
puzzle: challenge-144-cryptohack-primed5
category: hashes
url: https://cryptohack.org/challenges/primed5/
status: solved
date: 2026-10-20
flag_ref: "FLAGS/hashes/challenge-5-cryptohack-primed5/flag.txt"
flag_sha256: 3ae0a42d42255f988fe9e5840ffd1cb8d13af139377f00168309029fc3308be6
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 144: PriMeD5
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (two flaws composed)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `sign` signs `MD5(long_to_bytes(p))` for prime p only; `check` verifies the SAME digest for ANY p
   (no primality re-check) and then leaks `FLAG[:gcd(a,p)]`.
2. ⇒ need MD5 collision (M1,M2), 128 B, `p=int(M1)` prime, `p'=int(M2)` with divisor `a ≥ 24 = len(FLAG)`.
   Sign p, check (p', sig, a) → `FLAG[:a]` = full flag.

## reusable-rules
- sign-prime/check-any is a classic "verification path must re-check ALL policy of the issuing path".
- `long_to_bytes` ⇒ reject collision messages with a leading 0x00 byte (int→bytes roundtrip differs).
- gcd oracle: `FLAG[:gcd(a,p')]` with a ≥ len(FLAG) prints the whole flag in one request.
- Expected acceptance ≈ P(odd)·P(prime 1024-bit)·P(small factor) ≈ 1/2·1/710·0.5 ≈ 1/2800;
  observed 1/1091 (factor-finding on M2 is luckier than the naive estimate — M2's last byte is
  shared with odd M1 but its middle bytes are unconstrained).

## anti-patterns / limits
- One flag submission; worked only from provided source + own code.

## artifacts [OBSERVED]
- code: 13392_provided.py, exploit.py, search.py
- data/logs: flag_primed5.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Provided: `13392_provided.py` (full server source; listener port 13392).
- NOT consulted: solutions pages / writeups / third-party flags.
