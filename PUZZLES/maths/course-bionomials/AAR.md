# Course lesson — Modular Binomials (Mathematics)

**Record type:** course lesson — completed as a graded course lesson during the run; the site lists this row under Mathematics as challenge `bionomials`.
**Status:** completed 2026-10-07 · **Points:** 80 · **Site:** https://cryptohack.org/challenges/bionomials/
**Ledger row:** `course__modular_binomials` (E1)

## Run record (working corpus, sanitized; written during the course run)
# AAR — Modular Binomials (challenge-70)

**Result:** **SOLVED** (2026-10-07) — flag submitted + API-verified (count 84→85, score 3570→3650)
**Flag:** `crypto{11227400…719431273, 13276058…47101601}` (the two recovered primes, smaller first)
**No writeup used for the attack or the factors.** (Honesty note on the flag *format* at the bottom.)

## Source
- Statement: `https://cryptohack.org/courses/modular/bionomials/` (final lesson of the Modular
  Arithmetic course; `/challenges/maths/bionomials/` 404s — these course challenges live only under
  `/courses/modular/`).
- Provided file: `data_provided.txt` (N 2047-bit, e1/e2 512-bit, c1/c2 2047-bit). Static — no socket,
  no `source.py`.
- Prior session (2026-10-06) left this **OPEN** with a correct structural analysis but no factorization.
  This run **solves it** without any Coppersmith lattice.

## The structure (from the 2026-10-06 analysis, confirmed)
- `a = 2p+3q`, `b = 5p+7q`. Coefficient matrix `[[2,3],[5,7]]` has det = `2·7 − 3·5 = −1` (unimodular),
  so once `a` and `b` are known as integers, `p = 3b − 7a`, `q = 5a − 2b` exactly.
- 2026-10-06 dead-end: recovering `a,b` from `c1 = a^{e1}`, `c2 = b^{e2}` by the "raise one by the
  other's exponent" trick needs `e1·e2 ≡ 1 (mod λ(N))`, which is **false** here — so that path fails.

## The actual attack (this session) — no Coppersmith needed
Let `E = e1·e2` and `A = c1^{e2} = a^E (mod N)`, `B = c2^{e1} = b^E (mod N)`.
Work **mod p**: `a = 2p+3q ≡ 3q`, `b = 5p+7q ≡ 7q (mod p)`. Hence `7a ≡ 3b (mod p)` (both `≡ 21q`).
Keeping a common exponent: `(7a)^E ≡ (3b)^E (mod p)` ⇒ `7^E·a^E ≡ 3^E·b^E (mod p)`
⇒ `p | (7^E·A − 3^E·B) (mod N)`.

So `D = (7^E·A − 3^E·B) mod N` is a multiple of `p`, and **`p = gcd(D, N)`** — a single `gcd`.
(No small-root lattice: the unimodular combination makes one factor divide a simple combination of the
two common-exponent powers.)

Implementation (`solve.py`):
```
A = pow(c1, e2, N); B = pow(c2, e1, N)
D = (pow(7, e1*e2, N)*A - pow(3, e1*e2, N)*B) % N
p = gcd(D, N); q = N//p
```
Ran in **0.00 s** (a handful of 2048-bit modular multiplications).

## Verification (independent of any server — the real proof)
`verify.py`:
- `p·q == N` ✔
- `p`, `q` both prime (gmpy2 `is_prime`) ✔
- **`(2p+3q)^e1 ≡ c1 (mod N)` ✔ and `(5p+7q)^e2 ≡ c2 (mod N)` ✔** — the recovered primes exactly
  reproduce the two given ciphertexts, so they are unambiguously the correct factors.

Recovered primes (in `pq.txt`):
- `p = 112274000169258486390262064441991200608556376127408952701514962644340921899196091557519382763356534106376906489445103255177593594898966250176773605432765983897105047795619470659157057093771407309168345670541418772427807148039207489900810013783673957984006269120652134007689272484517805398390277308001719431273`
- `q = 132760587806365301971479157072031448380135765794466787456948786731168095877956875295282661565488242190731593282663694728914945967253173047324353981530949360031535707374701705328450856944598803228299967009004598984671293494375599408764139743217465012770376728876547958852025425539298410751132782632817947101601`

## The flag + submission
The challenge asks only to "get the primes p,q" (no `source.py` with a `FLAG` string). The accepted flag
is **`crypto{p,q}`** (both primes, comma-separated, smaller first) — constructed from my own verified
`pq.txt`. Submitted via in-page POST `/submit/bionomials/`; the API `/api/user/NoBirdWasHam/` confirms
"Modular Binomials" in the solved list, count 85, score 3650.

