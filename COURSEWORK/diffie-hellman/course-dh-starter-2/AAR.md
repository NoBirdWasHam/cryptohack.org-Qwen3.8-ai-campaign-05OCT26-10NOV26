# Course lesson — Generators of Groups (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `dh-starter-2`.
**Status:** completed 2026-10-06 · **Points:** 20 · **Site:** https://cryptohack.org/challenges/dh-starter-2/
**Ledger row:** `course__generators_of_groups` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Generators of Groups

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/dh-starter-2/` (course lesson; the `/challenges/diffie-hellman/dh-starter-2/` path 404s — course challenges live only under `/courses/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search flag.

## The answer
`7`

Verification: submitted via in-page POST `/submit/dh-starter-2/`; confirmed in the user API (`/api/user/NoBirdWasHam/`) which now lists "Generators of Groups" under Diffie-Hellman.

## How it was solved
1. A g is primitive iff its order is p-1 = 28150. 2. Factor 28150 = 2·5²·563; distinct prime factors {2,5,563}. 3. g is NOT primitive iff g^((p-1)/q) ≡ 1 for some q in {2,5,563}. 4. Test g = 2,3,4,5,6: each fails at some q. 5. g = **7** passes all three → primitive. 6. 7 is the smallest.

## Learning points
Order-test for a generator: it suffices to check g^((p-1)/q) ≠ 1 for every prime q | (p-1) — far cheaper than enumerating the whole subgroup (brute-force would be 28150 elements, this is 3·log pow per candidate).

## What I did / did not do
Factored φ and ran the order test; verified 7 generates.

## Limitations
None.

## Configuration
- Date 2026-10-06 UTC · Windows 11 · python3 (3.10.11) + PyCryptodome · No Docker (native toolchain).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

