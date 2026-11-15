---
record: agent-aar
puzzle: challenge-172-cryptohack-lwe-low-bits
category: post-quantum
url: https://cryptohack.org/challenges/lwe-low-bits/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-11-cryptohack-lwe-low-bits/flag.txt"
flag_sha256: 5c862790153d23a72dd410bb8b36819d51ac248cbaec4f6742efd8e75f20b175
skills: []
human_twin: AAR.md
---

# AGENT — lwe-low-bits (CryptoHack Post-Quantum/LWE, 20 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (3 lines)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Same leak as high-bits: the generator prints **S** in `output.txt`
   (n=64, p=257, q=65537, eb=127).
2. x = (b − A·S) mod q, centered → **−881** = m + 257·e, |e| ≤ 127.
3. e = (−881 − 147)/257 = −4 is the unique in-bounds solution → **m = 147**.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Nothing failed; direct computation, recorded in one pass. The S leak removed the learning task — no lattice or sample-combination attack was attempted (nor needed).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Provided challenge files: `_pq/lwe-low-bits_a2c45284086e181a601486fe22f873ff.sage` (generator, prints S) and `_pq/lwe-low-bits_output.txt` (S, A, b).
- Course-recommended background: Hoffstein–Pipher–Silverman. No third-party writeups consulted.
