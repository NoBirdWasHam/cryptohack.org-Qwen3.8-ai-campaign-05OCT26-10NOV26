# Course lesson — Deriving Symmetric Keys (Diffie-Hellman)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Diffie-Hellman as challenge `dh-starter-5`.
**Status:** completed 2026-10-06 · **Points:** 40 · **Site:** https://cryptohack.org/challenges/dh-starter-5/
**Ledger row:** `course__deriving_symmetric_keys` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Deriving Symmetric Keys

**Result:** SOLVED
**Date:** 2026-10-06 (UTC)

## Source
- Statement: `https://cryptohack.org/courses/public-key/dh-starter-5/` (course lesson; the `/challenges/diffie-hellman/dh-starter-5/` path 404s — course challenges live only under `/courses/`).
- Provided files: see `site.md`.
- **NOT consulted:** the `/solutions/` page, any writeup, any search flag.

## The answer
``flag — recorded in FLAGS/diffie-hellman/challenge-5-cryptohack-dh-starter-5/flag.txt``

Verification: submitted via in-page POST `/submit/dh-starter-5/`; confirmed in the user API (`/api/user/NoBirdWasHam/`) which now lists "Deriving Symmetric Keys" under Diffie-Hellman.

## How it was solved
1. shared_secret = A^b mod p = 1547922466740669851136899009270554812141325611574971428561894811681012510829813498961168330963719034921137405736161582760628870855358912091728546731744381382987669929718448423076919613463237884695314172139247244360699127770351428964026451292014069829877638774839374984158095336977179683450837507011404610904412301992397725594661037513152497857482717626617522302677408930050472100106931529654955968569601928777990379536458959945351084885704041496571582522945310187  (b from the statement). 2. Key derivation per source.py: key = SHA1(str(shared_secret).encode())[:16]. 3. AES-CBC with the given IV, PKCS7-unpad. 4. Plaintext = **`flag — recorded in FLAGS/diffie-hellman/challenge-5-cryptohack-dh-starter-5/flag.txt`**.

## Learning points
DH's output is a shared *secret integer*; to use it for bulk encryption you hash it to a symmetric key (here SHA1→16 bytes → AES-128-CBC). The flag decrypts with valid PKCS7 padding, which independently confirms the secret was right.

## What I did / did not do
Computed the secret, derived the AES key exactly as source.py does, decrypted + unpad; valid padding confirms correctness.

## Limitations
None.

## Configuration
- Date 2026-10-06 UTC · Windows 11 · python3 (3.10.11) + PyCryptodome · No Docker (native toolchain).

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

