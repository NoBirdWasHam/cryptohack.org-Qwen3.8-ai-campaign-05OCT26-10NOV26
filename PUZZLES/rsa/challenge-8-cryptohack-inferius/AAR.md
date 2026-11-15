# Course lesson — Inferius Prime (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `inferius`.
**Status:** completed 2026-10-06 · **Points:** 30 · **Site:** https://cryptohack.org/challenges/inferius/
**Ledger row:** `course__inferius_prime` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Inferius Prime (challenge-56)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/challenge-8-cryptohack-inferius/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `inferius`)
- Provided files: `inferius_provided.py` (from `/static/challenges/inferius_2facb420dc30897696869e3fd11b4b4f.py`),
  `inferius_output.txt`
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/challenge-8-cryptohack-inferius/flag.txt``
- Verified: p·q == n exactly; re-encrypting the flag with (e=65537, n) reproduces `ct`. Star lit.

## 4. How it was solved
1. The provided source is the giveaway: `p = getPrime(100); q = getPrime(100)`. The comment
   "8 × (100+100) = 1600 bits strong (I think?)" confuses **decimal digits with bits** — the modulus
   is really ~200 bits, not 1600.
2. **msieve v1.53 (NFS)** factored n in seconds (3365/3096 relations):
   `p = 848445505077945374527983649411` (100 bits), `q = 1160939713152385063689030212503` (100 bits).
3. `φ = (p−1)(q−1)`, `d = inverse(e, φ)`, `m = pow(ct, d, n)` → flag.

## 5. Learning points
- **Always read the provided source.** The vulnerability was stated in the code; the "1600 bits"
  claim was the author miscounting (8 decimal digits/bit is the inverse of the real ~3.32 digits/bit).
- A 200-bit modulus is **completely broken**: NFS does it instantly on a laptop. This is the concrete
  example behind the "1024-bit primes minimum" guidance from challenge 55.
- Tooling note: pure-Python Pollard rho/SQUFOF/ECM (sympy) could not reach 100-bit factors in a
  reasonable time (~2^50 ops); a C factorizer (msieve) is the appropriate tool at this size.

## 6. What I did / did not do
Did: read source, identified 100-bit primes, ran msieve NFS, verified p·q==n, decrypted,
re-verified by re-encryption, submitted, verified star. Did not: consult solutions.

## 7. Limitations
None — exact factorization + re-encryption round-trip.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Factorizer: msieve 1.53 win64 (`~\tools\msieve153`)
- Workdir: `...\challenge-56-cryptohack-inferius-prime\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
The provided generator uses `getPrime(100)` for both primes while the comment claims "1600 bits" — the
author confused decimal digits with bits. The real ~200-bit modulus is instantly factorable by NFS, so
the ciphertext decrypts.

## How the answer follows
1. Provided `inferius_provided.py`: p, q each 100 bits ⇒ n ≈ 200 bits (the "8 × (100+100) = 1600
   bits" comment miscounts digits vs bits).
2. msieve v1.53 (NFS; 3365/3096 relations) factored n: p = 848445505077945374527983649411,
   q = 1160939713152385063689030212503; p·q == n exactly.
3. φ = (p−1)(q−1); d = inverse(65537, φ); m = pow(ct, d, n) → ``flag — recorded in FLAGS/rsa/challenge-8-cryptohack-inferius/flag.txt``;
   re-encrypting the flag reproduces ct; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded. Pure-Python rho/SQUFOF/ECM (sympy) could not reach 100-bit factors in reasonable time
(~2^50 ops) — the reason a C NFS factorizer (msieve) was used; no other paths failed. No
solutions/writeups consulted.

## Sources
Provided `inferius_provided.py` + `inferius_output.txt`; msieve 1.53; self-derived; no writeups.

