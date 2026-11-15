# Course lesson — Working with Fields (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `dh-starter-1`.
**Status:** completed 2026-10-06 · **Points:** 10 · **Site:** https://cryptohack.org/challenges/dh-starter-1/
**Ledger row:** `course__working_with_fields` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Working with Fields

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/dh-starter-1/` (course lesson; the `/challenges/diffie-hellman/dh-starter-1/` path 404s — course challenges live only under `/courses/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search flag.

## The answer
`569`

Verification: submitted via in-page POST `/submit/dh-starter-1/`; confirmed in the user API (`/api/user/NoBirdWasHam/`) which now lists "Working with Fields" under Diffie-Hellman.

## How it was solved
1. Need d with 209·d ≡ 1 (mod 991). 2. d = 209^(-1) mod 991 via extended Euclid / Fermat: pow(209,-1,991). 3. d = **569**. 4. Check 209·569 mod 991 = 1. CONFIRMED.

## Learning points
Modular inverse = the multiplicative counterpart to division in F_p; exists because p is prime (every non-zero element is a unit).

## What I did / did not do
Single pow(x,-1,p) call; verified the product ≡ 1.

## Limitations
None.

## Configuration
- Date 2026-10-06 UTC · Windows 11 · python3 (3.10.11) + PyCryptodome · No Docker (native toolchain).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

