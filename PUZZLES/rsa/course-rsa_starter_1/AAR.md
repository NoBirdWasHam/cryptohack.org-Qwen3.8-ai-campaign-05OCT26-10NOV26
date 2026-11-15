# Course lesson — Modular Exponentiation (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `rsa_starter_1`.
**Status:** completed 2026-10-06 · **Points:** 10 · **Site:** https://cryptohack.org/challenges/rsa_starter_1/
**Ledger row:** `course__modular_exponentiation` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Modular Exponentiation (challenge-49)

## 1. Result
**SOLVED** — answer `19906`, submitted + solved-star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `rsa_starter_1`)
- **NOT consulted:** solutions/solves pages, writeups.

## 3. Answer + verification
- `101^17 mod 22663 = 19906`
- Computed with Python's built-in `pow(101, 17, 22663)` (three-arg modular exponentiation — exactly what the lesson introduces). Verified by the leaderboard star.

## 4. How it was solved
1. Recognize the task is a single modular exponentiation.
2. `pow(base, exp, mod)` computes `base^exp mod mod` in O(log exp) via square-and-multiply — no giant intermediate.
3. Answer: `19906`.

## 5. Learning points
- Modular exponentiation is the *primitive* of RSA (encryption = `c = m^e mod N`).
- Always use the three-arg `pow` in Python — it never materializes the full `101^17`.
- A "trapdoor function" is easy forward, hard reverse without the key — RSA's `x -> x^e mod N` is exactly that (inverse needs the factorization / φ(N)).

## 6. What I did / did not do
Did: compute the value with the stated operation, submit, verify the star. Did not: consult any solution.

## 7. Limitations
Answer-challenge: the value is the answer; no interactive flag to re-derive independently.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS_NT-10.0-26200), git-bash · User: <USER>
- Interpreter: python3 = Python 3.10.11 · Workdir: `~\Practice_runs\cryptohack_org\challenge-49-cryptohack-modular-exponentiation\`
- Agent/model: Hermes Agent (Nous Research), qwen38-27b, desktop · Tools: terminal, browser (submit + star check)
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify)

## Vulnerability (plain words)

No vulnerability -- this is a knowledge/observation drill in the RSA-101 track, said plainly:
the task is to apply the definition of modular exponentiation, the primitive RSA is built on.
The map x -> x^e mod N (here 101^17 mod 22663) is computed by square-and-multiply: expand the
exponent in binary, repeatedly square and multiply in, reducing mod N at every step. Reduction is
legal at every step because (a mod N)(b mod N) = ab (mod N), so the computation stays in
{0..N-1} and costs O(log e) multiplications -- it never materializes the full 101^17. Inverting
x -> x^e mod N is hard without the factorization of N (one needs the exponent of the unit group,
phi/lambda); that easy-forward/hard-backward asymmetry is exactly what RSA later keys on.

## How the answer follows

Python's three-argument `pow(101, 17, 22663)` IS square-and-multiply -> `19906` (AAR section 3),
submitted and leaderboard-star-verified. One operation, one value.

## Limitations / attempts that failed

Answer challenge: the computed integer is the answer; nothing to re-derive independently. Single
pass per AAR section 6; no run_log.txt in the folder and no failed attempts recorded in run logs.

## Sources

- Statement card `rsa_starter_1` on `https://cryptohack.org/challenges/rsa/` (`site.md`).
- Self-derived per logs; NOT consulted: solutions/solves pages, writeups (AAR section 2).
- Upgrade note: arithmetic re-checked at upgrade time -- `pow(101, 17, 22663) = 19906` reproduced
  (comprehension check, not a new solve).

