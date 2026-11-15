# AAR — whats_my_kernel (What's My Kernel, 70 pts)

Solved 2026-10-16. Flag: `[flag — recorded in FLAGS/isogenies/challenge-17-cryptohack-whats_my_kernel/flag.txt]`. Verified via user API: score 8135→8205, solved 169→170 (exact command output: `{"submitted": "[flag — recorded in FLAGS/isogenies/challenge-17-cryptohack-whats_my_kernel/flag.txt]", "submit": {"ok": true, "status": 200, ...}, "before": {"score": 8135, "solved": 169}, "after": {"score": 8205, "solved": 170}, "score_delta": 70}`).

## Attack (self-solve, no external writeups)

The SIDH public key leaks the kernel when the two image points are collinear on the 2-primary subgroup.

1. **Data** (from server static files, verified byte-identical to local copies via `raw equal: True`):
   - E_0: y² = x³ + 1 over F_{p²}, p = 2^216·3^137 − 1 = 2443942366…73567 (434 bits), F_{p²} = F_p[i]
   - P_a, Q_a: order 2^216 (c_a = 3^137 times full generators); P_b = P_a, Q_b = Q_a
   - E_A, P_B = φ(P_a), Q_B = φ(Q_a), φ = isogeny with kernel R = P_a + n·Q_a
2. **Key observation**: Q_B ∈ ⟨P_B⟩ — the two public images lie on one cyclic subgroup.
3. **ECDLP**: solve Q_B = m·P_B in ⟨P_B⟩, ord(P_B) = 2^216 (verified: smallest s with 2^s·P_B = O is s = 216, i.e. 2^215·P_B ≠ O). Method: ℓ-adic (2-division) bit extraction, LSB-first, 216 bits, pure Python over F_{p²} (affine, one field inversion per doubling). Result:
   `m = 0xeac325184e820daac7ca1ea989e8002c894189e01e93b0e199c3a9`
   Verified by direct double-and-add: `m*P_B == Q_B : True` (two independent F_{p²} implementations agreed).
4. **Kernel relation**: φ(P_a + n·Q_a) = P_B + n·Q_B = (1 + n·m)·P_B = O. Since ord(P_B) = 2^216:
   `1 + n·m ≡ 0 (mod 2^216)` → `n ≡ −m⁻¹ (mod 2^216)`.
   (Consistency check via first-isomorphism-theorem: |im(φ|_{E[2^216]})| = 2^432/2^216 = 2^216 = |⟨P_B⟩| forces ord(P_B) = 2^216 — matches the computed s = 216.)
5. **Result**:
   `n = −m⁻¹ mod 2^216 = 0x77686f6f70735f746869735f7761735f6a7573745f615f646c6f67`
   `= bytes "whoops_this_was_just_a_dlog"` (27 bytes — exactly the 27-char FLAG slot: `n = bytes_to_long(FLAG[7:-1])`).
6. **Flag**: `[flag — recorded in FLAGS/isogenies/challenge-17-cryptohack-whats_my_kernel/flag.txt]` — accepted (+70).

The author planted the answer: the dlog recovers a 215-bit value that IS the 27-byte flag, reading "whoops_this_was_just_a_dlog" — the puzzle's own joke ("this was just a dlog").

## Errors & detours (evidence-scoped)

| # | Error | Evidence | Fix |
|---|-------|----------|-----|
| 1 | **Wrong flag-length assumption**: carried "19 hex digits (76-bit n)" from pre-compaction context | `FLAG = b"crypto{???????????????????????????}"` — inner measured **27** chars (`python -c` string op: `inner length: 27`) | n is up to 216 bits; flag inner = 27 raw bytes, not hex |
| 2 | Submitted `crypto{573745f615f646c6f67}` (= A mod 2^76, the 19-hex-digit candidate) | API: `score_delta: 0`, solved 168→168 | wrong (see #1) |
| 3 | Submitted `[flag value withheld — real-flag strings live only under FLAGS/]` (last 19 chars of the ASCII) | API: `score_delta: 0`, solved 169→169 (the +100/168→169 between submits was a different challenge, from parallel subagent work, not this one) | wrong |
| 4 | Misdiagnosis: suspected `output.txt` was locally-generated decoy data (the 215-bit ASCII "looked planted", inconsistent with a 76-bit n) | Fetched server static files: `raw equal: True` (output) and identical source — local data WAS the author's data; the real inconsistency was assumption #1 | Re-derived with 27-byte n → consistent |
| 5 | Vélu 2-isogeny closed-form work (verify_n.py, velu2_test.py) was a dead-end for the flag: needed only if the kernel were NOT recoverable by dlog; the x-map formula `x' = 2(v²+f(x))/(u−x)² − x − 4u` was verified by direct point addition on two points over F_17, but the y-map/codomain-fit failed the homomorphism check over F_17 (13/15 rows off curve; several arithmetic slips in the toy). **Not used for the solve** — the ECDLP route made it unnecessary. | terminal outputs of velu2_test.py runs | abandoned (correctly: unnecessary) |
| 6 | First solver run (pre-compaction) took 2144 s to bit 0 and died on missing `ec_sub` | solve.log / traceback | machine contention (parallel subagents); added `ec_sub`, rerun: 10.4 s total |

## Exact command receipts

- ECDLP + verification: `cd challenge-214-... && time python solve.py` → `ECDLP verified: m*P_B == Q_B`, `real 0m10.388s`
- Order check: `smallest s with 2^s*P_B = O : 216` (binary search over s, has(s) = [2^s·P_B == O])
- Independent re-verification (fresh F_{p²} impl): `m*P_B == Q_B : True`
- A + ASCII: `A = -m^-1 mod 2^216 = 0x77686f6f...67 (215 bits)`, `A ASCII: whoops_this_was_just_a_dlog`
- Flag-length proof: source line `FLAG = b"crypto{???????????????????????????}"` → `inner length: 27`
- Data authenticity: `raw equal: True` (local output.txt vs server static `output_f0f36907...txt`)
- Submission receipts: three `python submit_flag.py whats_my_kernel <flag>` calls; only the third returned `"score_delta": 70`

## Files

- `solve.py` — F_{p²} field + ECDLP (LSB-first 2-division) + verification; 10 s runtime
- `verify_n.py` — s-binary-search + candidate flag + (abandoned) 216-step Vélu chain
- `velu2_test.py` — toy Vélu 2-isogeny verification (incomplete; dead end)
- `source_real.sage`, `output_real.txt` — server-provided files (canonical)
- `site.md` — statement + setup + flag
- `solve.log` — full solver output

## Lessons (→ skill ctf-isogenies)

1. In a SIDH-style public key (images of a 2^e-torsion basis under the secret isogeny), FIRST check whether the two images are collinear (one in the other's cyclic subgroup). If Q_B ∈ ⟨P_B⟩: kernel coefficient n ≡ −m⁻¹ (mod 2^e) where Q_B = m·P_B — no isogeny computation needed. The ECDLP is e doublings + e subtractions (fast in Python for e ≈ 216, 434-bit field).
2. Read the FLAG placeholder length in the source BEFORE assuming hex encoding. `bytes_to_long(FLAG[7:-1])` on a 27-? slot gives a 216-bit integer that may be raw ASCII — the flag can literally be a sentence.
3. A recovered "weird" value (ASCII text from a dlog) is usually the author's planted answer, not a sign of broken data — re-examine your format assumptions before re-deriving the math.
4. Always re-fetch server static challenge files when doubting data provenance; `diff` in one command settles it.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
