---
record: agent-aar
puzzle: challenge-7-cryptohack-backpack
category: post-quantum
url: https://cryptohack.org/challenges/backpack/
status: solved
date: 2026-10-24
flag_ref: "FLAGS/post-quantum/challenge-7-cryptohack-backpack/flag.txt"
flag_sha256: e049b07943d5d49336a3b0a4f480fe3daff4f841a41779bcbb1bede6251a5781
skills: []
human_twin: AAR.md
---

# AGENT — CryptoHack "backpack" (120 pts, integer knapsack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack (solve10_halfcvp.py)" [OBSERVED text; evidence tag applies to its source, not each claim]
Exact subset-sum on the 182 unknown bits: `aU·x = t` where `t = ct − Σ(known 1-bits)`.
**Half-integer-target CVP**: lattice `L = {(2x, 2·aU·x) : x ∈ Z^182} ⊂ Z^183`
(rows `(2e_i, 2aU_i)`), target `T = (1^182, 2t)`. Then

`dist²((2x, 2aU·x), T) = Σ(2x_i−1)² + (2(aU·x−t))²`

- any 0/1 `x` with `aU·x = t` (the message): dist² = 182 exactly;
- any other integer point: a coord outside {0,1} adds ≥ +8, or `aU·x ≠ t` adds ≥ 4.

So the message is the **unique closest lattice point** (0/1 solution is unique at
density 0.48). Plain LLL + **Babai nearest-plane** found it in ~3 s total. Verified by
recomputing the full 272-bit `ct` from the candidate flag before submitting.

## reusable-rules
1. **CLOS/SVP formulations are structurally wrong here.** The lattice with rows
   `(e_i, W·a_i)` + `(0, W·t)` contains the kernel relations `(w, 0)` with
   `aU·w = 0` — try9 found relations of norm² 46, *shorter* than the message vector
   (norm² ≈ 91). So SVP/BKZ on CLOS returns relations, never the message; scanning
   reduced rows for a 0/1 row (solve_bkz.py) is a lottery.
2. **try5's CVP target `1^182` is biased**: penalty `(x_i−1)²` gives x=0 and x=2 the
   same cost as x=1-shifts, so non-0/1 solutions (e.g. message + short relation) can be
   strictly closer than the message → enumeration returns a wrong point.
   The symmetric half-integer target (scaled ×2 to stay integral) is the fix: it is
   *flat* on {0,1}^182 and strictly penalizes everything else.
3. Exact-CVP-on-kernel (min ‖v‖ over the solution coset) is also unsafe: ‖m+w‖ can drop
   below ‖m‖ via ⟨m,w⟩<0; the objective must be ‖x−½‖, not ‖x‖.

## anti-patterns / limits
1. **CLOS/SVP formulations are structurally wrong here.** The lattice with rows
   `(e_i, W·a_i)` + `(0, W·t)` contains the kernel relations `(w, 0)` with
   `aU·w = 0` — try9 found relations of norm² 46, *shorter* than the message vector
   (norm² ≈ 91). So SVP/BKZ on CLOS returns relations, never the message; scanning
   reduced rows for a 0/1 row (solve_bkz.py) is a lottery.
2. **try5's CVP target `1^182` is biased**: penalty `(x_i−1)²` gives x=0 and x=2 the
   same cost as x=1-shifts, so non-0/1 solutions (e.g. message + short relation) can be
   strictly closer than the message → enumeration returns a wrong point.
   The symmetric half-integer target (scaled ×2 to stay integral) is the fix: it is
   *flat* on {0,1}^182 and strictly penalizes everything else.
3. Exact-CVP-on-kernel (min ‖v‖ over the solution coset) is also unsafe: ‖m+w‖ can drop
   below ‖m‖ via ⟨m,w⟩<0; the objective must be ‖x−½‖, not ‖x‖.

## artifacts [OBSERVED]
- code: diag2.py, diag3.py, diag_lattice.py, solve10_halfcvp.py, solve_backpack.py, solve_bkz.py, test_clos.py
- data/logs: flag_backpack.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Lagarias–Odlyzko low-density attack; Impagliazzo–Thurber threshold; Babai nearest-plane
(textbook: HPS §2.14 lattice crypto). No CryptoHack solutions/writeups consulted.
