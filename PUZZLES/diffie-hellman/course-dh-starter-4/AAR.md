# Course lesson — Computing Shared Secrets (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `dh-starter-4`.
**Status:** completed 2026-10-06 · **Points:** 30 · **Site:** https://cryptohack.org/challenges/dh-starter-4/
**Ledger row:** `course__computing_shared_secrets` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Computing Shared Secrets

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/dh-starter-4/` (course lesson; the `/challenges/diffie-hellman/dh-starter-4/` path 404s — course challenges live only under `/courses/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search flag.

## The answer
`1174130740413820656533832746034841985877302086316388380165984436672307692443711310285014138545204369495478725102882673427892104539120952393788961051992901649694063179853598311473820341215879965343136351436410522850717408445802043003164658348006577408558693502220285700893404674592567626297571222027902631157072143330043118418467094237965591198440803970726604537807146703763571606861448354607502654664700390453794493176794678917352634029713320615865940720837909466`

Verification: submitted via in-page POST `/submit/dh-starter-4/`; confirmed in the user API (`/api/user/NoBirdWasHam/`) which now lists "Computing Shared Secrets" under Diffie-Hellman.

## How it was solved
1. Recompute B = g^b mod p from b → matches Alice's stated B (sanity check passed). 2. Shared secret = A^b mod p (or B^a mod p). 3. pow(A, b, p) = 1174130740413820656533832746034841985877302086316388380165984436672307692443711310285014138545204369495478725102882673427892104539120952393788961051992901649694063179853598311473820341215879965343136351436410522850717408445802043003164658348006577408558693502220285700893404674592567626297571222027902631157072143330043118418467094237965591198440803970726604537807146703763571606861448354607502654664700390453794493176794678917352634029713320615865940720837909466

## Learning points
The shared secret is A^b = (g^a)^b = g^(ab) = (g^b)^a = B^a — the commutativity of the group is exactly why both sides agree without revealing a or b.

## What I did / did not do
Verified B from b (matches), then computed A^b mod p.

## Limitations
None.

## Configuration
- Date 2026-10-06 UTC · Windows 11 · python3 (3.10.11) + PyCryptodome · No Docker (native toolchain).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

