# Course lesson — Legendre Symbol (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `root1`.
**Status:** completed 2026-10-06 · **Points:** 35 · **Site:** https://cryptohack.org/challenges/root1/
**Ledger row:** `course__legendre_symbol` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Legendre Symbol

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/modular/root1/` (course lesson; the
  `/challenges/maths/root1/` path 404s — these course challenges live only under
  `/courses/modular/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search-engine flag.
  (CryptoHack's policy now *allows* publishing solutions; this run kept the stricter
  self-imposed no-writeup rule.)

## The flag
`93291799125366706806545638475797430512104976066103610269938025709952247020061090804870186195285998727680200979853848718589126765742550855954805290253592144209552123062161458584575060939481368210688629862036958857604707468372384278049741369153506182660264876115428251983455344219194133033177700490981696141526`

Verification: submitted to the leaderboard via in-page POST `/submit/root1/`; the
`#check-root1` solved-star on `/challenges/maths/` was reloaded and confirmed lit
(`display:block`).

## How it was solved
1. Read p and the 10 integers from output_provided.txt.
2. For each x, compute the Legendre symbol L = pow(x, (p-1)//2, p).
   L==1 -> QR, L==p-1 -> QNR. Exactly one of the 10 is a QR.
3. That QR (index 5) = 85256449…4781771.
4. Since p = 3 mod 4, the square root is r = pow(x, (p+1)//4, p)  (Fermat shortcut).
5. The two roots are r and p-r. Submit the **larger**.
   r = 93291799…41526 (larger); p-r = 82322360…7613.
6. Independent check: pow(larger, 2, p) == the QR.  CONFIRMED.

## Learning points
- The Legendre symbol `a^((p-1)/2) mod p` is an O(log p) test for QR-ness — no search.
- For p = 3 mod 4, `sqrt(x) = x^((p+1)/4) mod p` follows directly from Fermat:
  (x^((p+1)/4))^2 = x^((p+1)/2) = x^(1) (since x^((p-1)/2)=1 for a QR).
- The (±r) pairing means always pick the smaller/larger as the task demands.

## What I did / did not do
Used only the Legendre symbol + the p=3mod4 sqrt formula; verified by squaring.

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
- Note: 'Fermat' in the body names the theorem behind the p≡3 mod 4 sqrt shortcut, not a book/paper source.

