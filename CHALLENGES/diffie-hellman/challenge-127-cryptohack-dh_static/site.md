# CryptoHack — dh_static (100 pts)

- **Platform:** CryptoHack (cryptohack.org), category: Diffie-Hellman
- **Challenge name:** dh_static
- **Slug:** `dh_static`
- **Points:** 100
- **Folder:** challenge-127-cryptohack-dh_static
- **Account:** NoBirdWasHam
- **Status:** SOLVED 2026-10-15 (flag submitted, score_delta +100)

## Verbatim statement

> You've just finished eavesdropping on a conversation between Alice and Bob. Now you have a chance to talk to Bob. What are you going to say? Connect at socket.cryptohack.org 13373

## Service

- `socket.cryptohack.org` port **13373** (fresh session per connection)
- Phase 1 (passive, printed on connect):
  - `Intercepted from Alice: {"p": "0x<1536-bit safe prime>", "g": "0x02", "A": "0x..."}`
  - `Intercepted from Bob: {"B": "0x8d79b693...94ebfa8ef0"}` — **globally static**,
    identical across all connections (verified over 6+ connections)
  - `Intercepted from Alice: {"iv": "...", "encrypted": "..."}` — the flag,
    key = SHA1(str(A^b))[:16], AES-128-CBC
- Phase 2: `Bob connects to you, send him some parameters:`
  - I send one JSON line `{"p": ..., "g": ..., "A": ...}` (hex strings)
  - Bob replies `Bob says to you: {"B": "<g^b mod p>"}` then
    `Bob says to you: {"iv": ..., "encrypted": ...}` (fixed 66-char message
    "Hey, what's up. I got bored generating random numbers did you see?",
    under key SHA1(str(A^b mod p))[:16]). No further conversation.
- No provided files.

## Group facts (computed)

- P = 0xffffffff...7327ffffffffffffffff — **1536-bit SAFE prime**: P−1 = 2q,
  q = (P−1)/2 is a 1535-bit prime (sympy isprime). So <2> has prime order q;
  B = 2^b mod P is otherwise an infeasible DLP.
- P ≡ 7 (mod 8) → (2|P) = 1.
