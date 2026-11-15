# AAR — Successive Powers (challenge-89)

**Result:** **SOLVED** (2026-10-07) — flag submitted + API-verified (score 3650→3710, solved 85→86)
**Flag:** `[flag — recorded in FLAGS/maths/challenge-5-cryptohack-powers/flag.txt]`

## Source
- Statement page: `https://cryptohack.org/challenges/maths/` (card `data-challenge="powers"`,
  60 pts, 5109 solves). No provided files; the 12 integers are inline. No interactive service.
- **NOT consulted:** any writeup/solution (there are 30 on the site per the card). The attack
  below is derived from the statement alone.

## The attack
The list `a = [588,665,216,113,642,4,836,114,851,492,819,237]` is `x^e, x^(e+1), …, x^(e+11) (mod p)`
for an unknown integer `x` and unknown 3-digit prime `p`.

**Key observation:** the ratio of successive terms is `x` regardless of the exponent:
`a[i+1] * a[i]^{-1} ≡ x (mod p)`. So for a candidate prime `p`, **every** ratio
`a[i+1]·a[i]⁻¹ (mod p)` must equal the *same* value.

- Brute-force the ~58 three-digit primes. For each `p`, skip it if any `a[i] ≡ 0 (mod p)`
  (ratio undefined); otherwise compute the 11 ratios `a[i+1]·mod_inverse(a[i],p) mod p` and
  keep `p` only if they are all equal.
- **Exactly one** three-digit prime works: `p = 919`, with common ratio `x = 209`.

## Verification (independent of the server)
- Ratio consistency: `a[i]·209 ≡ a[i+1] (mod 919)` for all 11 transitions ✔
- Order of `209 mod 919` = `918` (full primitive order), so the powers are distinct.
- Discrete log: `588 ≡ 209^25 (mod 919)`, and `209^(25+i) ≡ a[i]` for all `i=0..11` ✔
  (exact reconstruction of the entire list).
So `p=919, x=209` is the unique, verified solution.

## Flag + submission
Statement order is "Find **p** and **x**", so `[flag — recorded in FLAGS/maths/challenge-5-cryptohack-powers/flag.txt]`. Submitted via in-page synchronous
`XMLHttpRequest POST /submit/powers/` (same origin, carries the session cookies). The submit response
body is identical for right/wrong flags, so ground truth = the user API:
`/api/user/NoBirdWasHam/` shows **"Successive Powers" in the solved list, score 3710, 86 solved.**

## Learning / takeaways
- **"Successive powers → constant ratio" is the whole trick.** A geometric progression mod `p`
  has constant ratio `x`, so the exponent and the huge exponents don't matter — only the ratios.
  Reduces "factor nothing / dlog a huge power" to a trivial per-prime consistency check.
- **Search space is the modulus, not the base.** With `p` in a tiny range (3-digit primes) and the
  ratio constraint being *deterministic* (all ratios equal), one candidate survives — no lattice,
  no Coppersmith, no NFS.
- **Guard the degenerate case:** if some `a[i] ≡ 0 (mod p)` the inverse doesn't exist — skip that
  `p` (a term ≡ 0 would mean `x` is not a unit, and "successive powers" stops being a clean GP).
- **Verify by reconstruction**, not just the ratio check: recover the start exponent by a tiny
  discrete log (order 918 is trivial) and reproduce all 12 terms.
- **Tooling:** pure Python `sympy.isprime` + `sympy.mod_inverse`; no special libraries.

## What I did / did not do
Did: derived the ratio-consistency attack from the statement; brute-forced 3-digit primes; verified
by full reconstruction; submitted; API-verified.
Did not: consult any of the 30 site solutions/writeups; use any writeup flag.

## Configuration
- Date 2026-10-07 (EDT) · Host Windows 11 (MSYS bash) · User OWNER
- Interpreter python3 (sympy 1.12). Working dir `...\challenge-89-cryptohack-powers\`.
- Network: cryptohack.org (statement scrape + in-page XHR submit + API verify).
- No Docker — native, self-managed toolchain.


## How the answer follows
1. The list a[0..11] is x^e, x^(e+1), …, x^(e+11) mod p ⇒ every successive ratio a[i+1]·a[i]⁻¹ ≡ x
   (mod p), independent of the unknown exponent e.
2. Brute-force the ~58 three-digit primes; skip any p with some a[i] ≡ 0 (inverse undefined); keep p
   only if all 11 ratios agree. Exactly one survives: p = 919 with common ratio x = 209.
3. Verified by reconstruction: a[i]·209 ≡ a[i+1] (mod 919) for all 11 transitions;
   ord(209 mod 919) = 918; a tiny dlog gives 588 ≡ 209^25 and 209^(25+i) ≡ a[i] for all i — the whole
   list reproduced.
4. Flag = [flag — recorded in FLAGS/maths/challenge-5-cryptohack-powers/flag.txt] (statement order: p then x); API-verified (score 3650→3710, solved 85→86).

## Limitations / attempts that failed
None recorded — the ratio constraint is deterministic and the surviving candidate is unique and fully
reconstructed. Ground-truth caveat: the in-page submit response body is identical for right/wrong
flags, so the user API (not the response) served as verification; degenerate zero-ratio primes are
skipped by design (documented above).

## Sources
Statement card `powers` (12 inline integers only, no files, no service); self-derived from the
statement alone; sympy isprime/mod_inverse; none of the site's 30 solutions consulted.
