# Course lesson — Chinese Remainder Theorem (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `crt1`.
**Status:** completed 2026-10-06 · **Points:** 40 · **Site:** https://cryptohack.org/challenges/crt1/
**Ledger row:** `course__chinese_remainder_theorem` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Chinese Remainder Theorem

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/modular/crt1/` (course lesson; the
  `/challenges/maths/crt1/` path 404s — these course challenges live only under
  `/courses/modular/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search-engine flag.
  (CryptoHack's policy now *allows* publishing solutions; this run kept the stricter
  self-imposed no-writeup rule.)

## The flag
`872`

Verification: submitted to the leaderboard via in-page POST `/submit/crt1/`; the
`#check-crt1` solved-star on `/challenges/maths/` was reloaded and confirmed lit
(`display:block`).

## How it was solved
1. N = 5*11*17 = 935.
2. Standard CRT: x = sum_i a_i * M_i * (M_i^-1 mod n_i) mod N, M_i = N/n_i.
   - i=1: a=2,n=5  -> M=187, inv(187 mod5)=inv(2)=3  -> 2*187*3=1122
   - i=2: a=3,n=11 -> M=85,  inv(85 mod11)=inv(8)=7  -> 3*85*7=1785
   - i=3: a=5,n=17 -> M=55,  inv(55 mod17)=inv(4)=13 -> 5*55*13=3575
3. x = (1122+1785+3575) mod 935 = 6482 mod 935 = **872**.
4. Verify: 872 mod 5 = 2, 872 mod 11 = 3, 872 mod 17 = 5.  CONFIRMED.

## Learning points
- CRT merges coprime congruences into one mod the product — the backbone of RSA
  decryption (compute mod p and mod q, recombine).
- The per-term M_i = N/n_i, multiply by its modular inverse, sum mod N.

## What I did / did not do
Computed the standard CRT sum; verified all three congruences.

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

