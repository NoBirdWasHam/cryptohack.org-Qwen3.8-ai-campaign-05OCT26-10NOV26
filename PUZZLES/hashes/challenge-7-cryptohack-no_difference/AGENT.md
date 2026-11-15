---
record: agent-aar
puzzle: challenge-148-cryptohack-no_difference
category: hashes
url: https://cryptohack.org/challenges/no_difference/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/hashes/challenge-7-cryptohack-no_difference/flag.txt"
flag_sha256: 5d7e4b10159d5cc47d6135c239b22cd18524bbf097f895ba2b3c99d64f45f3d4
skills: []
human_twin: AAR.md
---

# AGENT — <!-- AAR -->
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
The hash's SBOX is NOT injective (rows satisfy S[x]=S[x^0x0F] plus cross-row duplicates).
permute = bit-transpose (involution): bit i of t_j = bit j of x_i. Message byte k XORs
state byte 4+k, so in permuted coords the HIGH nibble of every t_j is fully controllable
while the LOW nibble is fixed by INIT. Found a colliding SBOX pair (0x50,0x80) sharing the
fixed low nibble at position j=0, built two one-block messages whose post-substitute states
coincide -> identical hashes. Server returned the flag. See solve2.py.

## reusable-rules
- A hash SBOX that is a non-injective map gives trivial collisions: match the FIXED bits of
  the pre-substitute state and swap only the controllable bits through a colliding pair.
- Listener protocol gotcha: this listener sends only the before_input quote (no JSON prompt
  line) — send the dict immediately after the first line.

## anti-patterns / limits
- Flag captured directly from the live listener; site auto-marks solved on listener capture.

## artifacts [OBSERVED]
- code: solve.py, solve2.py
- data/logs: flag_no_difference.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "No Difference" (175 pts, slug `no-difference`)
- **Interactive service:** socket.cryptohack.org 13395
- **NOT consulted:** solutions pages, search-engine writeups (no-cheat rule)
