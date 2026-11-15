---
record: agent-aar
puzzle: challenge-124-cryptohack-dh_additive
category: diffie-hellman
url: https://cryptohack.org/challenges/dh_additive/
status: solved
date: 15 Oct 2026
flag_ref: "FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt"
flag_sha256: f57b64180f29db6a820a2fe698c82453141ad107eac377c9c429f495dc663825
skills: []
human_twin: AAR.md
---

# AGENT — dh_additive (70 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Connected to `socket.cryptohack.org:13380` (no input needed). The server prints
   the intercepted DHKE traffic: Alice's `{p, g, A}`, Bob's `{B}`, and Alice's
   `{iv, encrypted}` (AES-128-CBC, per the "Deriving Symmetric Keys" script).
2. The statement's hint: they did DHKE in an **additive** group (Z_p under addition)
   instead of multiplicative. In the additive group the "discrete log" is trivial:
   `A = a·g (mod p)` ⇒ `a = A · g⁻¹ (mod p)` — just multiply by the inverse of g.
3. Computed `a = A * pow(2, -1, p) % p` and `b = B * pow(2, -1, p) % p`.
4. Shared secret of additive DH: `secret = a·B % p` (= `b·A % p` = `a·b·g mod p`;
   asserted both sides equal).
5. Key = `SHA1(str(secret))[:16]`; AES-128-CBC decrypt with the server's `iv`;
   strip PKCS7 → `[flag — recorded in FLAGS/diffie-hellman/challenge-9-cryptohack-dh_additive/flag.txt]`.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Connected once, read the three intercepted lines, computed, decrypted, submitted.
- Did not probe beyond the statement (no input channel exists).

## artifacts [OBSERVED]
- code: solve.py
- data/logs: live_transcript_2026-10-15.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/diffie-hellman/ (category page, slug `dh_additive`)
- Service: `socket.cryptohack.org:13380` (passive; fresh values per connection)
- Decrypt script: "Deriving Symmetric Keys" = `challenge-75-cryptohack-dh-starter-5/decrypt_provided.py` (from the dh-starter-5 course challenge, already in this repo)
- **NOT consulted:** /solutions/, /solves/, any external writeups.
