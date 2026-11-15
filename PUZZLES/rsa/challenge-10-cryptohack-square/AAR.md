# Course lesson — Square Eyes (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `square`.
**Status:** completed 2026-10-06 · **Points:** 35 · **Site:** https://cryptohack.org/challenges/square/
**Ledger row:** `course__square_eyes` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Square Eyes (challenge-58)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/challenge-10-cryptohack-square/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `square`)
- Provided file: `square_output.txt` (from `/static/challenges/output_00dace150c0bc52f7abf03fc3e9529d2.txt`)
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/challenge-10-cryptohack-square/flag.txt``
- Verified: `isqrt(n)² == n` (exact); re-encrypting the flag with (e=65537, n) reproduces `ct`;
  star lit.

## 4. How it was solved
1. Statement says the same 2048-bit prime was used twice ⇒ suspect `n = p²`.
2. `p = isqrt(n)` → `p² == n` exactly (p is 2048 bits).
3. `φ(p²) = p² − p` (Euler's totient for prime powers: `φ(pᵏ) = pᵏ − pᵏ⁻¹`).
4. `d = inverse(65537, n − p)`; `m = pow(ct, d, n)` → flag.

## 5. Learning points
- **φ(p²) = p² − p, NOT (p−1)².** The statement's "look again at the formula for Euler's totient"
  is a pointer to exactly this. For `n = p·q` with p≠q, φ = (p−1)(q−1) = n − p − q + 1; for p=q
  that would wrongly give (p−1)² — the correct value differs by p−1.
- Square-root test (`isqrt(n)² == n`) is O(1) versus any factorization — "square root is faster
  than factoring".
- A modulus must be a product of **distinct** primes for the standard φ formula and CRT-based
  decryption to hold.

## 6. What I did / did not do
Did: read statement, square-root test, φ(p²) decryption, re-encryption round-trip, submitted,
verified star. Did not: consult solutions.

## 7. Limitations
None — exact square + re-encryption round-trip.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-58-cryptohack-square-eyes\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
The same 2048-bit prime was used twice, so n = p². An integer square root exposes p in O(1), and the
prime-power totient φ(p²) = p² − p (NOT (p−1)²) makes the key fully invertible.

## How the answer follows
1. Statement hints a repeated prime ⇒ test p = isqrt(n); p² == n exactly (p is 2048 bits).
2. φ(p²) = p² − p; d = inverse(65537, n − p); m = pow(ct, d, n) →
   ``flag — recorded in FLAGS/rsa/challenge-10-cryptohack-square/flag.txt``.
3. Verified: re-encrypting the flag reproduces ct; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded — exact square test + re-encryption round-trip; no failed attempts logged. No
solutions/writeups consulted.

## Sources
Provided `square_output.txt` + statement's totient hint for prime powers; self-derived; no writeups.

