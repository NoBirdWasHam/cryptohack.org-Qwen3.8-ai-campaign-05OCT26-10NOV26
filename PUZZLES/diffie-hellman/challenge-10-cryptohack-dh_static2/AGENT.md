---
record: agent-aar
puzzle: challenge-129-cryptohack-dh_static2
category: diffie-hellman
url: https://cryptohack.org/challenges/dh_static2/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/diffie-hellman/challenge-10-cryptohack-dh_static2/flag.txt"
flag_sha256: 4bc962c429176bca3fedca1e698c73988624547231ddbddd6276aff66e79f828
skills: []
human_twin: AAR.md
---

# AGENT — 
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The service reuses the same secret exponent b across connections (static-DH: it hands you a fixed B = 2^b mod P0 and answers with AES under a key derived from A^b) and lets the client submit its **own group parameters**, checking only that p is a 2048-bit prime — no safe-prime rule, no p−1 smoothness policing. So you can hand it p = 2·R·S+1 whose p−1 has a ≈1790-bit factor S built entirely from small primes. Pohlig–Hellman over the S-part then leaks most of b per session; two sessions with independent smooth parts CRT to b exactly, and the flag falls out of the KDF.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
Logged failed/near-miss paths: AES-**CTR** guess for the KDF mode in solve4 (the only thing wrong with that near-miss — actual mode is CBC); early param probes rejected by the strength rule (messages above); bugs en route — kt parity (odd kt made kt·q+1 always even), order factorization missing kt factors plus a `m//=1` infinite loop, bsgs giant-step sign and wrong modulus, PH CRT using xi instead of (xi−x), JSON trailing-data parse.

## artifacts [OBSERVED]
- code: probe.py, probe2.py, probe3.py, probe5.py, probe6.py, solve.py, solve2.py, solve3.py, solve4.py, solve5.py
- data/logs: b_recovered.txt, flag_dh_static2.txt, solve3.log, solve4.log, solve5.log, solve5b.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Live probing of the server's parameter policy (probe*.py, probe*.log archived) and own solve progression solve.py→solve5.py/solve5.log; b_recovered.txt holds the recovered b. Self-derived per logs; no textbook or third-party reference cited in the original AAR; no writeups/solutions consulted.
