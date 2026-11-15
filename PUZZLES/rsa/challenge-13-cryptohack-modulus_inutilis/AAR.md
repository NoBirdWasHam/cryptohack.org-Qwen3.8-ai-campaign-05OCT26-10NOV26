# Course lesson — Modulus Inutilis (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `modulus_inutilis`.
**Status:** completed 2026-10-06 · **Points:** 50 · **Site:** https://cryptohack.org/challenges/modulus_inutilis/
**Ledger row:** `course__modulus_inutilis` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Modulus Inutilis (challenge-61)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/challenge-13-cryptohack-modulus_inutilis/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `modulus_inutilis`)
- Provided files: `modulus_inutilis_provided.py`, `modulus_inutilis_output.txt` (from the category-page file links)
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/challenge-13-cryptohack-modulus_inutilis/flag.txt``
- Verified: `r = icbrt(ct)` with `r³ == ct` exactly (the exact integer cube root, not a float). Star lit.

## 4. How it was solved
1. Source sets `e = 3`; the flag is short (~24 bytes ⇒ `pt` < 2^200).
2. `ct = pow(pt, 3, n)`; since `pt³ ≈ 2^576 << n ≈ 2^2048`, **no wraparound** ⇒ `ct = pt³`.
3. Exact integer cube root of `ct` (Newton's method) = `pt` → `long_to_bytes` = the flag.

## 5. Learning points
- **Small e + short message + no padding = integer root attack.** With `e=3` and a message whose
  cube is smaller than `n`, the ciphertext *is* the plain cube. This is precisely why real RSA
  always applies **padding** (OAEP/PKCS#1 v1.5) and why "my primes are large enough" is irrelevant —
  the message size, not the key size, was the flaw.
- Use an **exact** integer root (Newton / binary search), never `round(x**(1/3))` — float precision
  is lost well before 600 bits.

## 6. What I did / did not do
Did: read source + output, identified e=3 short-message case, computed exact cbrt, verified r³==ct,
submitted, verified star. Did not: consult solutions.

## 7. Limitations
None — exact cube root is a unique, verifiable inverse.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 · Workdir: `...\challenge-61-cryptohack-modulus-inutilis\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
Textbook RSA with e = 3 and an unpadded short message: pt³ < n, so the modular reduction never fires
and the ciphertext is literally the perfect cube pt³ over the integers — an exact integer cube root
inverts it without touching the key.

## How the answer follows
1. `modulus_inutilis_provided.py` uses e = 3; flag ~24 bytes ⇒ pt < 2^200 ⇒ pt³ ≈ 2^576 << n ≈ 2^2048
   ⇒ ct = pt³ exactly (no wraparound).
2. Exact integer cube root of ct (Newton, never float): r³ == ct verified.
3. long_to_bytes(r) = ``flag — recorded in FLAGS/rsa/challenge-13-cryptohack-modulus_inutilis/flag.txt``; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded — the exact integer root is a unique, verifiable inverse (float `x**(1/3)` was avoided
as unsound past ~2^53 precision, per the run's own note). No solutions/writeups consulted.

## Sources
Provided `modulus_inutilis_provided.py` + output; self-derived; no writeups.

