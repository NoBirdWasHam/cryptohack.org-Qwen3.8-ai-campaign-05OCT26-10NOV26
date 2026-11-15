# Course lesson — Crossed Wires (RSA)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under RSA as challenge `wires`.
**Status:** completed 2026-10-06 · **Points:** 100 · **Site:** https://cryptohack.org/challenges/wires/
**Ledger row:** `course__crossed_wires` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Crossed Wires (challenge-63)

## 1. Result
**SOLVED** — flag ``flag — recorded in FLAGS/rsa/course-wires/flag.txt``, submitted + star verified 2026-10-06 (UTC).

## 2. Source
- Statement: `https://cryptohack.org/challenges/rsa/` (card `wires`)
- Provided files: `source_provided.py`, `wires_output.txt` (from the category-page file links)
- **NOT consulted:** solutions/writeups. (The statement's "RSA: how to factorize N given d"
  resource link names the exact technique used.)

## 3. The flag + verification
- ``flag — recorded in FLAGS/rsa/course-wires/flag.txt``
- Verified: `e·d − 1 = k·φ` with k = 8254 divides exactly; p·q == N; `(p−1)(q−1) == φ`;
  re-encrypting the flag with the 5 friends' e_i (in order) reproduces the given ciphertext; star lit.

## 4. How it was solved
1. Everyone shares **my N**; each friend's "key" is just `(N, e_i)` with `e_i` a 17-bit prime.
   The flag was encrypted 5× in sequence: `c = m^{e1 e2 e3 e4 e5 mod ?}` — no, precisely
   `c = ((...((m^{e1})^{e2})...)^{e5}) mod N`, so reversing needs `e_i⁻¹ mod φ(N)` for each.
2. I'm given **both** `e = 0x10001` **and** `d` for the same N, so `e·d − 1 = k·φ(N)` for small `k`
   (k < e). Enumerating `k = 1..e` and testing the quadratic `x² − (N−φ+1)x + N` for a square
   discriminant + `p·q == N` recovered φ at **k = 8254** (p, q 1024-bit).
3. `d_i = inverse(e_i, φ)` for each friend; applying them in reverse order to `c` yields the flag.

## 5. Learning points
- **"Factor N given (e, d)"**: knowing *both* exponents for a modulus is fatal — `ed − 1` is a
  multiple of φ, and because φ ≈ N the multiplier k is small, so a short enumeration (or
  continued fractions) recovers φ and hence p, q. This is the *dual* of Wiener's attack (which
  recovers a small d from e alone).
- The social angle: "friends using their own keys" is harmless as long as they don't reuse your N —
  but here they all encrypted under *your* modulus, so anyone who can break your key breaks all of
  their encryptions.
- Composition of RSA under one N: `m^a` then `^b` = `m^{ab mod λ(N)}`; reversing needs the
  per-exponent inverses mod φ (or λ) — order matters when applying them.

## 6. What I did / did not do
Did: read source + output, recovered φ via k-enumeration (the resource's technique), verified
p·q==N and (p−1)(q−1)==φ, undid the 5 encryptions in reverse, re-verified by re-encrypting,
submitted, verified star. Did not: consult solutions.

## 7. Limitations
None — exact φ recovery + full re-encryption round-trip.

## 8. Configuration
- Date: 2026-10-06 (UTC) · Host: Windows 11 (MSYS), git-bash · User: <USER>
- Interpreter: python3 = 3.10.11 (pycryptodome) · Workdir: `...\challenge-63-cryptohack-crossed-wires\`
- Agent/model: Hermes Agent, qwen38-27b, desktop · Tools: terminal, browser
- Network: `https://cryptohack.org/challenges/rsa/` (submit/verify), static file fetches


## Vulnerability (plain words)
All five friends encrypt under MY modulus N, and I am given BOTH e and d for that N. Then e·d − 1 is
a small multiple of φ(N); enumerating the multiplier recovers φ, factors N, and thereby inverts every
friend's exponent.

## How the answer follows
1. c = ((…(m^{e1})^{e2}…)^{e5}) mod N with five 17-bit primes e_i on shared N; my (e = 0x10001, d)
   given.
2. e·d − 1 = k·φ(N) with k < e; enumerate k, φ = (ed−1)/k, test x² − (N−φ+1)x + N for square
   discriminant and p·q == N. Hit at k = 8254 (1024-bit p, q; (p−1)(q−1) == φ verified).
3. d_i = inverse(e_i, φ); apply d_5 … d_1 in reverse order to c →
   ``flag — recorded in FLAGS/rsa/course-wires/flag.txt``; re-encrypting with the five e_i in
   order reproduces the ciphertext; star verified 2026-10-06.

## Limitations / attempts that failed
None recorded. (The AAR's first-pass phrasing "m^{e1 e2 …} mod ?" was self-corrected in-place to the
sequential-power reading — a formulation note, not a failed attack.) No solutions/writeups consulted.

## Sources
Provided `source_provided.py` + `wires_output.txt`; statement's "RSA: how to factorize N given d"
resource (technique named there); self-derived; no writeups.