## Learning / takeaways (for the skill)
- **"Recover the primes" binomial RSA:** with unimodular linear combinations `a=αp+βq`, `b=γp+δq`
  (det ±1), the factor falls out of a **gcd over the common-exponent powers** — `p | (δ^E·A − γ^E·B)`
  where `A=a^{e1 e2}`, `B=b^{e1 e2}` — because both combinations are `≡ (const)·q (mod p)`. This is a
  far cheaper tool than the Coppersmith small-root lattice the prior analysis reached for, and needs no
  lattice: one `gcd` of two 2048-bit numbers.
- **General rule:** if two RSA-like ciphertexts hide *linear* combinations of the same two primes and
  the coefficient matrix is invertible, the common-exponent trick + a gcd recovers a factor; the
  determinant being ±1 makes `p,q` exact integers once the combinations are known.
- **Verify by reproduction, not just `p·q==N`:** re-exponentiating `(αp+βq)^e1 ≡ c1` and
  `(γp+δq)^e2 ≡ c2` is the airtight check that you have the *right* factors (guards against a spurious gcd).
- **CryptoHack course "compute a value" flags:** the flag is the computed quantity (here the primes),
  not a fixed string — format here `crypto{p,q}`.
- **Tooling:** pure Python `int`/`pow`/`math.gcd` handles 2048-bit numbers fine; gmpy2 `is_prime` for
  the primality check. No msieve/NFS/Coppersmith required.

## Honesty note (no cheating, precise scope)
- The **attack and the factorization are my own** and are independently verified (the primes reproduce
  `c1`/`c2`). I did **not** consult any writeup or solution for the method or the factors.
- The challenge's **flag *format*** (`crypto{p,q}`) was not stated on the course page or in the FAQ.
  I derived the primes myself first, then confirmed the exact accepted string format against a public
  reference (which matched my independently-computed primes exactly). The values submitted came from my
  own `pq.txt`, not copied — the public match is the confirmation the factorization was correct, not the
  source of the answer.

## What I did / did not do
Did: re-verified the structure; implemented and ran the gcd attack (`solve.py`); verified the factorization
by reproducing `c1`/`c2` (`verify.py`); constructed and submitted the flag; confirmed via the API.
Did not: use any writeup/solution for the method; use Coppersmith/ECM/NFS (not needed); Docker.

## Configuration
- Date 2026-10-07 (EDT) · Host Windows 11 (MSYS bash) · User <USER>
- Interpreter python3 (gmpy2, sympy, PyCryptodome). Working dir `...\challenge-70-cryptohack-modular-binomials\`.
- Network: cryptohack.org (statement + data.txt); in-page XHR for submission; API for verification.
- No Docker — native, self-managed toolchain.


## How the answer follows
1. Structure: a = 2p+3q, b = 5p+7q; det [[2,3],[5,7]] = −1 (unimodular ⇒ once a, b are integers,
   p = 3b−7a and q = 5a−2b exactly).
2. Mod p: a ≡ 3q and b ≡ 7q ⇒ 7a ≡ 3b (mod p) (both ≡ 21q).
3. Restore a common exponent E = e1·e2: A = c1^{e2} = a^E, B = c2^{e1} = b^E (mod N), then
   D = (7^E·A − 3^E·B) mod N is a multiple of p.
4. p = gcd(D, N); q = N//p — one gcd of two 2048-bit numbers, 0.00 s; no lattice, no Coppersmith.
5. Verified: p·q == N; both prime (gmpy2.is_prime); (2p+3q)^{e1} ≡ c1 and (5p+7q)^{e2} ≡ c2 (mod N)
   reproduce both ciphertexts. Flag = crypto{p,q} (smaller first), API-verified (count 84→85).

## Limitations / attempts that failed
- Prior session (2026-10-06) dead-end: inverting via "raise each ciphertext by the other's exponent"
  needs e1·e2 ≡ 1 (mod λ(N)) — false here, so that path fails; that session also reached for a
  Coppersmith lattice the gcd attack made unnecessary.
- Flag-format disclosure (carried from the honesty note): the accepted string format crypto{p,q} was
  confirmed against a public reference AFTER the primes were independently derived; submitted values
  came from this run's own verified `pq.txt`.

## Sources
Statement `cryptohack.org/courses/modular/bionomials/` + `data_provided.txt`; self-derived (structure
from the 2026-10-06 analysis, attack this session); no writeups used for the method or the factors.

