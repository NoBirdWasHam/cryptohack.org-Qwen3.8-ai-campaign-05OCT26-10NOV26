---
record: agent-aar
puzzle: challenge-9-cryptohack-long_story_short
category: hashes
url: https://cryptohack.org/challenges/long_story_short/
status: solved
date: 2026-10-16
flag_ref: "FLAGS/hashes/challenge-9-cryptohack-long_story_short/flag.txt"
flag_sha256: 56bc579c05bac06f44a5d8a0b8e56afe4dc8e0e6f562541ace0b77e0d90df602
skills: []
human_twin: AAR.md
---

# AGENT — Long Story Short (long_story_short, 60 pts, Hashes)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
PBKDF2-HMAC-SHA256 vault (socket 13434, salt `bluerock-vault-2026`, 200000 iterations). The
passphrase is 128 bytes — LONGER than the SHA-256 HMAC block size (64 bytes). Per RFC 2104,
an HMAC key longer than the block size is first replaced by `H(key)` — here `H = SHA-256`.
So inside every HMAC call the effective key is `SHA-256(passphrase)`, which is EXACTLY the
fingerprint the server publishes. Sending `passphrase_hex = fingerprint` (32 bytes) makes the
server derive the identical PBKDF2 key and the vault opens. The key can also be computed
locally to verify the reasoning before connecting.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Single-shot solve; no failed attempts recorded in run logs.

## artifacts [OBSERVED]
- code: 13434.py, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided server source `13434.py` + live socket 13434. Standard referenced: RFC 2104 (HMAC key-length rule, cited in the original AAR). No writeups/solutions consulted.
