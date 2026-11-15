# Course lesson — Public Keys (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_2`.
**Status:** completed 2026-10-06 · **Points:** 15 · **Site:** https://cryptohack.org/challenges/rsa_starter_2/
**Ledger row:** `course__public_keys` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Public Keys (challenge-50)

## 1. Result
**SOLVED** — ciphertext `301`, submitted + solved-star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_2`)
- **NOT consulted:** solutions/solves pages, writeups.

## 3. Answer + verification
- `N = p·q = 17·23 = 391`; `c = 12^65537 mod 391 = 301`
- Verified by the leaderboard star.

## 4. How it was solved
1. Public key = `(N, e)` where `N = p·q`.
2. `N = 17·23 = 391`, `e = 65537`.
3. RSA "encrypt": `c = pow(12, 65537, 391) = 301`.

## 5. Learning points
- The public key is *only* `(N, e)`; the primes `p,q` are private. Encryption needs no secret.
- `e = 65537 (0x10001)` is the standard small public exponent — fast encryption, and it's public anyway.
- Tiny primes (17, 23) are only for teaching — real RSA uses ≥1024-bit primes.

## 6. What I did / did not do
Did: form N, encrypt, submit, verify star. Did not: consult solutions.

## 7. Limitations
Answer-challenge.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 · Workdir: `...\challenge-50-cryptohack-public-keys\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/`

## Vulnerability (plain words)

No vulnerability -- this is the key-construction step of the RSA-101 track, said plainly. The
public key is exactly the pair `(N, e) = (p*q, 65537)`, and RSA encryption is the trapdoor
permutation `c = m^e mod N`, computed in the multiplicative monoid mod N (reduce mod N after
every square-and-multiply step). Because 65537 = 2^16 + 1 (the Fermat prime F4), the ladder needs
only 16 squarings and 1 multiply. Inverting m -> m^e mod N needs an exponent d with
e*d = 1 mod phi(N) so that (m^e)^d = m^(1+k*phi) = m for all units m (Euler's theorem) -- so
`(N, e)` alone hands over no shortcut, and the primes are the secret behind the "public" key.

## How the answer follows

`N = 17*23 = 391`; `c = pow(12, 65537, 391) = 301` (AAR section 3); submitted and
star-verified. One multiply to form N, one modpow for c.

## Limitations / attempts that failed

Answer challenge. No run_log.txt in the folder; single pass per AAR section 6; no failed attempts
recorded in run logs. The teaching primes (17, 23) make N factorable by eye -- real RSA uses
>=1024-bit primes; nothing here tests factorization hardness.

## Sources

- Statement card `rsa_starter_2` on `https://cryptohack.org/challenges/rsa/` (`site.md`).
- Self-derived per logs; NOT consulted: solutions/writeups (AAR section 2).
- Upgrade note: arithmetic re-checked at upgrade time -- 17*23 = 391 and
  `pow(12, 65537, 391) = 301` reproduced (comprehension check, not a new solve).

