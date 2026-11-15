# Course lesson — Factoring (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_factoring`.
**Status:** completed 2026-10-06 · **Points:** 15 · **Site:** https://cryptohack.org/challenges/rsa_factoring/
**Ledger row:** `course__factoring` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Factoring (challenge-55)

## 1. Result
**SOLVED** — answer `19704762736204164635843` (the smaller prime), submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_factoring`)
- **NOT consulted:** solutions/writeups. (The statement's own "primefac-fork" resource link was noted but not used.)

## 3. The answer + verification
- Smaller prime `19704762736204164635843` (75 bits); larger `25891488409945882411992` (75 bits);
  product == the given 150-bit n. Star lit on `check-rsa_factoring`.

## 4. How it was solved
1. n = 510143758735509025530880200653196460532653147 (150-bit semiprime, two ~75-bit primes).
2. **sympy `factorint`** (ECM) found the factors in ~34 s — the statement's own hint ("modern methods",
   pointing at Lenstra ECM + GNFS) is exactly the intended path; 150 bits is trivially below the
   threshold where NFS would be needed.
3. Answer = the smaller factor.

## 5. Learning points
- The statement is a lesson in **key-size hygiene**: small-prime RSA moduli were publicized via the
  RSA Factoring Challenge; modern guidance is ≥1024-bit primes (2048-bit modulus) at minimum.
- For a ~150-bit semiprime, **ECM (sympy factorint)** is the right tool — Pollard rho is too slow
  (75-bit factors ⇒ ~2^37 iterations); NFS is overkill.

## 6. What I did / did not do
Did: read the statement, ran sympy factorint, verified product==n, submitted, verified star.
Did not: consult solutions; did not use the linked primefac-fork (sympy's ECM sufficed).

## 7. Limitations
None — exact factorization with product check.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (sympy) · Workdir: `...\challenge-55-cryptohack-factoring\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify)


## Vulnerability (plain words)
The "RSA" modulus is a 150-bit semiprime: two ~75-bit primes sit far inside the reach of modern
factoring, so anyone with an ECM implementation can rebuild the private key. The lesson is key-size
hygiene, not protocol design.

## How the answer follows
1. n = 510143758735509025530880200653196460532653147 (150 bits) from the `rsa_factoring` card.
2. `sympy.factorint` (ECM path) returned two 75-bit factors in ~34 s: 19704762736204164635843 and
   25891488409945882411992.
3. Product check: factors multiply back to n exactly; the challenge asks for the smaller prime —
   answer 19704762736204164635843; star on `check-rsa_factoring` verified 2026-10-06.

## Limitations / attempts that failed
None recorded — exact factorization with product verification. Pollard rho was judged too slow at
this factor size (~2^37 iterations) and NFS overkill (sizing notes, not failures); the statement's
linked primefac-fork was not needed (sympy's ECM sufficed). No solutions/writeups consulted.

## Sources
Statement card `rsa_factoring` (cryptohack.org RSA course); self-derived per run logs; no third-party
solutions consulted.

