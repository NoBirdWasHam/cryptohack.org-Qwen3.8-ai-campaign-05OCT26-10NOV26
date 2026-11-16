---
record: agent-aar
puzzle: challenge-26-cryptohack-put_a_ring_on_it-ecsc_2023_no
category: ctf-archive
url: https://cryptohack.org/challenges/put_a_ring_on_it-ecsc_2023_no/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-26-cryptohack-put_a_ring_on_it-ecsc_2023_no/flag.txt"
flag_sha256: 5e8441fff0d1ef7a06284e5cdd80751b8d2ac5181a05e21e1dea19ecfb65bf9d
skills: []
human_twin: AAR.md
---

# AGENT — put_a_ring_on_it (ECSC 2023 Norway, CryptoHack ctf-archive)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
1. For each of 16 rings: candidate = indices with both responses < l.
   Result: 15 rings unique; ring 1 had one coincidental fake (expected ≈0.6
   collisions over 256 fakes) → 2 combos.
2. AES key = concat of first byte (hex [0:2]) of candidate pubkeys per ring.
3. CBC-decrypt `enc` with `iv`; the valid combo yields fully-printable plaintext.
   (chal.py does **not** PKCS7-pad; flag is exactly 32 bytes — first solve pass
   assumed padding and found nothing until that was relaxed.)

Key numbers: ring 1 real index = 15 (byte `a2`), the `b3` candidate at index 4
was the coincidental fake.

## reusable-rules
- Ring-size/leak aside, **scalar serialization range** is an anonymity channel:
  reduced vs unreduced mod-l responses perfectly separate real from simulated
  responses in this construction.
- Check the exact serialization/padding assumptions of the generator before
  trusting a plaintext oracle (no PKCS7 here).

## anti-patterns / limits
- None material. Both candidates in ring 1 were exhausted (2 combos); uniqueness
  in the other 15 rings was confirmed by successful decryption of all 16 key
  bytes (single full-ASCII plaintext).

## artifacts [OBSERVED]
- code: ed25519.py, solve.py
- data/logs: data.json, flag_put_a_ring_on_it-ecsc_2023_no.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
not recorded in run logs (pre-discipline solve)
