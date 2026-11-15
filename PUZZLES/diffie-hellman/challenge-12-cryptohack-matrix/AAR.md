# AAR — matrix (75 pts)

**Result:** SOLVED — flag submitted, `score_delta: 75`. Date: 2026-10-15 (UTC).

## Sources

- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `matrix`)
- Files: `the_matrix.provided`, `flag.provided` (URLs in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups.

## Flag

`[flag — recorded in FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt]`

## How it was solved

1. Read the generator: 50×50 matrix M over GF(2); first 272 bits of `msg` = flag,
   rest random; require det ≠ 0 and multiplicative_order > 10^12; C = M^31337 saved
   as flag.enc.
2. Goal: recover M from C = M^E with E = 31337 (prime), without knowing ord(M).
   Key fact: ord(M) divides the **exponent of GL(50,2)**
   `L = lcm(2^d − 1 : 1 ≤ d ≤ 50) · 2^6` (the 2^6 comes from unipotent/Jordan
   blocks; each 2^d−1 is odd). L is 785 bits.
3. Since E ∤ L (order of 2 mod 31337 is > 50, so 31337 ∤ any 2^d−1, d≤50), solve
   `k ≡ −L·E⁻¹ (mod E)` and set `t0 = (1 + k·L)/E` — then `E·t0 ≡ 1 (mod L)`
   hence `E·t0 ≡ 1 (mod ord(M))`, so `M = C^{t0}`.
4. One fast exponentiation in GL(50,2): rows packed as 50-bit ints, mul = 2500
   AND+parity ops; ~785 squarings → under a second in pure Python.
5. Verify `M^E == C` (TRUE). Recover msg via M[i][j] = msg[i + j·N] (i.e.
   column-by-column: first 50 flag bits = column 0 of M), take 272 bits → flag.

## Exact commands

```
~/tools/crypto-ctf/venv/Scripts/python.exe -u solve.py
cd ~/Practice_runs/cryptohack_org && python submit_flag.py matrix "[flag — recorded in FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt]"
```

## Exact outputs

`solve.py` (full in `live_transcript_2026-10-15.txt`):
```
L bit_length: 785
t0 bit_length: 785
M^E == C: True
FLAG: [flag — recorded in FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt]
```

`submit_flag.py matrix "[flag — recorded in FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt]"`:
```json
{"submitted": "[flag — recorded in FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt]", "submit": {"ok": true, "status": 200, "body": "Flag submitted. Press back to return to the challenge. Please enable JavaScript for a better experience"}, "before": {"score": 7870, "solved": 166}, "after": {"score": 7945, "solved": 167}, "score_delta": 75}
```

## Verification

- `debug1.py`: optimized GF(2) mul vs naive triple-loop (5/5), mat_pow vs naive
  (137 muls), and `M^L == I` for 3 random invertible 50×50 GF(2) matrices —
  confirms both the arithmetic and the group-exponent formula.
- `M^E == C` asserted in solve (the recovered M really is an E-th root of C).
- Decoded flag is clean ASCII with the exact `crypto{...}` shape (34 chars).
- `score_delta: 75` from the user API — ground truth.

## Lessons

- **Rooting in a finite group without knowing the order:** if the order r of M
  divides a known L and E ∤ L, then M = C^t with t = (1 + kL)/E, k ≡ −L·E⁻¹ (mod E).
  The "order > 10^12" condition is a red herring — it only blocks small-order shortcuts.
- **Group exponent of GL(n,q):** lcm(q^d−1, 1≤d≤n) · p^⌈log_p n⌉. Forgetting the
  p-power (Jordan/unipotent part) is the classic mistake — it silently makes the
  root check fail.
- Bit-packing GF(2) matrices: when ANDing a packed row with packed columns, the
  index spaces must be oriented the SAME way (bit N−1−i for both), or you compute
  the mirrored product (caught by a 4×4 probe, not by the final check).
- `x & 1 << i` in Python is `x & (1 << i)` — `&` binds tighter than `<<`;
  parenthesize shifts.
- Sage `Matrix` rows built as `msg[i::N]` store the row-major message
  column-wise; invert that mapping before reading the flag.

## What I did / did not do

- Derived the group-exponent root from the provided generator source only.
- Did not attempt the (infeasible-looking) matrix DLP; not needed.

## Limitations

None. Flag submitted and API-verified (score_delta > 0).

## Configuration

- Date: 2026-10-15 (UTC); host: Windows 11, git-bash; user OWNER.
- Interpreter: `~/tools/crypto-ctf/venv/Scripts/python.exe` (stdlib only).
- Working dir: `~\Practice_runs\cryptohack_org\challenge-126-cryptohack-matrix`.
- Network: cryptohack.org only (downloads + submit/API). No socket.
- Evidence: `solve.py`, `debug1.py`, `the_matrix.provided`, `flag.provided`,
  `live_transcript_2026-10-15.txt`, `flag.txt`.
