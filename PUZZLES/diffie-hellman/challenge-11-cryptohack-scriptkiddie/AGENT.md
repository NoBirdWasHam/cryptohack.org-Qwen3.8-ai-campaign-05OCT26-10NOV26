---
record: agent-aar
puzzle: challenge-11-cryptohack-scriptkiddie
category: diffie-hellman
url: https://cryptohack.org/challenges/scriptkiddie/
status: solved
date: 2026-10-15
flag_ref: "FLAGS/diffie-hellman/challenge-11-cryptohack-scriptkiddie/flag.txt"
flag_sha256: 5918eb02590493fd38bfd8babf8d804d6537efddfb4c56b48fb76167a28e59e5
skills: []
human_twin: AAR.md
---

# AGENT — scriptkiddie (70 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Read `script.provided`. The "DH" functions are:
   `generate_public_int(g, a, p): return g ^ a % p` and
   `generate_shared_secret(A, b, p): return A ^ b % p`.
   Python precedence: `%` binds tighter than `^`, so these compute
   **bitwise XOR**: `B = g XOR (b % p)`, `secret = A XOR (b % p)`.
   The author meant modular exponentiation `pow(g, a, p)` — classic script-kiddie bug.
2. Everything needed is in `output.provided` (p, g=2, A, B, iv, ciphertext).
   Invert the XOR: `a = A XOR g`, `b = B XOR g`; shared secret = `A XOR (b % p)`.
   (No discrete log at all — "DH" here was XOR, which is its own inverse.)
3. Reused the script's own key derivation: key = SHA1(str(secret))[:16],
   AES-128-CBC with the given iv, strip PKCS7 → flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Read both provided files, inverted the XOR, decrypted, submitted.
- Did not run the provided script interactively (not needed; all inputs known).

## artifacts [OBSERVED]
- code: solve.py
- data/logs: live_transcript_2026-10-15.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `scriptkiddie`)
- Files: `script.provided`, `output.provided` (URLs in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups.
