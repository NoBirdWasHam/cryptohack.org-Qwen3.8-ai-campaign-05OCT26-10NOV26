# Course lesson — Monoprime (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `monoprime`.
**Status:** completed 2026-10-06 · **Points:** 30 · **Site:** https://cryptohack.org/challenges/monoprime/
**Ledger row:** `course__monoprime` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Monoprime (challenge-57)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/challenge-9-cryptohack-monoprime/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `monoprime`)
- Provided file: `monoprime_output.txt` from `https://cryptohack.org/static/challenges/output_086036e35349a406b94bfac9a7af6cca.txt`
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/challenge-9-cryptohack-monoprime/flag.txt``
- Verified: (a) re-encrypting the recovered flag with (e, n) reproduces `ct` exactly (`pow(m, e, n) == ct` ✓); (b) leaderboard star lit.

## 4. How it was solved
1. `n` is a **single prime**, not p·q. For a prime modulus `φ(N) = n − 1` (no factoring at all).
2. `d = inverse(e, n−1)` (e=65537).
3. `m = pow(ct, d, n)` → ``flag — recorded in FLAGS/rsa/challenge-9-cryptohack-monoprime/flag.txt``.

## 5. Learning points
- RSA's modulus must be **composite** (a product of two large primes). If `n` is prime, `φ(n)=n−1`
  is public information and the whole trapdoor vanishes — decryption is one `pow`.
- The "why two primes?" resource the statement links to is exactly this: with one prime there's no
  hidden φ, so the problem is trivially invertible.

## 6. What I did / did not do
Did: read output.txt, recognised the single-prime modulus, computed φ=n−1, decrypted, re-verified by
re-encryption, submitted, verified star. Did not: consult solutions.

## 7. Limitations
None — full round-trip (re-encrypt) verification available.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-57-cryptohack-monoprime\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static output.txt fetch


## Vulnerability (plain words)
The modulus n is a single prime instead of a product of two. Then φ(n) = n − 1 is public and the RSA
trapdoor collapses: decryption is one modular exponentiation with no factoring at all.

## How the answer follows
1. Inspected `monoprime_output.txt`: n is prime (single-prime modulus).
2. φ = n − 1; d = inverse(65537, n−1); m = pow(ct, d, n) → ``flag — recorded in FLAGS/rsa/challenge-9-cryptohack-monoprime/flag.txt``.
3. Verified pow(m, e, n) == ct (round-trip); star verified 2026-10-06.

## Limitations / attempts that failed
None recorded — the prime-modulus case makes φ public, so the recovery is a unique, verified inverse.
No solutions/writeups consulted.

## Sources
Provided `monoprime_output.txt`; self-derived; no writeups.

