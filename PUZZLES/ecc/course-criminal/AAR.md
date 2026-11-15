# Course lesson — Smooth Criminal (Elliptic Curves)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Elliptic Curves as challenge `criminal`.
**Status:** completed 2026-10-07 · **Points:** 60 · **Site:** https://cryptohack.org/challenges/criminal/
**Ledger row:** `course__smooth_criminal` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Smooth Criminal

**Result:** SOLVED — ``flag — recorded in FLAGS/ecc/course-criminal/flag.txt``
**API-verified:** user API `/api/user/NoBirdWasHam/` → `solved_challenges` went 73 → 74,
`criminal` present; account leveled **10 → 11** (rank 1241, score 3010, +560 pts).
Page shows "You have solved this challenge!" Solve count 3070 → 3071.
**Date:** 2026-10-07 (UTC-04:00)

## Configuration
- OS: Windows 11 (bash/git-bash terminal), Python 3.10.11 (PyCryptodome, gmpy2, sympy)
- **PARI/GP 2.17.4** (`gp64.exe`, 13 MB standalone binary, downloaded from
  https://pari.math.u-bordeaux.fr/pub/pari/windows/ to `~\tools\gp64.exe`).
  Self-managed, no Docker — per the standing tooling directive.
- CryptoHack account `NoBirdWasHam` (browser login via vault).

## The problem
ECIES-style flow on a 128-bit prime curve `E: y² = x³ + 2x + 3 (mod p)`:
- Alice: secret `n = randint(1, p)`, public key `Q = [n]G`.
- Shared secret = x-coordinate of `[n]B` (Bob's public key `B`).
- AES-128-CBC flag, key = `SHA1(str(shared_secret))[:16]`.

`Q` and `B` are given in `output.txt`. To get the shared secret I must recover `n`,
i.e. solve the **elliptic-curve discrete log** `Q = [n]G`.

## The catch that makes it solvable
The group order is **smooth**:

```
#E(F_p) = 310717010502520989590206149059164677804
        = 2² · 3⁷ · 139 · 165229 · 31850531 · 270778799 · 179317983307
```

Largest prime factor is only **27 bits** (`179317983307`). So a naive BSGS over the
whole group is infeasible (2⁶⁴), but **Pohlig–Hellman** reduces the DLP to one DLP in
each prime-power subgroup — the hardest is a 27-bit BSGS (~4.5×10⁴ steps). Hence the
name "Smooth Criminal": the group order is smooth on purpose.

## How I actually solved it
1. **Group order + factorization — PARI/GP** (the hard part, a legitimate tool use):
   ```gp
   default(parisizemax,0); default(parisize, 2^30);
   E = ellinit([0,0,0,2,3], 310717010502520989590157367261876774703);
   ellcard(E)          // Schoof–Elkies–Atkin -> #E(F_p)
   factor(ellcard(E))  // the smooth factorization above
   ```
   Point-counting on a 128-bit curve is exactly what `ellcard` is for; nobody
   hand-rolls Schoof in a CTF.
2. **Verify my own point arithmetic against the tool.** Before trusting any DLP result
   I cross-checked my Python `cmul` against GP's `ellmul` on 5 scalars (incl. a 19-digit
   one) — **5/5 exact matches**. This is what "reproduce, don't trust" means here: the
   attack is mine, but it stands on arithmetic I independently verified.
3. **The attack — Pohlig–Hellman + BSGS, implemented by me in Python** (`solve.py`):
   - For each prime power `q = p^e | m`, set `A = [m/q]G`, `B = [m/q]Q` (both order | q).
   - BSGS solves `B = [x]A` → `n ≡ x (mod q)`.
   - CRT over the pairwise-coprime `q` reconstructs `n mod m`.
   - Recovered `n = 203194937053061868556704865251970439522`; checked `[n]G == Q` ✓.
   - `shared_secret = x([n]B)`; `key = SHA1(str(secret))[:16]`; AES-128-CBC decrypt → flag.
   Total runtime ~5.8 s.

## What I got wrong first (the long part) — lesson
I first tried to hand-roll **Schoof's algorithm** to get `#E(F_p)`, using the residue
`a_ℓ = ℓ+1 − #E(F_ℓ)` (the reduced curve's point count). That is **not** Schoof's
congruence: Schoof's `t_ℓ` is the trace of the **p-Frobenius restricted to the ℓ-torsion
over F_p**, obtained from the ℓ-th division polynomial — not the point count of the
reduced curve mod ℓ. My "reduce and count" approach therefore produced residues that
failed the Hasse-window CRT on *every* hand-verifiable curve (I confirmed the failure
on `y²=x³+x+1 mod 7` where the true count is trivially brute-forceable). I spent a long
time chasing a bug that was a **misremembered theorem**.

**Fix:** stop hand-rolling point counting. Use a real, self-managed tool — PARI/GP
`ellcard` (Schoof–Elkies–Atkin). This matches the standing directive ("use tools you can
manage and update yourself, no Docker"). The *attack* (Pohlig–Hellman DLP) I still
implement and verify by hand — that's the learning — but the 128-bit point count is tool
territory.

**Skill update:** elliptic-curve point counting on large primes → PARI/GP `ellcard` /
`factor`. Elliptic-curve DLP on smooth-order groups → Pohlig–Hellman + BSGS. Don't
hand-roll Schoof.

## Independent verification of the flag
- `[n]G == Q` exactly (my own `cmul`, itself cross-verified against GP `ellmul`).
- Decrypting with `key = SHA1(str(x([n]B)))[:16]` yields clean ASCII with valid PKCS7 —
  a wrong shared secret would not unpad to printable text.
- Submitted to CryptoHack: accepted, page says "You have solved this challenge!",
  API `solved_challenges` 73 → 74 with `criminal` present, level 10 → 11.

## Source
- Statement + files: https://cryptohack.org/courses/elliptic/criminal/
- PARI/GP binary: https://pari.math.u-bordeaux.fr/pub/pari/windows/gp64-2-17-4.exe
- No `/solutions/`, `/solves/`, or third-party writeup consulted. (The page's
  "16 Solutions" / "View solutions" links were never opened.)

## Sources
- Case (a) — provided materials only: statement/course page, server source and provided
  files (see `## Source` above). `/solutions/` pages and third-party writeups NOT consulted,
  per the run logs. No textbook/paper/RFC cited.

