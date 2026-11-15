---
record: agent-aar
puzzle: challenge-173-cryptohack-lwe-private-public
category: post-quantum
url: https://cryptohack.org/challenges/lwe-private-public/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/post-quantum/challenge-12-cryptohack-lwe-private-public/flag.txt"
flag_sha256: 0887b81c877be1db0e3cd0002a0acea3ea1eb122e443bf2cac6208c24af0ceec
skills: []
human_twin: AAR.md
---

# AGENT — lwe-private-public (CryptoHack Post-Quantum/LWE, 25 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Pure knowledge question: **Kyber1024 (ML-KEM-1024) public key = 1568 bytes**
(per the NIST FIPS 203 parameter table: ML-KEM-512 pk=800 B, ML-KEM-768 pk=1184 B,
ML-KEM-1024 pk=1568 B; secret keys 3932/3888/6368… precisely: sk 1632/2560/3968 B
for 512/768/1024). The LWE public-key discussion in the statement (O(n² log q)
scaling) is the setup; the answer is the standard's parameter.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Pure retrieval — no derivation exists to record; nothing failed. The specific document copy consulted at solve time is not named in the run logs (only the cross-check outcome is recorded).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- FIPS 203 (ML-KEM) / Kyber published parameter table — a standard, not a writeup.
- Course statement page https://cryptohack.org/challenges/post-quantum/lwe-private-public/ (cached). No solution artifacts consulted.
