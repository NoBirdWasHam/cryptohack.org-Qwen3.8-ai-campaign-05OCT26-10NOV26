# Course lesson — Quadratic Residues (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `root0`.
**Status:** completed 2026-10-06 · **Points:** 25 · **Site:** https://cryptohack.org/challenges/root0/
**Ledger row:** `course__quadratic_residues` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Quadratic Residues

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/modular/root0/` (course lesson; the
  `/challenges/maths/root0/` path 404s — these course challenges live only under
  `/courses/modular/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search-engine flag.
  (CryptoHack's policy now *allows* publishing solutions; this run kept the stricter
  self-imposed no-writeup rule.)

## The flag
`8`

Verification: submitted to the leaderboard via in-page POST `/submit/root0/`; the
`#check-root0` solved-star on `/challenges/maths/` was reloaded and confirmed lit
(`display:block`).

## How it was solved
1. Brute-force `a in 1..p-1` for each candidate x and test `a*a % p == x`.
2. Results: 14 -> no root (QNR); **6 -> roots {8, 21} (QR)**; 11 -> no root (QNR).
3. The two roots of 6 are 8 and 21 (21 = -8 mod 29, confirming the (±a) pairing).
4. Submit the smaller: **8**.

## Learning points
- Half of F_p* are quadratic residues; the rest are not. Brute-force is fine for
  tiny p (29) but is "wildly unreasonable" for large p (next challenge).
- QRs always come in ±a pairs; pick the smaller (or larger, per the task).

## What I did / did not do
Computed all three candidates by direct squaring; verified 6 is the only QR and 8 < 21.

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

