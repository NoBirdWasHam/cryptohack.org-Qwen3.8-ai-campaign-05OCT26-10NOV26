---
record: agent-aar
puzzle: challenge-23-cryptohack-bespoke
category: rsa
url: https://cryptohack.org/challenges/bespoke/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/rsa/challenge-23-cryptohack-bespoke/flag.txt"
flag_sha256: 7f2c3fe94d0a0b67d1e2d5c510a72ac5f3f16947cd57a077c2ce133849e54af1
skills: []
human_twin: AAR.md
---

# AGENT — 105-cryptohack-bespoke: Bespoke Padding (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Read `13386.py`: flag `m` encrypted as `c = pow(a*m + b, 11, N)` with **fresh random
   (a,b) per query** but the **same m and same N for the whole TCP session** (e=11).
2. Recognized **Franklin-Reiter related-message attack**: ciphertexts of linear transforms
   of one message share the root `m` **mod N**.
3. First attempt (`solve.py`) gcd'ed the polynomials over Q -> constant. Bug:
   `(a*m+b)^11 - c = k*N != 0` as an integer — `m` is a root only in (Z/N)[x].
4. `solve2.py`: monic-ize `f_i = (a_i x + b_i)^11 - c_i` (divide by `a_i^11`), then
   Euclid in (Z/N)[x] via long division by the **monic** divisor (valid over any ring).
   Degree walked 11->1 in 10 steps; remainder `x + k` => `m = -k mod N`.
5. Two queries suffice; decoded m -> flag; submitted via `submit_flag.py`
   (session cookie had expired mid-run — re-logged via vault, refreshed `.cookies.json`,
   patched csrf extraction for the site's new JS-embedded `_csrf_token`).

## reusable-rules
- Franklin-Reiter: e+1 related messages `(a_i m + b_i)` kill textbook RSA with small e;
  this "padding" is exactly the linear form the attack needs.
- The gcd **must** live in (Z/N)[x]; monic long division sidesteps Z/N not being a field.
- "Encrypted flag is different every time" is no defense when the *message* is fixed.

## anti-patterns / limits
- Worked from statement + provided file only; 3 queries on one connection (2 needed);
  no probing beyond the statement's protocol.
- Submitted via `submit_flag.py`; correctness from API score delta, not the submit body.

## artifacts [OBSERVED]
- code: 13386.py, solve.py, solve2.py
- data/logs: flag_bespoke.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/rsa/
- **Challenge:** "Bespoke Padding" (100 pts, 1974 solves, slug `bespoke`)
- **Provided file:** `13386.py` (server source)
- **Service:** socket.cryptohack.org:13386 (JSON line protocol, `{"option":"get_flag"}`)
- **NOT consulted:** `/challenges/bespoke/solutions/`, any writeups (no-cheat rule)
