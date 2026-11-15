# Course lesson — RSA Decryption (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_5`.
**Status:** completed 2026-10-06 · **Points:** 20 · **Site:** https://cryptohack.org/challenges/rsa_starter_5/
**Ledger row:** `course__rsa_decryption` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — RSA Decryption (challenge-53)

## 1. Result
**SOLVED** — decrypted message `13371337`, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_5`)
- **NOT consulted:** solutions/writeups.

## 3. Answer + verification
- `N = 882564595536224140639625987659416029426239230804614613279163` = p·q (the same modulus from #51/#52: p=857504083339712752489993810777, q=1029224947942998075080348647219).
- `m = c^d mod N = pow(77578995801157823671636298847186723593814843845525223303932, d, N) = 13371337`.
- Verified by the leaderboard star.

## 4. How it was solved
1. Recognize `N` equals `p·q` from the previous two challenges (the course reuses one modulus).
2. `d` from #52.
3. `m = pow(c, d, N) = 13371337`.

## 5. Learning points
- The course's running modulus: p, q fixed across #51–#53. Factoring N once (here, p and q were *given*) unlocks totient, private key, and decryption.
- `13371337` = "1337" repeated — leetspeak "leet", a common CTF answer motif.

## 6. What I did / did not do
Did: reuse p,q, decrypt, submit, verify star. Did not: consult solutions.

## 7. Limitations
Answer-challenge.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 · Workdir: `...\challenge-53-cryptohack-rsa-decryption\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/`

## Vulnerability (plain words)

No vulnerability -- this is the decryption step: why `m = c^d mod N` inverts `c = m^e mod N`.
Since `e*d = 1 + k*phi(N)` (the d from #52), `(m^e)^d = m^(1+k*phi) = m * (m^phi)^k = m (mod N)`
for gcd(m, N) = 1 by Euler's theorem. The non-unit edge case gcd(m, N) != 1 is not a hole:
x -> x^(ed) is the identity mod p and mod q separately (trivial where p divides m, Euler/Fermat
otherwise), so the CRT glues the two identities into the identity on all of Z/NZ -- RSA decrypts
EVERY message, not just the units. The course reuses the same p, q, N, d from #51-52, so the
operation is one modpow.

## How the answer follows

`m = pow(77578995801157823671636298847186723593814843845525223303932, d, N) = 13371337` with
N = 882564595536224140639625987659416029426239230804614613279163 and the d from #52
(AAR section 3); submitted and star-verified. (The leetspeak look of 13371337 stays as recorded
in AAR section 5.)

## Limitations / attempts that failed

Answer challenge; no run_log.txt in the folder; single pass per AAR section 6; no failed attempts
recorded in run logs. Consistency of the reused parameters is itself a check: p*q equals the
given N (re-verified at upgrade time).

## Sources

- Statement card `rsa_starter_5` on `https://cryptohack.org/challenges/rsa/` (`site.md`); p, q
  from the challenge-51 folder and d from challenge-52.
- Self-derived per logs; NOT consulted: solutions/writeups (AAR section 2).
- Upgrade note: re-checked at upgrade time that `pow(c, d, N) == 13371337` and `p*q == N`
  (comprehension check, not a new solve).

