# Course lesson — Euler's Totient (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_3`.
**Status:** completed 2026-10-06 · **Points:** 20 · **Site:** https://cryptohack.org/challenges/rsa_starter_3/
**Ledger row:** `course__euler_s_totient` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Euler's Totient (challenge-51)

## 1. Result
**SOLVED** — φ(N) = `882564595536224140639625987657529300394956519977044270821168`, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_3`)
- **NOT consulted:** solutions/writeups.

## 3. Answer + verification
- `p = 857504083339712752489993810777`, `q = 1029224947942998075080348647219`
- For distinct primes, `φ(N) = (p−1)(q−1)`.
- Computed directly; verified by the leaderboard star.

## 4. How it was solved
1. `φ(N) = (p−1)·(q−1)` (Euler product for N = p·q).
2. `857504083339712752489993810776 · 1029224947942998075080348647218 = 882564595536224140639625987657529300394956519977044270821168`.

## 5. Learning points
- φ(N) is the *trapdoor*: knowing p,q makes φ(N) trivial, and φ(N) gives d.
- RSA's security is entirely "factorization of N is hard" — the moment p,q leak, everything collapses.

## 6. What I did / did not do
Did: apply φ for a semiprime, submit, verify star. Did not: consult solutions.

## 7. Limitations
Answer-challenge.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 · Workdir: `...\challenge-51-cryptohack-eulers-totient\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/`

## Vulnerability (plain words)

No vulnerability -- this is the definition step: what phi(N) IS and why RSA cares. phi(N) counts
the residues mod N that have a multiplicative inverse. For N = p*q with distinct primes, the
Chinese remainder theorem gives a ring isomorphism Z/NZ = Z/pZ x Z/qZ, hence on unit groups
(Z/NZ)* = (Z/pZ)* x (Z/qZ)*; the factors are cyclic of orders p-1 and q-1, so
phi(N) = (p-1)(q-1). phi(N) is the ORDER of the unit group, so Euler's theorem says
a^phi(N) = 1 (mod N) for every invertible a: RSA exponents live modulo phi(N). Knowing p,q makes
phi trivial; phi gives d; therefore "factor N" is the single security assumption of the scheme.

## How the answer follows

Direct evaluation: `(p-1)(q-1) = 857504083339712752489993810776 * 1029224947942998075080348647218
= 882564595536224140639625987657529300394956519977044270821168` with the given p, q
(AAR section 3); submitted and star-verified.

## Limitations / attempts that failed

Answer challenge; no run_log.txt in the folder; no failed attempts recorded in run logs.
Comprehension note (addition, not a correction): decryption correctness only requires
e*d = 1 mod lambda(N) with lambda(N) = lcm(p-1, q-1) (Carmichael), which divides phi(N); the
course uses Euler's phi and computing with it is exactly what the site expects.

## Sources

- Statement card `rsa_starter_3` on `https://cryptohack.org/challenges/rsa/` (`site.md`).
- Self-derived per logs; NOT consulted: solutions/writeups (AAR section 2).
- Upgrade note: the (p-1)(q-1) product was re-multiplied at upgrade time and reproduced exactly
  (comprehension check, not a new solve).

