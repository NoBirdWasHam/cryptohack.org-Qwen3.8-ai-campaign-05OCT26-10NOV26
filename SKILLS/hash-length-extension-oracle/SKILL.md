---
name: hash-length-extension-oracle
description: Use when a hash oracle leaks MD state. Length-extension.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, sha256, length-extension, merkle-damgard]
---

# MD length-extension / intermediate-state theft via hash oracles

> **PROVENANCE WARNING:** the concrete recipe (sign_in_please_again / HKCERT-CTF-2021 pbox
> stretching) was retrieved from the challenge author's postmortem
> (mystiz.hk/posts/2021-11-18-hkcert-ctf-2/) under an owner-approved brief; ledger entry
> challenge-319 is TAINTED. Treat this skill as a reminder the family EXISTS; prefer
> re-deriving it yourself before replaying the recipe.

## When to Use
A service hashes attacker-influenced structures with MD-family hashes (SHA-256) and returns
digests of short (<=55 B) messages, or of permutations/mappings with set-only coverage guards.

## Core primitive
Hand-roll the SHA-256 compression function `compress(state8ints, 64B block) -> state` (validate
against hashlib incl. a length-extension self-test — working implementation:
cryptohack_org/challenge-319.../sha256ext.py).
Any digest of a <=55-byte message IS the intermediate state after its single padded block:
known-plaintext structure lets you TREAT PAST DIGESTS AS STATES and continue them:
`digest_of(msg || pad(L) || cont) = chain(past_digest, padless continuation blocks)`.

## Oracle-stretching pattern (set-guard != length-guard)
If a server accepts a permutation/mapping requiring only SET coverage of payload indices
(guard like `set(pbox)==set(range(n))`) but not list LENGTH, duplicates let you stretch the
hashed payload to ANY length and plant MD padding bytes (0x80, length field) at chosen offsets
via your own known bytes (e.g. salt values). Design stretched messages so their block1 equals
the PADDED form of a shorter payload variant:
- 21B `P|salt|r` padded = `P(16) s(4) r 80 00*34 00*7 A8` — equals a 64-byte stretched message
  with salt bytes chosen 00/00/80/A8 at the right duplicated positions.
- Then a fresh call's block1 state == an old call's digest iff the substituted byte (pepper)
  matches: testing 16 candidates vs 16 saved digests recovers an unknown byte with
  P = 1-(1-16/256)^16 ~ 64% (reconnect on miss).
- With state + its unknown-byte value known, continue the chain to forge/predict digests, and
  recover message bytes one oracle call per byte by brute-forcing the continuation block.

## Cost traps
- Surjectivity often forces one FRESH unknown byte (fresh random pepper) into your forged
  continuation block: brute-force it too (x256) — do NOT assume it equals the recovered value
  (the author's own writeup glosses this over; it broke the first implementation).
- Pure-python compress ~155us; 262k candidates = ~41s serial. `multiprocessing.Pool(16)`
  (module-level picklable worker; Windows spawn-safe) cuts it to ~3s — essential under a
  server-side 60s alarm. Measure compress cost BEFORE trusting a serial time budget.
- Local clone first (drive chall.py via subprocess pipes; on Windows stub `signal.alarm`;
  read pipes with os.read(fd,4096) — blocking file .read(n) waits for n bytes; emoji+payload
  can arrive in separate writes — anchor markers BEFORE the payload).
