# Course lesson — Adrien's Signs (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `adrien`.
**Status:** completed 2026-10-06 · **Points:** 80 · **Site:** https://cryptohack.org/challenges/adrien/
**Ledger row:** `course__adrien_s_signs` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Adrien's Signs

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/modular/adrien/` (course lesson; the
  `/challenges/maths/adrien/` path 404s — these course challenges live only under
  `/courses/modular/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search-engine flag.
  (CryptoHack's policy now *allows* publishing solutions; this run kept the stricter
  self-imposed no-writeup rule.)

## The flag
``flag — recorded in FLAGS/maths/course-adrien/flag.txt``

Verification: submitted to the leaderboard via in-page POST `/submit/adrien/`; the
`#check-adrien` solved-star on `/challenges/maths/` was reloaded and confirmed lit
(`display:block`).

## How it was solved
1. Each plaintext bit is encoded as c = a^e mod p (bit 1) or c = -a^e mod p (bit 0),
   with random e. The value a^e is a quadratic residue mod p (a is a QR, so is any
   power). -a^e is a QNR **iff** -1 is a QNR mod p, i.e. p = 3 mod 4.
2. Check p = 1007621497415251: p = 3 mod 4, and legendre(-1, p) = p-1 (a QNR).
   So the Legendre symbol of c distinguishes the bit directly.
3. For each of the 224 ciphertext values, compute L = pow(c, (p-1)//2, p):
   L == 1 -> bit '1'; L == p-1 -> bit '0'.
4. Group the 224 bits into 28 bytes -> flag.
5. Result: **`flag — recorded in FLAGS/maths/course-adrien/flag.txt`**.

## Learning points
- A bit hidden behind a random exponent can be recovered if the *sign* carries the bit:
  QR vs QNR is a property of the value, not the exponent. The Legendre symbol is the
  decoder.
- The whole trick hinges on p = 3 mod 4 so that -1 is a QNR (otherwise -1 is a QR and
  the sign would carry no info).
- 224 bits = 28 bytes; the flag length 28 matches crypto{...}.

## What I did / did not do
Reconstructed the flag purely from Legendre symbols; no brute force (e is 30-bit random and unknown).

## Limitations
None.

## Configuration
- Date: 2026-10-06 UTC · Host: Windows 11 (bash / MSYS shell) · User: <USER>
- Interpreter: python3 (3.10.11 default); gmpy2, sympy, PyCryptodome available
- Working dir: ~\Practice_runs\cryptohack_org\… (challenge-6X-cryptohack-…)
- Network: cryptohack.org (statements + files), in-page XHR for submission
- No Docker — native, self-managed toolchain (PyCryptodome, gmpy2, pwntools, sympy,
  msieve, curl).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

