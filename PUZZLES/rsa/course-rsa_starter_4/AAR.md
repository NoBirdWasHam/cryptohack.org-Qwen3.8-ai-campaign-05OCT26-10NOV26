# Course lesson — Private Keys (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_4`.
**Status:** completed 2026-10-06 · **Points:** 20 · **Site:** https://cryptohack.org/challenges/rsa_starter_4/
**Ledger row:** `course__private_keys` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Private Keys (challenge-52)

## 1. Result
**SOLVED** — `d = 121832886702415731577073962957377780195510499965398469843281`, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_4`)
- **NOT consulted:** solutions/writeups.

## 3. Answer + verification
- `φ(N) = (p−1)(q−1) = 882564595536224140639625987657529300394956519977044270821168` (from #51).
- `d = e⁻¹ mod φ(N) = pow(65537, -1, φ(N))` (Python 3.8+ built-in modular inverse) = `121832886702415731577073962957377780195510499965398469843281`.
- Self-check: `e·d mod φ(N) == 1` ✓. Verified by the leaderboard star.

## 4. How it was solved
1. `φ(N) = (p−1)(q−1)`.
2. `d = inverse(e, φ(N))` via `pow(e, -1, phi)` (extended Euclidean under the hood).
3. Assert `e·d ≡ 1 (mod φ(N))`.

## 5. Learning points
- `d` is the modular multiplicative inverse of `e` **mod φ(N)** — it exists iff gcd(e, φ(N)) = 1 (guaranteed when p−1, q−1 don't share e's factors).
- `pow(e, -1, m)` is the clean way to do it in modern Python (no hand-rolled egcd needed).

## 6. What I did / did not do
Did: compute d, self-check, submit, verify star. Did not: consult solutions.

## 7. Limitations
Answer-challenge.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 · Workdir: `...\challenge-52-cryptohack-private-keys\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/`

## Vulnerability (plain words)

No vulnerability -- this is the key-generation step: what the private exponent d IS. d is defined
by the congruence `e*d = 1 (mod phi(N))`, i.e. `e*d = 1 + k*phi(N)` for some k; it exists iff
gcd(e, phi(N)) = 1 and is found by the extended Euclidean algorithm (Python: `pow(e, -1, phi)`).
That one relation is the whole correctness proof of RSA decryption:
`(m^e)^d = m^(ed) = m * (m^phi(N))^k = m (mod N)` for every unit m, by Euler's theorem. The
private key is therefore not a separate object -- it is the inverse of e in a group whose order
phi(N) only the factorization of N reveals.

## How the answer follows

With phi(N) = (p-1)(q-1) from #51: `d = pow(65537, -1, 88256459...21168) =
121832886702415731577073962957377780195510499965398469843281`; the self-check
`e*d mod phi(N) == 1` passed (AAR section 3); submitted and star-verified.

## Limitations / attempts that failed

Answer challenge; no run_log.txt in the folder; no failed attempts recorded in run logs.
Comprehension note (addition, not a correction): any representative of e^-1 mod lambda(N)
decrypts identically; the course's expected answer is the canonical inverse mod phi(N), which is
what was computed and verified by the star.

## Sources

- Statement card `rsa_starter_4` on `https://cryptohack.org/challenges/rsa/` (`site.md`); p, q,
  phi carried from the challenge-51 folder.
- Self-derived per logs; NOT consulted: solutions/writeups (AAR section 2).
- Upgrade note: re-checked at upgrade time that `pow(65537, -1, phi)` equals the archived d and
  that `e*d mod phi == 1` (comprehension check, not a new solve).

