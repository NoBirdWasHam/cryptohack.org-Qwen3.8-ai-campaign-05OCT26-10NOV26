# Course lesson — Export-grade (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `export_grade`.
**Status:** completed 2026-10-06 · **Points:** 100 · **Site:** https://cryptohack.org/challenges/export_grade/
**Ledger row:** `course__export_grade` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Export-grade

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/export_grade/`
- Live protocol at `socket.cryptohack.org:13379` (see `site.md`); solver `solve.py`.
- **NOT consulted:** `/solutions/`, any writeup, any search flag.

## The flag
``flag — recorded in FLAGS/diffie-hellman/challenge-7-cryptohack-export_grade/flag.txt``

Verification: submitted via in-page POST; the user API now lists "Export-grade" under Diffie-Hellman (7/7 DH solved). The DLOG was verified: `g^a ≡ A (mod p)` before deriving the key.

## How it was solved
1. **Force the weakest parameters.** The MITM controls the negotiation: reply with `supported: ["DH64"]`, and Bob agrees (`chosen: DH64`). Alice and Bob then do DH with a **64-bit prime** `p = 0xde26ab651b92a129`, `g = 2`.
2. **Passive phase:** capture `A = g^a`, `B = g^b`, and the AES-CBC `iv`+`encrypted_flag`.
3. **Recover a (64-bit DLOG).** `p-1 = 2³·3·293·5417·420233272499`. Crucially, `g = 2` is *not* a full generator: its order is `r = 2²·3·293·5417·420233272499` (63 bits). Verified `A, B ∈ <g>` (`A^r ≡ 1`), then solved the DLOG in that subgroup with **Pohlig–Hellman**: for each prime `q | r`, solve `g^(r/q)^x ≡ A^(r/q) (mod p)` for `x mod q` — the largest sub-group (420233272499, ~39 bits) via **BSGS** (~65k table), the rest trivially — then **CRT** to recombine.
4. Because `r` has a `2²` factor and the CRT over the distinct primes only fixes `a mod (r/2)`, test `a` and `a + r/2` and keep the one with `g^a ≡ A`. (First attempt skipped this and silently produced a wrong key.)
5. `a = 3458824760982333828` (62 bits). Shared secret `= B^a mod p`.
6. **Key derivation** same as #75: `key = SHA1(str(secret))[:16]` → AES-128-CBC → ``flag — recorded in FLAGS/diffie-hellman/challenge-7-cryptohack-export_grade/flag.txt`` (clean PKCS7 this time).

## Learning points
- "Export-grade" crypto = deliberately weakened crypto negotiated by legacy/interoperability code. If you can sit in the middle of the negotiation, you can pin the *weakest* common parameter — the attack is on the protocol, not the math alone. (Historical echo: the 1990s US export-crypto downgrades.)
- Pohlig–Hellman reduces DLOG to the size of the **largest prime factor of the group order**; here that factor was only 39 bits, so BSGS was ~2^20 — seconds. (The 1024/2048-bit safe-prime groups elsewhere are safe-prime *precisely* so p-1's factors are huge.)
- Always compute the *actual order of g*, not p-1, before setting up Pohlig–Hellman — g was not a generator and the first (naive, full p-1) attempt failed verification.

## What I did / did not do
- Full attack in `solve.py`: force DH64 → capture → PH+BSGS+CRT DLOG → verify → decrypt. Did not try the larger negotiated parameters (unnecessary once DH64 is pinned).

## Limitations
None — flag recovered and API-verified.

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

