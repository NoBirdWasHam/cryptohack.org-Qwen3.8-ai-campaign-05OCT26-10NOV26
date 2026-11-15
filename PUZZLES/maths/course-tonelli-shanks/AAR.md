# Course lesson — Modular Square Root (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `tonelli-shanks`.
**Status:** completed 2026-10-06 · **Points:** 35 · **Site:** https://cryptohack.org/challenges/tonelli-shanks/
**Ledger row:** `course__modular_square_root` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Modular Square Root

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/modular/tonelli-shanks/` (course lesson; the
  `/challenges/maths/tonelli-shanks/` path 404s — these course challenges live only under
  `/courses/modular/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search-engine flag.
  (CryptoHack's policy now *allows* publishing solutions; this run kept the stricter
  self-imposed no-writeup rule.)

## The flag
`2362339307683048638327773298580489298932137505520500388338271052053734747862351779647314176817953359071871560041125289919247146074907151612762640868199621186559522068338032600991311882224016021222672243139362180461232646732465848840425458257930887856583379600967761738596782877851318489355679822813155123045705285112099448146426755110160002515592418850432103641815811071548456284263507805589445073657565381850521367969675699760755310784623577076440037747681760302434924932113640061738777601194622244192758024180853916244427254065441962557282572849162772740798989647948645207349737457445440405057156897508368531939120`

Verification: submitted to the leaderboard via in-page POST `/submit/tonelli-shanks/`; the
`#check-tonelli-shanks` solved-star on `/challenges/maths/` was reloaded and confirmed lit
(`display:block`).

## How it was solved
1. Read a, p from output_provided.txt. p = 1 mod 4 (the hard case), legendre(a/p)=1.
2. Implement Tonelli-Shanks by hand (stdlib + gmpy2, no Sage):
   - factor p-1 = q * 2^s with q odd;
   - find a quadratic non-residue z (legendre(z/p) = p-1);
   - init m=s, c=z^q, t=a^q, r=a^((q+1)/2);
   - loop while t != 1: find smallest i with t^(2^i)=1, set
     b=c^(2^(m-i-1)); m=i; c=b^2; t=t*c; r=r*b.
3. r = 23623393…39120 (one root); the other is p-r.
4. Submit the **smaller**.
5. Independent check: pow(r, 2, p) == a.  CONFIRMED.

## Learning points
- Tonelli-Shanks is the general prime-modulus sqrt; the p=3mod4 formula is just the
  special case. The algorithm is a descent on the 2-adic part of p-1.
- Root-finding mod composites = factoring (why this is crypto-relevant).
- I implemented it from scratch rather than calling Sage — the point of the exercise.

## What I did / did not do
Hand-rolled Tonelli-Shanks; verified by squaring.

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
- Note: the algorithm name 'Tonelli–Shanks' comes from the challenge/course slug itself (`/courses/modular/tonelli-shanks/`); it was implemented by hand, no textbook/paper cited.

