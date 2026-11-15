# AAR — lack_of_entropy-firebird_inte (Firebird Internal CTF, Mystiz)

**SOLVED.** Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-13394-cryptohack-lack_of_entropy-firebird_inte/flag.txt]` (submitted ok:true, status 200;
solved count 256→257; score_delta 0 as expected for 0-pt archive challenges).

## The vulnerability
`chall.py` picks `p = random.getrandbits(256)` and derives
`q = int(gmpy2.digits(p, 3))` — i.e. the **base-3 digit string of p re-read as a
decimal integer**. So `q = f(p)` is a deterministic function of `p`: the whole
keypair has only ~256 bits of entropy and `n = p·f(p)` pins `p` uniquely.

## The attack
`f` is **strictly increasing**: if `p < p'` then base-3(p) has fewer digits than
base-3(p') (→ fewer decimal digits → smaller), or the same length with
lexicographically smaller digits (→ smaller as a decimal string). Carries at
powers of 3 don't break it (e.g. 2→"2"→2, 3→"10"→10). Therefore
`g(p) = p·f(p)` is strictly increasing on positive integers, and
`p = g⁻¹(n)` is recovered by **binary search** on `[1, 2^300]` — ~300 steps,
instant. Then standard RSA: `d = e⁻¹ mod (p-1)(q-1)`, `m = c^d mod n`.

## Key numbers
- p = 108620945043711001039798448113818516279249705471113441037537257405725491373069 (256 bits)
- q = f(p) = 11222…2221 (535 bits, decimal digits only 0/1/2 by construction)
- Verified: `p·q == n`, both prime, and `pow(m, e, n) == c` round-trip on the
  recovered flag bytes.

## Learning points
- "Digit-permutation" prime derivations (`base-b digits read in base-b'`) are
  order-preserving whenever b' > b, so `n = p·f(p)` is invertible by bisection —
  no Coppersmith/lattice needed despite the "lack of entropy" framing.
- The title was a red herring (or refers to `random` vs `secrets`): no MT19937
  state recovery or keyspace brute was needed; monotonicity collapses the search.
- Quick magnitude sanity-check first (n ≈ p^3.096 ⇒ p ≈ n^0.323) tells you the
  search bounds are sane before writing anything.

## Limitations
- Nothing failed: single-shot solve, no failed strategies to report.
- Monotonicity of `f` was spot-checked at carry boundaries (2/3, 8/9, 3^40−1/3^40)
  plus the bisection's exact-reconstruction assertion `p·f(p) == n`, which is the
  real proof — if any interval violated monotonicity, the assertion would fail.
- No third-party writeups/solutions consulted (campaign rule); derivation is
  from the provided source only.

## Files
- `chall.py`, `output.txt` — provided files (downloaded from archive.cryptohack.org links on the category card)
- `statement.txt`, `site.md` — statement + provenance
- `solve.py` — runnable (`~/tools/crypto-ctf/venv/Scripts/python.exe solve.py`)
- `flag_lack_of_entropy-firebird_inte.txt` — the flag

## Vulnerability (plain words)
The RSA keypair is made from ONE random draw: p is 256 random bits and the "second prime" q is just the base-3 digit string of p re-read as a decimal number, q = f(p). q adds no randomness at all, so n = p·f(p) is an equation in a single unknown — the "lack of entropy" is exactly this second-prime-free keygen.

## How the answer follows
1. f is strictly increasing: more base-3 digits ⇒ more decimal digits; same length ⇒ lexicographic digit order = decimal order; carries at powers of 3 never break it (spot-checked at 2/3, 8/9, 3^40−1/3^40).
2. Hence g(p) = p·f(p) is strictly increasing ⇒ p = g⁻¹(n) is unique and binary search on [1, 2^300] (~300 evaluations) recovers it; the assertion p·f(p) == n is the proof.
3. Standard RSA from there: d = e⁻¹ mod (p−1)(q−1), m = c^d mod n; verified pow(m, e, n) == c on the flag bytes ⇒ flag `[flag — recorded in FLAGS/ctf-archive/challenge-13394-cryptohack-lack_of_entropy-firebird_inte/flag.txt]` (submitted ok:true, solves 256→257).

## Limitations / attempts that failed
- Single-shot solve — no failed attempts recorded in run logs ("Nothing failed", original Limitations section).
- Monotonicity was justified by spot-checks + the exact-reconstruction assertion rather than a formal proof over every interval; the assertion failing would have flagged any violation.

## Sources
Provided files only: `chall.py`, `output.txt` (archive.cryptohack.org card links). Self-derived from source; no writeups or solution artifacts consulted (campaign rule); no external textbook cited in run logs.
