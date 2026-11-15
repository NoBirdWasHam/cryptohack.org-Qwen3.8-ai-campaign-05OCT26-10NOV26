# 1337crypt v2 (DownUnderCTF 2021) — AAR

## Solved
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-55-cryptohack-1337crypt_v2-downunderctf2021/flag.txt]` — submitted, ok:true, solved-list 245→246.

## The challenge (NOT plain Fermat despite the task hint)
Files: `1337crypt-v2.sage`, `output.txt`. Sage source:
- `p, q = getPrime(1337)` — 1337-bit primes, `n = p*q` **never published**.
- `hint1 = p^2 + q^2`.
- 2× `hint2`: `a,b = getrandbits(1337)`; `x = (a+α/2^338) + (b+β/2^338)·z` in
  `K = Q(z)`, `z = p + qi` (root of `(X-p)^2 + q^2`); `y = x·conj(x)`; store `(int(y), a, b)`.
- `c = (r + flag·I)^0x1337` in `(Z/n)[I]/(I^2+1)`, printed as `im*I + re`.

## Attack
1. Model: `y = (A+Bp)^2 + (Bq)^2 = A^2 + 2ABp + B^2·hint1` with `A=a+α/2^338`, `B=b+β/2^338`.
   So `p = (Y - A^2 - B^2·h1)/(2AB)` — but naive rounding fails: `β·p` and `β²h1` terms
   make the error ~2^1338 (verified numerically; first attempt failed exactly here).
2. Key structure: with α fixed, `p(β) = C1/B − C2·B` is **linear in β to within O(1)**
   over the whole β-range (|p''_B| = O(1), chord deviation ≤ 0.25), while α contributes
   only ~2 bits total. So from the two hints:
   `q1·β1 − q2·β2 = D0 + z`, `|z| ≤ ~9` (exact rational q_i = secant slopes).
3. Scale to integers (`W_i = q_i·Lc`, `D = D0·Lc`, Lc = lcm of denominators) and solve the
   weighted CVP: lattice rows `(2^8002, 0, W1), (0, 2^8002, −W2)`, target `(0, 0, Dp)`.
   Box coords weighted so `|Wt·β'| ~ |err| ~ 2^8339`; λ1 ~ 2^8669 ⇒ true point is the
   unique closest vector. `fpylll CVP.closest_vector` (enumeration) recovers β1, β2 exactly.
   (Hand-rolled exact-Fraction Babai nearest-plane failed despite the theoretical bound;
   fpylll's enumeration worked first try — use fpylll.)
4. `p = round(p1(β1)) ± window` filtered by `h1 − p²` perfect square + primality of p, q.
5. Decrypt in the Gaussian ring: `λ = lcm(p²−1, q²−1)`, `d = e^{-1} mod λ`,
   `m = c^d` via pair arithmetic mod n; verify `m^e == c`; flag = `long_to_bytes(im(m))`.

## Key numbers
W1,W2 ~ 2^9335, Lc ~ 2^8335, D ~ 2^9670; true residual err ~ 2^8336 < Lc·16 ✓;
λ1 ~ 2^8669 vs true CVP distance ~ 2^8345 (unique closest, gap ~2^324).

## Learning points
- Always run the error analysis before trusting a "close values" attack: the floor `int(y)`
  and the `β/2^338` offsets looked negligible but the `β²·h1` term dominates y itself.
- Functions of the form C1/B − C2·B over a unit interval are linear to O(1) — that residual
  structure is the whole exploit ("mantissa_in_crypto" pun: the fractional bits leak p).
- For weighted CVP with box ≫ error, use fpylll `CVP.closest_vector`, not DIY Babai.
- e=0x1337=4919 prime; ring exponent λ = lcm(p²−1, q²−1) works for Z[i]/(n) regardless of
  how −1 splits mod p, q; always re-encrypt to verify.

## Limitations
- First attempt (naive rounding of p from one hint) failed as predicted by error analysis.
- Hand-rolled exact-Fraction Babai nearest-plane returned a wrong point on the real lattice
  even though the synthetic instance passed; root cause not chased — replaced by fpylll
  enumeration (worked immediately).
- No listener involved (static output.txt challenge); nothing to hammer.

## Files
- `solve2.py` — full working solve (run with ~/tools/crypto-ctf/venv python).
- `solve.py` — first (failed) naive-rounding attempt, kept for the record.
- `1337crypt-v2.sage`, `output.txt` — original challenge files.
- `flag_1337crypt_v2-downunderctf2021.txt` — the flag.

## Sources
not recorded in run logs (pre-discipline solve)
