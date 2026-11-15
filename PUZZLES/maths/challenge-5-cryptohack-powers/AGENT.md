---
record: agent-aar
puzzle: challenge-89-cryptohack-powers
category: maths
url: https://cryptohack.org/challenges/powers/
status: solved
date: 2026-10-07
flag_ref: "FLAGS/maths/challenge-5-cryptohack-powers/flag.txt"
flag_sha256: 164907c5ea43093df0971f26041645c5a2902e390f5d624347a3b00a26fe4d14
skills: []
human_twin: AAR.md
---

# AGENT — Successive Powers (challenge-89)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The list `a = [588,665,216,113,642,4,836,114,851,492,819,237]` is `x^e, x^(e+1), …, x^(e+11) (mod p)`
for an unknown integer `x` and unknown 3-digit prime `p`.

**Key observation:** the ratio of successive terms is `x` regardless of the exponent:
`a[i+1] * a[i]^{-1} ≡ x (mod p)`. So for a candidate prime `p`, **every** ratio
`a[i+1]·a[i]⁻¹ (mod p)` must equal the *same* value.

- Brute-force the ~58 three-digit primes. For each `p`, skip it if any `a[i] ≡ 0 (mod p)`
  (ratio undefined); otherwise compute the 11 ratios `a[i+1]·mod_inverse(a[i],p) mod p` and
  keep `p` only if they are all equal.
- **Exactly one** three-digit prime works: `p = 919`, with common ratio `x = 209`.

## reusable-rules
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

## anti-patterns / limits
Did: derived the ratio-consistency attack from the statement; brute-forced 3-digit primes; verified
by full reconstruction; submitted; API-verified.
Did not: consult any of the 30 site solutions/writeups; use any writeup flag.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement page: `https://cryptohack.org/challenges/maths/` (card `data-challenge="powers"`,
  60 pts, 5109 solves). No provided files; the 12 integers are inline. No interactive service.
- **NOT consulted:** any writeup/solution (there are 30 on the site per the card). The attack
  below is derived from the statement alone.
