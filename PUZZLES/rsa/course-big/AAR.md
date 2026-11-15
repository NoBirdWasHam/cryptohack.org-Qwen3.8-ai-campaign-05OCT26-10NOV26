# Course lesson — Everything is Big (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `big`.
**Status:** completed 2026-10-06 · **Points:** 70 · **Site:** https://cryptohack.org/challenges/big/
**Ledger row:** `course__everything_is_big` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Everything is Big (challenge-62)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/course-big/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `big`)
- Provided files: `source_provided.py`, `big_output.txt` (from the category-page file links)
- **NOT consulted:** solutions/writeups.

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/course-big/flag.txt``
- Verified: recovered `d` is exactly 256 bits (matching `getPrime(256)`); p·q == N exactly;
  re-encrypting the flag with (e, N) reproduces `c`; star lit.

## 4. How it was solved
1. The source is the giveaway: `d = getPrime(256)` — a **256-bit private exponent** on a 2048-bit
   modulus. "Massive numbers" (N and e both 2048 bits) is the misdirection; the small *d* is the bug.
2. **Wiener's attack**: from `e·d = k·φ(N) + 1` and `φ(N) ≈ N`, `|e/N − k/d| < 1/(2d²)` for
   `d < N^{1/4}` (256 ≪ 512 bits, so the condition holds with huge margin). The continued fraction
   of `e/N` has `k/d` as a convergent.
3. For each convergent: candidate `φ = (e·d − 1)/k` (must divide exactly), then solve
   `x² − (N − φ + 1)·x + N = 0` → p, q (discriminant must be a square, p·q == N).
4. The first valid convergent gave d (256 bits) and p, q (1024 bits each). `m = c^d mod N` → flag.

## 5. Learning points
- **Wiener's attack**: a private exponent `d < N^{1/4}` is recoverable from (e, N) alone via
  continued fractions. The fix is to use a *large* random `d` (standard) or to use CRT parameters.
- The dual of this: if **e and d for the same N** are both known, `ed − 1 = k·φ(N)` for an unknown
  small `k` — enumerating `k` (or using the convergent) recovers φ and factors N. (That's exactly the
  next challenge, "Crossed Wires".)
- "Big N and big e" does **not** imply security — the size of the *secret* (d) is what matters.

## 6. What I did / did not do
Did: read source + output, recognised the 256-bit d, implemented continued-fraction Wiener search,
verified p·q==N and e/N convergent, decrypted, re-verified by re-encryption, submitted, verified star.
Did not: consult solutions.

## 7. Limitations
None — exact factorization + re-encryption round-trip.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-62-cryptohack-everything-is-big\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
A 2048-bit modulus with a 256-bit private exponent d (source: `d = getPrime(256)`). Since d < N^0.25,
the continued fraction of e/N contains k/d as a convergent (Wiener's attack): big N and big e are
misdirection — the small secret exponent is the flaw.

## How the answer follows
1. From e·d = k·φ(N) + 1 and φ ≈ N: |e/N − k/d| < 1/(2d²); enumerate CF(e/N) convergents as (k, d).
2. Per convergent: φ = (e·d − 1)/k must divide exactly; solve x² − (N − φ + 1)x + N = 0; discriminant
   must be a square and p·q == N. First valid convergent gave d (256 bits) and 1024-bit p, q.
3. m = c^d mod N → ``flag — recorded in FLAGS/rsa/course-big/flag.txt``; re-encrypting reproduces c; star 2026-10-06.

## Limitations / attempts that failed
None recorded — exact factorization + re-encryption round-trip; no failed attempts logged. No
solutions/writeups consulted.

## Sources
Provided `source_provided.py` + `big_output.txt`; Wiener continued-fraction method (standard number
theory); self-derived; no writeups.

