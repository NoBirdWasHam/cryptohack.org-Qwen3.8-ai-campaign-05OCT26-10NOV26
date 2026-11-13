# AAR — CryptoHack "backpack" (120 pts, integer knapsack)

**Flag:** `[flag — recorded in FLAGS/post-quantum/challenge-184-cryptohack-backpack/flag.txt]` — submitted, `score_delta: 120` (ok:true).

## The vuln
Merkle–Hellman-style knapsack: superincreasing `b`, public `a_i = r·b_i mod q`, and
`encrypt` sums `a_i` over message bits **without reducing mod q**. n = 272 bits
(34-byte flag), `a_i` up to 2^378 → raw density 272/378 ≈ 0.72, but the source leaks
`crypto{...}` + `}` and ASCII MSB=0 for the 26 inner bytes → 90 bits known →
**182 unknowns, effective density 182/378 ≈ 0.48**, well under the 0.646 low-density
LLL threshold.

## The attack (solve10_halfcvp.py)
Exact subset-sum on the 182 unknown bits: `aU·x = t` where `t = ct − Σ(known 1-bits)`.
**Half-integer-target CVP**: lattice `L = {(2x, 2·aU·x) : x ∈ Z^182} ⊂ Z^183`
(rows `(2e_i, 2aU_i)`), target `T = (1^182, 2t)`. Then

`dist²((2x, 2aU·x), T) = Σ(2x_i−1)² + (2(aU·x−t))²`

- any 0/1 `x` with `aU·x = t` (the message): dist² = 182 exactly;
- any other integer point: a coord outside {0,1} adds ≥ +8, or `aU·x ≠ t` adds ≥ 4.

So the message is the **unique closest lattice point** (0/1 solution is unique at
density 0.48). Plain LLL + **Babai nearest-plane** found it in ~3 s total. Verified by
recomputing the full 272-bit `ct` from the candidate flag before submitting.

## Why the 9 prior attempts failed (key learning)
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

## Key numbers
- n=272, max a bits=378, ct bits=385; known bits 90 (prefix/suffix + 26 MSB=0);
  unknowns 182; t bits 384; lattice 182×183, entries ~2^379; LLL 2.5 s; Babai hit.

## Limitations / what didn't work (evidence in try*.log)
- try1–try4, try6–try9: CLOS basis + LLL/BKZ row-scans, exact-CVP crash
  (`gmpy2.igcdq` doesn't exist), union-of-relations (rank 180 < needed 181),
  vv norm²=234 non-0/1 — all dead ends for the reason above, not tuning.
- solve_bkz.py (BKZ-40/60 on CLOS, no log kept): same structural flaw.
- Not needed in the end: pruning, HowgraveGraham–Joux merging, q-recovery.

## References
Lagarias–Odlyzko low-density attack; Impagliazzo–Thurber threshold; Babai nearest-plane
(textbook: HPS §2.14 lattice crypto). No CryptoHack solutions/writeups consulted.
## Vulnerability (plain words)
The public key is a Merkle-Hellman knapsack, but `encrypt` forgot the mod-q reduction: the ciphertext is the *exact integer* sum of the selected public weights, so the trapdoor's scrambling hides nothing once part of the plaintext is free. The `crypto{`/`}` wrapper and the zero MSB of the 26 inner ASCII bytes pin 90 of the 272 message bits; the remaining 182 unknowns against weights of ~2^378 give subset-sum density 182/378 ~ 0.48 — under the ~0.646 low-density threshold, where the solution is provably unique and lattices find it (Lagarias-Odlyzko regime).

## How the answer follows
1. Subtract the known bits: t = ct - sum(known 1-bit weights) leaves aU*x = t over the integers in the 182 unknowns.
2. Encode 0/1 solutions as *closest* vectors, not shortest: lattice L = {(2x, 2*aU*x) : x in Z^182} (rows (2e_i, 2aU_i)), target T = (1^182, 2t). Then dist^2((2x,2aU*x), T) = sum(2x_i-1)^2 + (2(aU*x - t))^2 — an exact identity: any 0/1 solution has dist^2 = 182; any non-0/1 coordinate costs >= +8; any aU*x != t costs >= +4. At this density the 0/1 solution is unique, so the message is the unique closest lattice point: the objective is flat on {0,1}^182 and nothing else can tie or beat it.
3. Plain LLL (2.5 s) + Babai nearest-plane hit it (~3 s total). Verified end-to-end before submitting by recomputing the full 272-bit ciphertext from the candidate flag — flag `[flag — recorded in FLAGS/post-quantum/challenge-184-cryptohack-backpack/flag.txt]` (score_delta 120, ok:true).

## Limitations / attempts that failed
- Nine prior attempts (try1-try9, solve_bkz) shared one structural error: CLOS/SVP formulations contain the kernel relations (w, 0) with aU*w = 0 of norm^2 ~ 46, strictly shorter than the message vector (~91), so LLL/BKZ returns relations, never the message; row-scans for a 0/1 row are a lottery. try9's relation of norm^2 46 is the direct evidence.
- try5's integer target 1^182 is biased — (x_i-1)^2 costs x=0 and x=2 symmetrically, so non-0/1 points (message + short relation) can be strictly closer; exact-CVP-on-the-kernel-coset minimizes the wrong norm (||x|| not ||x-1/2||) for the same reason. The symmetric half-integer target (scaled x2 to stay integral) is the fix.
- Crash: `gmpy2.igcdq` does not exist (exact-CVP helper). Union-of-relations lattice had rank 180 < the needed 181. vv norm^2=234 non-0/1.
- Pruning, Howgrave-Graham-Joux merging, and q-recovery were never needed.

## Sources
Lagarias-Odlyzko low-density attack; Impagliazzo-Thurber density threshold; Babai nearest-plane via HPS (An Introduction to Mathematical Cryptography) section 2.14. No CryptoHack solutions/writeups consulted.
