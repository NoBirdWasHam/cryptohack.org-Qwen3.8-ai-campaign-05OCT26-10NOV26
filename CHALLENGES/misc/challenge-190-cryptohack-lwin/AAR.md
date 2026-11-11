# AAR — CryptoHack "lwin" (L-Win, 120 pts, misc)

**Solved:** true. Flag: `crypto{minimal_polynomial_in_an_arbitrary_field}` (score_delta +120, verified via submit_flag.py JSON ok:true).

## What the challenge was
Despite the name (which suggested LWE), this is an **LFSR with unknown taps**. `lwin.py`:
state = the 384 flag bits; each clock feeds back `XOR_{t in SECRET_T} s[t]` (4 unknown taps);
768 clocks are discarded, then 2048 output bits are given in `output.txt`. So we know
`s[768..2815]` of the sequence satisfying `s[n+384] = XOR_t s[n+t]` for all n ≥ 0, and must
recover `s[0..383]` = the flag.

## The attack
1. **Recover the taps linearly.** For n ∈ [768, 2431] every index `n+t` and `n+384` lies inside
   the known window, so `Σ_t v_t·s[n+t] = s[n+384]` is a GF(2) linear system in the 384-bit
   tap-indicator vector v (1664 equations). Gaussian elimination (rows as Python ints) gave
   rank 384 → unique solution: taps **[0, 6, 15, 16]**.
2. **Backward extension.** Characteristic polynomial `p(x) = x^384 + Σ_t x^t`. Since tap 0 is
   present, p(0)=1 and the state transition is invertible; directly `s[m] = s[m+384] + Σ_{t≠0} s[m+t]`
   (equivalently divide p by x^{t_min}=1) extends the sequence backwards from the window to
   s[0..383].
3. **Verify:** forward-simulated from recovered s[0..383] with the recovered taps — reproduced
   all 2048 window bits; bytes decode to printable `crypto{...}`.

## Key numbers
- Window 2048 bits ≥ 2·384; tap system rank 384 (full), 0 free vars; taps [0,6,15,16].

## Pitfalls hit (worth remembering)
- **Naive Berlekamp–Massey fails.** BM on the window returns the *tail's* minimal polynomial
  (degree 265 on a toy), which annihilates the sequence only from n ≥ 768 onward, so backward
  extension through it corrupts the first ~119 bits. Verified by checking the BM recurrence
  against a ground-truth toy sequence (56 violations at small n).
- **Singular transition when 0 ∉ taps:** p(x) has factor x^{t_min}; the first t_min initial bits
  are then information-theoretically lost through 768 clocks (toy trials with t_min=119/191
  recovered the tail but not the head). Here tap 0 was present, so recovery was unique.
- Two coding bugs fixed during dev (pivot-store falling into consistency check; back-substitution
  direction) — caught only by the toy harness.

## Limitations
- The tap-recovery step assumes the window-only system has full rank; if it didn't, a nullspace
  search over free vars plus ASCII/prefix constraints would be needed (not implemented).
- If tap 0 were absent, head recovery would need the kernel-coset + printable-ASCII approach
  (sketched above, not implemented). Toy evidence for both cases is in toy2.py runs.

## Files
- `solve2.py` — the working solver (`python3 solve2.py [output.txt]`); `solve.py` — the failed
  BM approach (kept as evidence); `toy.py`/`toy2.py`/`dbg*.py` — toy validation harnesses.
- `lwin.py`, `output.txt` — challenge files; `flag_lwin.txt` — the flag.
## Vulnerability (plain words)
The flag *is* the LFSR's initial state, and the recurrence is linear with only 4 unknown taps. 2048 consecutive output bits (after a 768-bit warm-up) satisfy s[n+384] = XOR_t s[n+t] for the same tap set at every position — a linear system over GF(2) in the tap positions, solvable from the window alone. And because one tap sits at position 0, the state transition is invertible, so the sequence can be run *backwards* through the discarded 768 clocks and the flag reappears exactly.

## How the answer follows
1. For each n in [768, 2431] (1664 equations — every index needed lies inside the known window): sum_t v_t*s[n+t] = s[n+384], linear in the 384-bit tap-indicator vector v. GF(2) Gaussian elimination (rows as Python ints) came out rank 384 with 0 free vars -> unique taps {0, 6, 15, 16}.
2. Tap 0 present => p(0)=1 => the transition matrix is invertible; run the recurrence backwards, s[m] = s[m+384] + sum_{t!=0} s[m+t], from the known window down to s[0..383].
3. Verify: forward-simulate the recovered 384 bits with the recovered taps — reproduces all 2048 window bits; the bytes decode to printable `crypto{...}` -> flag `crypto{minimal_polynomial_in_an_arbitrary_field}` (+120, ok:true).

## Limitations / attempts that failed
- Naive Berlekamp-Massey fails: BM on the window returns the *tail's* minimal polynomial (degree 265 on a toy) which annihilates the sequence only from n >= 768, corrupting the first ~119 bits under backward extension (56 violations vs a ground-truth toy at small n). Kept as `solve.py` evidence.
- Had tap 0 been absent, p(x) carries a factor x^{t_min} and the first t_min bits are information-theoretically lost through 768 clocks (toy trials with t_min=119/191 recovered the tail, not the head); the kernel-coset + printable-ASCII fallback is sketched but not implemented.
- Two coding bugs during development (pivot-store falling into the consistency check; back-substitution direction) — caught only by the toy harness.

## Sources
Challenge files `lwin.py`, `output.txt`; own solvers `solve2.py` (working) / `solve.py` (failed BM); toy harnesses `toy.py`, `toy2.py`. No writeups consulted.
