# Course lesson — Manyprime (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `manyprime`.
**Status:** completed 2026-10-06 · **Points:** 40 · **Site:** https://cryptohack.org/challenges/manyprime/
**Ledger row:** `course__manyprime` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Manyprime (challenge-59)

## 1. Result
**SOLVED** — flag ``flag — recorded in COURSEWORK/rsa/course-manyprime/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `manyprime`)
- Provided file: `manyprime_output.txt` (from `/static/challenges/output_5a478a5d4764257d0bbdfaed340fcbdd.txt`)
- **NOT consulted:** solutions/writeups. (The statement's "Elliptic Curve Factorization Method"
  resource link was the intended path; I used sympy's ECM-based `factorint`, the same algorithm.)

## 3. The flag + verification
- ``flag — recorded in COURSEWORK/rsa/course-manyprime/flag.txt``
- Verified: all **32 factors are prime**, product == n exactly; re-encrypting the flag with
  (e=65537, n) reproduces `ct`; star lit.

## 4. How it was solved
1. n = 2033 bits, a product of **32 distinct 64-bit primes** (2033/32 ≈ 63.5 bits each).
2. **ECM** is the right algorithm: it finds smallish factors in time polynomial in the factor size,
   so 64-bit primes drop out quickly one at a time. `sympy.factorint(n)` (ECM + trial division +
   Miller-Rabin primality) returned all 32 factors.
3. `φ(N) = Π(p_i − 1)` (Carmichael/product form over distinct primes), `d = inverse(e, φ(N))`,
   `m = pow(ct, d, N)` → flag.

## 5. Learning points
- **Choosing the factorization algorithm by factor size** is the whole lesson:
  - Pollard rho: good up to ~40–50-bit factors.
  - **ECM: good for smallish factors (≤ ~80 bits) hidden in a huge composite** — exactly this case.
  - NFS: only for large, balanced factors (the 1024-bit-and-up regime from challenge 55).
- The statement's "over 30" primes, each ~64 bits, is a deliberate ECM showcase: NFS on the whole
  2033-bit number would be hopeless, and rho would stall; ECM peels the 64-bit primes off efficiently.
- `φ` of a product of distinct primes is `Π(p_i − 1)` — no need for the (p−1)(q−1) two-prime form.

## 6. What I did / did not do
Did: read statement/output, ran sympy factorint (ECM), verified all-32-prime + product==n,
computed φ and d, decrypted, re-verified by re-encryption, submitted, verified star.
Did not: consult solutions.

## 7. Limitations
None — full factorization with product + primality checks and a re-encryption round-trip.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome, sympy) · Workdir: `...\challenge-59-cryptohack-manyprime\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
The 2033-bit modulus is a product of 32 distinct ~64-bit primes. ECM cost tracks FACTOR size, not
modulus size, so the small primes peel off quickly and φ(N) = Π(p_i − 1) becomes computable.

## How the answer follows
1. n = 2033 bits from `manyprime_output.txt`; statement says "over 30" small primes
   (2033/32 ≈ 63.5 bits each).
2. `sympy.factorint(n)` (ECM + trial division + Miller–Rabin) returned all 32 factors; verified each
   is prime and their product == n.
3. φ = Π(p_i − 1); d = inverse(65537, φ); m = pow(ct, d, n) → ``flag — recorded in COURSEWORK/rsa/course-manyprime/flag.txt``;
   re-encryption reproduces ct; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded. Algorithm-fit notes (not failures): rho stalls on 64-bit factors; NFS on the whole
2033-bit composite is hopeless; ECM is the right tool. No solutions/writeups consulted.

## Sources
Provided `manyprime_output.txt`; statement's ECM resource (algorithm named only); self-derived;
no writeups.

