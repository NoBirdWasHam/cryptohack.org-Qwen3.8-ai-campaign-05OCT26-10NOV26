# AAR — lfsr-destroyer (CryptoHack, 250 pts)

## Flag
`[flag — recorded in FLAGS/misc/challenge-11-cryptohack-lfsr-destroyer/flag.txt]`
Submitted via `python3 submit_flag.py lfsr-destroyer ...` → `ok:true`, `score_delta: 250`.

## The cipher
Filter generator: 128-bit Fibonacci LFSR, feedback taps `[0,1,2,7]`
(new bit = s0⊕s1⊕s2⊕s7), output taken from state positions `[0,16,32,64,96,127]`
and combined by a fixed Boolean filter f(x0..x5) = 1 ⊕ XOR of 27 squarefree
monomials (max degree 5). 256 clocks skipped before first output.
Key = 128 random bits. Server oracle: encrypt up to 2500 bytes of **chosen**
plaintext; flag released on `get_flag` with the correct key integer.

## Vulnerability / attack
Chosen plaintext ⇒ encrypt 512 zero bytes ⇒ raw keystream (4096 bits).
Each keystream bit is a degree-5 polynomial in the 128 key bits (the tapped
bits are linear forms in the key, since the LFSR is linear). The system is
small enough to hand to a SAT solver: 128 Boolean key variables, symbolic
simulation of skip+512 output clocks, one equality constraint per keystream
bit. z3 (5.3.1) recovers the key in ~9 s; verified locally by re-running the
keystream, then sent `{"option":"get_flag","key":...}`.

## Key numbers
- 512 keystream bits used (LIMIT allows 20000); key uniquely pinned.
- Local selftest: 3/3 random 128-bit keys recovered in 6.5–14.3 s.
- Remote solve: 9.0 s (server's 15 s timeout is per-message, so offline
  solving between messages is fine).
- Filter Walsh spectrum (computed for this AAR): max |W_f(w)| = 32/64 at
  w = x1⊕x2⊕x5 ⇒ linear approximation with p = 0.75, bias ε = 0.25. A (fast)
  correlation attack was therefore also viable; not needed.

## Why not the other classic attacks
- Berlekamp–Massey: useless directly — output is nonlinear.
- Algebraic/linearization: each output bit gives 1 equation over ~27 distinct
  degree-≤5 monomials in the tapped linear forms; monomials at different
  times are (almost all) distinct, so equations ≪ monomials — hopeless with
  only 20000 keystream bits against C(128,5) ≈ 1.7e8 monomials.
- SAT sidesteps the monomial blowup entirely.

## Learning points
- Chosen-plaintext on a keystream generator = free keystream; always try
  all-zero plaintext first.
- Filter generators with ≤128-bit state are routinely SAT-tractable even
  with degree-5 filters; bit-blasted symbolic simulation of the exact
  reference class is ~30 lines and beats hand-rolled algebra.
- Check the filter's Walsh spectrum to know whether correlation attacks are
  on the table (here bias 0.25 — surprisingly strong for a "destroyer").

## Limitations / honest notes
- Did not implement a fast-correlation (lattice) attack despite the bias;
  SAT was faster to build and comfortably within time.
- z3 runtime (6–14 s) is close to the 15 s per-message timeout; a slower
  machine could need fewer keystream bits or a different solver.
- Folder hygiene: the challenge folder also contains `source_b7cb...py` +
  `output_1078...txt`, which belong to a different (ElGamal-style per-bit
  padding) challenge, not lfsr-destroyer. Left untouched.
- No third-party writeups consulted; math derived locally. Reference for
  filter-generator theory: standard textbook material (e.g. Stinson &
  Paterson, *Cryptography: Theory and Practice*, stream-cipher chapters).

## Files
- `solve.py` — `python solve.py selftest` (local) / `python solve.py` (remote).
  Needs z3 (`pip install z3-solver`; venv at ~/tools/crypto-ctf/venv).
- `flag_lfsr-destroyer.txt` — the flag.
