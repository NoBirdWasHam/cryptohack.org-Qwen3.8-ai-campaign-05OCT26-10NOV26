# Course lesson — Parameter Injection (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `parameter_injection`.
**Status:** completed 2026-10-06 · **Points:** 60 · **Site:** https://cryptohack.org/challenges/parameter_injection/
**Ledger row:** `course__parameter_injection` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Parameter Injection

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/parameter_injection/`
- Live protocol at `socket.cryptohack.org:13371` (probed + exploited; see `site.md`).
- **NOT consulted:** `/solutions/`, any writeup, any search flag.

## The flag
``flag — recorded in COURSEWORK/diffie-hellman/course-parameter_injection/flag.txt``

Verification: submitted via in-page POST; the user API now lists "Parameter Injection" under Diffie-Hellman (7/7 DH solved).

## How it was solved
1. **The vulnerability:** we are a man-in-the-middle and may *rewrite* either party's DH public value. DH only works because both sides raise the *other's* value to their own secret: Bob computes `A^b`, Alice computes `B^a`.
2. **Inject the group identity.** Send Bob `A' = 1` (so Bob computes `1^b = 1`), and send Alice `B' = 1` (so Alice computes `1^a = 1`). Both parties now believe the shared secret is `1` — a value I know without any discrete log.
3. The server (playing Bob, then relaying for Alice) returns `iv` + `encrypted_flag`.
4. **Key derivation** (from `source_provided.py` in #75): `key = SHA1(str(shared_secret))[:16]` → AES-128-CBC.
5. `SHA1("1")[:16]` decrypts the ciphertext → ``flag — recorded in COURSEWORK/diffie-hellman/course-parameter_injection/flag.txt`` (32 bytes, block-aligned, so "invalid padding" is expected and correct).

## Learning points
- DH without authentication / without validating the peer's public value is trivially broken by a MITM: injecting `g^0 = 1` (or `0`, or any value of small known order) forces a known shared secret.
- Production DH mandates validating that the peer's value has large prime order in a safe-prime group — exactly why the NIST/OWASP guides exist. This challenge is the 1024-bit weak-prime cousin of that rule.
- The flag's `!!!!!!!!` and the "n1c3_0n3_m4ll0ry" text are a wink: the padding check fails on purpose.

## What I did / did not do
- Probed the wire protocol first (JSON, hex strings, one direction at a time), then ran the two-injection MITM in one connection (`solve.py`). Did not attempt the real (secure) path — no DLOG on the 1024-bit prime.

## Limitations
None — flag recovered and API-verified.

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.
- Note: 'NIST/OWASP guides' in the body is an analogy in the learning-points, not a consulted source.

