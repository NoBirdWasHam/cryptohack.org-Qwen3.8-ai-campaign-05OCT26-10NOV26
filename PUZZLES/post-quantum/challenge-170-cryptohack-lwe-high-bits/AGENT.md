---
record: agent-aar
puzzle: challenge-170-cryptohack-lwe-high-bits
category: post-quantum
url: https://cryptohack.org/challenges/lwe-high-bits/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-170-cryptohack-lwe-high-bits/flag.txt"
flag_sha256: 14993db977ff54ff86b0c447cbf330d1718c108468ea0f0fe2ec1fbfdb73af2b
skills: []
human_twin: AAR.md
---

# AGENT — lwe-high-bits (CryptoHack Post-Quantum/LWE, 15 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (3 lines)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. The challenge generator `lwe-high-bits.sage` contains `print("S = ", S, "\n")` —
   the **secret key is leaked** in `output.txt` (n=64, p=257, q=65537, Δ=255, eb=127).
2. Compute x = (b − A·S) mod q = (44007 − 58415) mod 65537 → centered **−14408**,
   the exact integer Δ·m + e.
3. Solve m·255 + e = −14408 (mod 65537) with m ∈ [0,257), |e| ≤ 127:
   two candidates — (m=200, e=127) via k=−1 and (m=201, e=−126) via k=+1.
   x/Δ = −56.5019… sits 127 vs 128 from the two adjacent Δ-multiples: a **boundary
   instance** where naive round(x/Δ) decryption returns 200. The true message
   (server-accepted) is **m = 201** (e = −126).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- The run logs record the boundary ambiguity and the two surviving candidates, but do **not** record that candidate 200 was submitted and rejected; the tie between the two in-bounds candidates was broken only by the server.
- No lattice/learning attack was attempted — the S leak made it moot; whether one was considered is not recorded.

## artifacts [OBSERVED]
- code: solve_bit.py, solve_bit2.py
- data/logs: flag_bit.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Provided challenge files: generator `_pq/lwe-high-bits_a83f7bfc0f6e3bfd1b962842feb5d91d.sage` (its `print("S = ", S)` is the leak) and `_pq/lwe-high-bits_output.txt` (S, A, b).
- Course-recommended background: Hoffstein–Pipher–Silverman (LWE encoding/decoding ranges). No third-party writeups consulted.
