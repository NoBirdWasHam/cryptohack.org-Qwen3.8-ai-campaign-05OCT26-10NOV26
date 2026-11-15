# Course lesson — Computing Public Values (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `dh-starter-3`.
**Status:** completed 2026-10-06 · **Points:** 25 · **Site:** https://cryptohack.org/challenges/dh-starter-3/
**Ledger row:** `course__computing_public_values` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Computing Public Values

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/dh-starter-3/` (course lesson; the `/challenges/diffie-hellman/dh-starter-3/` path 404s — course challenges live only under `/courses/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search flag.

## The answer
`1806857697840726523322586721820911358489420128129248078673933653533930681676181753849411715714173604352323556558783759252661061186320274214883104886050164368129191719707402291577330485499513522368289395359523901406138025022522412429238971591272160519144672389532393673832265070057319485399793101182682177465364396277424717543434017666343807276970864475830391776403957550678362368319776566025118492062196941451265638054400177248572271342548616103967411990437357924`

Verification: submitted via in-page POST `/submit/dh-starter-3/`; confirmed in the user API (`/api/user/NoBirdWasHam/`) which now lists "Computing Public Values" under Diffie-Hellman.

## How it was solved
1. A = g^a mod p = 2^a mod p with the 2048-bit NIST prime. 2. Single modular exponentiation pow(2, a, p). 3. A = 1806857697840726523322586721820911358489420128129248078673933653533930681676181753849411715714173604352323556558783759252661061186320274214883104886050164368129191719707402291577330485499513522368289395359523901406138025022522412429238971591272160519144672389532393673832265070057319485399793101182682177465364396277424717543434017666343807276970864475830391776403957550678362368319776566025118492062196941451265638054400177248572271342548616103967411990437357924

## Learning points
Public DH values are just repeated squaring (O(log a) multiplications) — the discrete log in the other direction is the hard direction.

## What I did / did not do
One pow(2,a,p); result is the public value A.

## Limitations
None.

## Configuration
- Date 2026-10-06 UTC · Windows 11 · python3 (3.10.11) + PyCryptodome · No Docker (native toolchain).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

