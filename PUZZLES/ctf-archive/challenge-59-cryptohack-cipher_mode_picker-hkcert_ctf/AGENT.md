---
record: agent-aar
puzzle: challenge-254-cryptohack-cipher_mode_picker-hkcert_ctf
category: ctf-archive
url: https://cryptohack.org/challenges/cipher_mode_picker-hkcert_ctf/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/ctf-archive/challenge-59-cryptohack-cipher_mode_picker-hkcert_ctf/flag.txt"
flag_sha256: 69514b8543e14c65730b4e99c869e9acbb739afcbaf1b25be1f9b204a46700f8
skills: []
human_twin: AAR.md
---

# AGENT — cipher_mode_picker-hkcert_ctf (archive.cryptohack.org:2951)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (2 queries)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `cfb data 00*80` → returns OFB keystream KS (5 blocks).
2. `ofb flag` → `ct = flag ⊕ KS`.
3. `flag = ct ⊕ KS`.

## reusable-rules
- Same key+IV across modes ⇒ any mode that exposes `E(iv)`-chain output under chosen plaintext breaks OFB. Zero-fill is the trick that makes CFB's ciphertext-feedback equal OFB's.
- ECB/CBC/CTR unused; CTR (`Counter.new(16, prefix=iv[:14])`) would also have leaked keystream but only for its own counter blocks, not the OFB chain.
- Protocol nit: `input('> ')` prompt has no newline, so it glues to the next hex line — parse last whitespace token.

## anti-patterns / limits
None — solved first try. (Prior solver's head start: card extraction + listener/port; chall.py re-fetched fresh.)

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_cipher_mode_picker-hkcert_ctf.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
not recorded in run logs (pre-discipline solve)
