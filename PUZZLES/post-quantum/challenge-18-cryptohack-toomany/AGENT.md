---
record: agent-aar
puzzle: challenge-18-cryptohack-toomany
category: post-quantum
url: https://cryptohack.org/challenges/toomany/
status: solved
date: 2026-10-17
flag_ref: "FLAGS/post-quantum/challenge-18-cryptohack-toomany/flag.txt"
flag_sha256: 029b2339da8d9a456408bc77589741fb222d0b13e8dc06f472466f2299f889c3
skills: []
human_twin: AAR.md
---

# AGENT — Too Many Errors (toomany, 100 pts, post-quantum)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The server (13390.py) is an LWE sample generator over Z_127: each `get_sample` draws
`a` (28 values) from `self.rand = random.Random(SEED)`, draws `e = self.rand.randint(-1,1)`,
then **reseeds `self.rand` with a fresh `getrandbits(32)`**, and with probability 1/2 overwrites
one random coordinate of `a`. `b = <a, FLAG> + e (mod 127)`.

The "fault" is not where the weakness is. The weakness is the `reset` option:
`reset` does `self.rand.seed(SEED)` — the **same** fixed seed. So after every reset, the
deterministic prefix of the PRNG stream (the 28 `a` draws **and** the `e` draw) is
**identical on every connection**. Only the post-reseed corruption is random.

Consequences:
- All clean samples (no corruption) return the **same** `a_clean` and the **same** `b_clean`
  (e is a fixed constant, never varying).
- A corrupted sample differs from `a_clean` in exactly one coordinate j (value v), and
  `b = b_clean + (v - a_j) * FLAG_j (mod 127)` — **exactly**, no error term, because e is the
  same constant in every sample.

So one corrupted sample per coordinate suffices: `FLAG_j = (b - b_clean) * inv(v - a_j) mod 127`
(127 is prime; invertible unless v == a_j). Two-or-more samples per coordinate give pairwise
solves `(b1-b2)*inv(v1-v2)` as a cross-check (all pairs agree exactly).

Recovery: 147 clean samples (all b=45), 153 corrupted samples covering all 28 coordinates
(5 and 26 had exactly one sample each — handled by the single-sample formula). All 8 known
positions (`crypto{...}`) recovered correctly — including j=5 via the single-sample fallback —
which validated the deterministic-e hypothesis before trusting the unknowns.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: 13390.py, collect2.py, collect3.py, solve_final.py, solve_toomany.py
- data/logs: samples.jsonl, solve_toomany.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
