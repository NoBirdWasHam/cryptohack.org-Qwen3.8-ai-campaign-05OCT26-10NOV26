# AAR — hide_and_seek (ECSC 2023 Norway) / cryptohack slug `hide_and_seek-ecsc_2023_norwa`

## Result
SOLVED — submitted, `ok:true`, solved count 269→270 (archive = 0 score by design).
Flag verified two independent ways: `x·P == X` DLP check, and PARI-recomputed `x mod 12775224751` matched Python (9306536884).

## Vulnerability
Curve order is smooth: `#E(F_p) = p+1-t` with `t = ellap` from PARI factors into 9 distinct primes of ~34 bits (`nn_ok=1` verified in PARI). So ECDLP on this curve is trivially solvable by Pohlig–Hellman + BSGS, once you can reduce the given oracle tuples to a bare `X = x·P` DLP instance.

## Attack (first principles, no writeups consulted)
Given 42 tuples `(a_i, b_i, R_i = a_i·P + b_i·Q)` with `Q = FLAG·P = x·P`:

- `R_i = (a_i + b_i·x)·P`.
- Take two tuples i, j:
  - `S = b_i·R_j − b_j·R_i = (a_j·b_i − a_i·b_j)·P = Δ·P`
  - `T = a_j·R_i − a_i·R_j = Δ·x·P`
- `Δ = a_j b_i − a_i b_j` is known (and invertible mod n for a non-degenerate pair), so `P = Δ⁻¹S`, `X = Δ⁻¹T`, giving a pure DLP instance `X = x·P`, `x = FLAG < n`.
- Pohlig–Hellman over the 9 prime factors (~2^34 each) using baby-step/giant-step per factor, CRT recombination. `x` verified by `x·P == X` before decoding.

## Key numbers
- p ≈ 2^309, n = #E = 1789850433742566803999659961102071018708588095980691155136886508769519951605603261424289500493 = product of 9 primes (12775224751 … 32337773063), squarefree ⇒ group cyclic.
- Largest prime factor ≈ 2^34.9 ⇒ per-factor BSGS ≈ 2^17.5 point ops, trivial.

## Files
- `hide_and_seek.sage`, `output.txt` (downloaded), `statement.txt`, `site.md`, `card.html`
- `ord.gp`/`ord2.gp` + `ord2.out` — PARI SEA trace + factorization
- `data.gp` — parsed output for PARI; `solve5.gp` — working PARI solver (killed mid-run for speed, first factor reused as cross-check)
- `solve_fast.py` + `fast.out` — final solver (gmpy2 BSGS Pohlig–Hellman, ~2 min), produced the flag
- `solve.py` — first plain-python attempt (same algorithm, too slow, superseded)

## Learning points
- "Hidden value" framing (Q = x·P) is a red herring for lattices here — two-tuple elimination `b_i R_j − b_j R_i` kills the unknown multiplier of P using only known scalars (2D kernel of [[a_i,b_i],[a_j,b_j]] trick).
- Always run `ellap` + `factor` on the group order for EC challenges: squarefree smooth order ⇒ Pohlig–Hellman regardless of how the DLP instance was dressed up.

## Limitations / honest notes
- First plain-python BSGS attempt killed at ~27 min (too slow per-step `pow(x,-1,p)`); PARI `elladd` legacy API ~25 min/factor, killed after 1 of 9 factors. gmpy2 BSGS solved it in ~2 min.
- GP gotchas found the hard way: F_p curves via `ellinit`+Mod use the old API where **infinity is `[0]`** (`elladd` rejects `[]`); multi-statement `if` bodies need `{}`, but `{}` inside call args ("embedded braces") is rejected by the parser.
- No solutions/writeups consulted; no flag value retrieved from any artifact (flag only from own derivation, cross-checked against own second implementation).

## Flag
`[flag — recorded in FLAGS/ctf-archive/challenge-23-cryptohack-hide_and_seek-ecsc_2023_norwa/flag.txt]` (also in flag_hide_and_seek-ecsc_2023_norwa.txt)

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
