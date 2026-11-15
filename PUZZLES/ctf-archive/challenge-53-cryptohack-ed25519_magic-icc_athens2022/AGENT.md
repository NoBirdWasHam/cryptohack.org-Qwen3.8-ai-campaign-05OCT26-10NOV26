---
record: agent-aar
puzzle: challenge-312-cryptohack-ed25519_magic-icc_athens2022
category: ctf-archive
url: https://cryptohack.org/challenges/ed25519_magic-icc_athens2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-53-cryptohack-ed25519_magic-icc_athens2022/flag.txt"
flag_sha256: 123694166e855405169d977d3f187afb99f4ff5a6cfbfbbe04ec8cd4cd3b7f39
skills: []
human_twin: AAR.md
---

# AGENT — ed25519_magic (ICC Athens), CryptoHack archive #312
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
- **Level 1** (re-sign `b"CryptoHack"` with a different signature): send
  `R ‖ LE32(s + L)`. Different 64 bytes (passes `new_sig == sig` guard), same scalar
  after barrett reduction → identical check point → verifies.
- **Level 2** (supply vk + sig for an unseen random 16-byte msg): vk = identity point
  `01‖0*31`, sig = `01‖0*31 ‖ 0*32` (R = identity, s = 0). Then
  `0·B + h·(−O) = O` and `pack(O) = 01‖0*31 = R` for **any** message. Deterministic.

## reusable-rules
- Pre-RFC reference implementations lack the canonical-form checks RFC 8032 §8.4
  mandates (S < L, and the cofactored equation). "Magic as originally conceived" =
  exactly these malleabilities.
- When a verifier reduces the scalar itself, `s + kL` is a free signature mutation.
- Identity public key + zero signature is a universal accept against verifiers that
  don't reject the small subgroup / identity — works even with unknown message.

## anti-patterns / limits
- Did not build the C extension locally (py3.12-era sdist on this host); validated
  against a hand-written emulator of the C code instead — the live server was the
  real ground truth.
- Small-order-A variant (order-8 torsion, 1/8 message-dependent) was considered and
  rejected as non-deterministic; identity-key is deterministic.
- First live attempt died on a client-side protocol-read bug (consumed the b64 line
  before the prompt); fixed, second attempt solved. No server-side failures.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_ed25519_magic.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
chal.py + the shipped ed25519-1.5 source tree (src/ed25519-supercop-ref/ed25519.c: crypto_sign_open, sc25519_from32bytes, ge25519_unpackneg_vartime) + the live listener (archive.cryptohack.org:31144). RFC 8032 §8.4 used as the reference standard naming the missing checks (a standard, not a solution writeup). Flag came from the live service after our own forgeries; no third-party writeups consulted.
