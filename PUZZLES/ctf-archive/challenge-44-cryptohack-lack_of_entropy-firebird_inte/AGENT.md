---
record: agent-aar
puzzle: challenge-13394-cryptohack-lack_of_entropy-firebird_inte
category: CTF Archive
url: https://cryptohack.org/challenges/lack_of_entropy-firebird_inte/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/ctf-archive/challenge-44-cryptohack-lack_of_entropy-firebird_inte/flag.txt"
flag_sha256: 4c494041ab89ca77c12f36214663a2e6b481ea0058e60774e1519cf55b5d9547
skills: []
human_twin: AAR.md
---

# AGENT — lack_of_entropy-firebird_inte (Firebird Internal CTF, Mystiz)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
`chall.py` picks `p = random.getrandbits(256)` and derives
`q = int(gmpy2.digits(p, 3))` — i.e. the **base-3 digit string of p re-read as a
decimal integer**. So `q = f(p)` is a deterministic function of `p`: the whole
keypair has only ~256 bits of entropy and `n = p·f(p)` pins `p` uniquely.

## reusable-rules
- "Digit-permutation" prime derivations (`base-b digits read in base-b'`) are
  order-preserving whenever b' > b, so `n = p·f(p)` is invertible by bisection —
  no Coppersmith/lattice needed despite the "lack of entropy" framing.
- The title was a red herring (or refers to `random` vs `secrets`): no MT19937
  state recovery or keyspace brute was needed; monotonicity collapses the search.
- Quick magnitude sanity-check first (n ≈ p^3.096 ⇒ p ≈ n^0.323) tells you the
  search bounds are sane before writing anything.

## anti-patterns / limits
- Nothing failed: single-shot solve, no failed strategies to report.
- Monotonicity of `f` was spot-checked at carry boundaries (2/3, 8/9, 3^40−1/3^40)
  plus the bisection's exact-reconstruction assertion `p·f(p) == n`, which is the
  real proof — if any interval violated monotonicity, the assertion would fail.
- No third-party writeups/solutions consulted (campaign rule); derivation is
  from the provided source only.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_lack_of_entropy-firebird_inte.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided files only: `chall.py`, `output.txt` (archive.cryptohack.org card links). Self-derived from source; no writeups or solution artifacts consulted (campaign rule); no external textbook cited in run logs.
