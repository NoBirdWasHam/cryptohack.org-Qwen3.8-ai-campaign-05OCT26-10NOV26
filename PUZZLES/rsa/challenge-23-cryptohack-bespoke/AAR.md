# AAR — 105-cryptohack-bespoke: Bespoke Padding (CryptoHack)

**Result:** SOLVED — submitted, API-verified (`score_delta +100`, 9095→9195, 180 solved).
**Date:** 2026-10-20 (UTC)

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/rsa/
- **Challenge:** "Bespoke Padding" (100 pts, 1974 solves, slug `bespoke`)
- **Provided file:** `13386.py` (server source)
- **Service:** socket.cryptohack.org:13386 (JSON line protocol, `{"option":"get_flag"}`)
- **NOT consulted:** `/challenges/bespoke/solutions/`, any writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/rsa/challenge-23-cryptohack-bespoke/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
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

## Learning points
- Franklin-Reiter: e+1 related messages `(a_i m + b_i)` kill textbook RSA with small e;
  this "padding" is exactly the linear form the attack needs.
- The gcd **must** live in (Z/N)[x]; monic long division sidesteps Z/N not being a field.
- "Encrypted flag is different every time" is no defense when the *message* is fixed.

## What I did / did not do
- Worked from statement + provided file only; 3 queries on one connection (2 needed);
  no probing beyond the statement's protocol.
- Submitted via `submit_flag.py`; correctness from API score delta, not the submit body.

## Limitations
- None material. Flag verified by submission (score_delta +100).

## Configuration (environment for this run)
- **Date:** 2026-10-20 ~13:40 UTC
- **Host OS:** Windows 11, shell = git-bash/MSYS · **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe` (stdlib for this solve)
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-105-cryptohack-bespoke`
- **Agent:** Hermes Agent (desktop, model qwen3.8-flash-next-unsloth-ud-q4_k_xl @ qwen3-8-flash);
  submission via `submit_flag.py bespoke <flag>`
- **Network:** socket.cryptohack.org:13386, cryptohack.org HTTPS (login + submit)
- Artifacts: `13386.py` (provided), `solve.py` (Q-gcd bug), `solve2.py` (working)
