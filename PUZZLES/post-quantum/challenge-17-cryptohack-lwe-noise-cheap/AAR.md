# AAR — Noise Cheap (challenge-181-cryptohack-lwe-noise-cheap)

## 1. Result
**SOLVED** — flag `[flag — recorded in FLAGS/post-quantum/challenge-17-cryptohack-lwe-noise-cheap/flag.txt]`, +90 pts (6915 -> 7005, 151 -> 152), submitted via `submit_flag.py` 2026-10-14 and live-verified via user API.

## 2. Source
- Socket `socket.cryptohack.org:13413`; server source cached at `_pq/13413.py`.
- **NOT consulted:** solutions/writeups (self-solve rule).

## 3. Attack (what worked)
Zero-samples give `b = A*S + p*e (mod q)` with per-sample ternary scalar `e in {-1,0,1}` (error in {-257,0,257} per sample).

**Failed attempts (for the record):**
1. Assumed a *single shared* e across all samples; tried 3 GF(q) [flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]s (e in {-1,0,1}) on 128 samples -> all inconsistent. `randint(-1,1)` is per-call; each sample has its own e.
2. Direct CVP on `L = {A c + q d : c in Z^64, d in Z^m}` (m=256), basis `[I_64  B_c; 0  qI_192]` with `B = A_Jbar * A_J^{-1} (mod q)` (det = q^192 = covolume, exact basis). LLL (127 s) + `babai` (fpylll, float64) -> wrong nearest point: residual `b - w` not ternary, coords ~1e4 (accumulated float64 nearest-plane error ~2e5 >> ||e|| ~ 3358). Babai is unreliable at this dim/offset ratio.

**Peeling attack (solved it):**
1. Split samples: `A1 = rows 0..63` (64x64, invertible mod q), `A2 = rows 64..191` (128 rows), `A3 = rows 192..255` (64 rows, verification only).
2. `B2 = A2 * A1^{-1} (mod q)` (128x64). From `b1 = A1*S + p*e1`, `b2 = A2*S + p*e2`:
   `t = p^{-1} * (b2 - B2*b1) (mod q) = e2 - B2*e1 (mod q)` — the `p^{-1}` scaling **divides the error by 257**: the CVP offset is the raw ternary `e2` (||e2|| ~ 9), not `p*e2`.
3. CVP on `L2 = {B2 c + q d} subset Z^128` (basis `[I_64  C; 0  qI_64]`, `C = B2b * B2t^{-1}`, det = q^64 = covolume). LLL (1.3 s) + **`closest_vector "proved"`** (rigorous enumeration; 0.07 s — the tight radius ||e2|| ~ 9 vs GSOs ~1e3 makes the FP-tree a single path). Returns `w = -B2*e1 (mod q)` **exactly**; `e2 = t - w` ternary, verified.
4. `e1`: solve `B2 * e1 = -w (mod q)` (128x64 GF(q) elimination); verify ternary.
5. `S = A1^{-1} * (b1 - p*e1) (mod q)`; verify against ALL 256 samples (each residual exactly in {-257,0,257}) — 0 bad.
6. Flag bytes: `v = center((b_f - A_f*S) mod q) = m + p*e_f in [-257, 384]`; `m = v mod 257`. Fetched indices 0..23 in the first connection, 24..31 in a second (S is shared across connections — sanity-checked: index 0 decrypts to 'c' on the new connection).

## 4. Key numbers
- q = 1048583 (prime); p = 257; n = 64; m = 256 zero-samples + 32 flag chars.
- ||e (256-dim)|| ~ 257*sqrt(2m/3) ~ 3358; lambda1(L) ~ q^{(m-n)/m} ~ 3.3e4 — ratio too thin for float Babai; after peeling, offset ||e2|| ~ 9 vs lambda1(L2) ~ q^{1/2} ~ 1024 — trivial for exact CVP.

## 5. Learning points / pitfalls
- **e is per-sample**, not shared — read `randint(-1,1)` inside `encrypt()`.
- **fpylll `babai` is float64**: at 256 dim it accumulated ~2e5 error and returned a wrong (but lattice) nearest point. Use `closest_vector(..., "proved")` when the true offset is tight (exact and fast — 0.07 s here).
- **Scaling by p^{-1} before CVP** shrinks the target offset by p — the peeling step makes the tight-CVP regime available.
- **Verification values must match the scaled error space**: after `p^{-1}` the error lives in {-1,0,1}, not {-257,0,257}. The intermediate "bad=92" result was a verification bug (checking the wrong set), not a CVP failure — the CVP had already succeeded.
- Block-triangular basis `[I_n  C; 0  qI_{m-n}]` for `{A c + q d}` (with `C = A_bar * A_top^{-1} mod q`) is an exact basis (det = q^{m-n} = covolume) — no HNF needed; sympy `hermite_normal_form` (row-style: pass `M.T`; needs the `D` param for speed) was the fallback.
- S is module-level in the listener: **shared across connections** (verified empirically), so data can be fetched and solved in separate sessions.

## 6. Files
- `_pq/nc_fetch.py` (256 zero + 24 flag samples -> `_nc_data.json`), `_pq/nc_solve3.py` (working solver), `_pq/nc_fetch2.py` (remaining flag chars + cross-connection sanity), `_pq/nc_debug.py` (CVP semantics debug), `_pq/_nc_flag_full.txt` (flag).
- Dead ends kept: `nc_solve.py` (shared-e assumption), `nc_solve2.py` (256-dim Babai), `nc_peel_test.py` (synthetic peeling test; its "bad" counts were the verification bug), `nc_sanity.py`.
## Vulnerability (plain words)
Two cost cuts compound: the error is a *ternary* scalar per sample (e in {-1,0,1}, i.e. error values {-257, 0, 257} mod q) and q = 1048583 ~ 2^20. The sample vector therefore sits only ||e|| ~ 3358 away from the exact lattice, where secure LWE noise looks ~ q/2 ~ 500,000 away. Worse for the scheme: the error multiplier p=257 is invertible mod q, so multiplying samples by p^-1 divides the error down to raw ternary size (norm ~ 9) — turning a thin-CVP problem into one that rigorous enumeration solves exactly and instantly.

## How the answer follows (peeling)
1. Kill the secret linearly. Split rows: A1 = rows 0..63 (64x64, invertible mod q), A2 = rows 64..191. With B2 = A2*A1^-1 (mod q): t = p^-1*(b2 - B2*b1) = e2 - B2*e1 (mod q). S cancels exactly (both samples are affine in S), and the p^-1 scaling shrinks the CVP offset from ||p*e|| ~ 3358 to ||e2|| ~ 9.
2. By construction t - (-B2*e1) = e2, so -B2*e1 is *the* nearest lattice point of L2 = {B2*c + q*d} to t. Offset ~9 vs lambda1(L2) ~ q^(1/2) ~ 1024 puts the problem deep in the unique-CVP regime: fpylll `closest_vector("proved")` (rigorous enumeration) returns it exactly in 0.07 s. The earlier full-size attempt failed only because offset 3358 vs lambda1 ~ 3.3e4 was beyond float64 Babai (accumulated ~2e5 error).
3. Read e1 off the recovered point: solve B2*e1 = -w (mod q) (128x64 GF(q) elimination), verify ternary; then S = A1^-1*(b1 - p*e1) (mod q), verified against ALL 256 samples (every residual lands in {-257,0,257}, 0 bad).
4. Flag chars: center((b_f - A_f*S) mod q) = m + p*e_f in [-257, 384], so m = v mod 257. S is module-level in the listener (shared across connections, sanity-checked), so the last 8 chars came from a second session.
Result `[flag — recorded in FLAGS/post-quantum/challenge-17-cryptohack-lwe-noise-cheap/flag.txt]`, live-verified.

## Limitations / attempts that failed
- Assumed a single *shared* e across samples; 3 GF(q) eliminations (e in {-1,0,1}) on 128 samples all inconsistent — `randint(-1,1)` is called per-encrypt, so e is per-sample.
- Direct 256-dim CVP on L = {A*c + q*d} (exact block-triangular basis, det = q^192): LLL + float64 Babai returned a wrong lattice point — accumulated float error ~2e5 >> ||e|| ~ 3358. Lesson: float Babai is unreliable when offset/lambda1 is thin; use proved enumeration when the offset is tight.
- A verification-space bug (checking residuals against {-257,0,257} *after* the p^-1 scaling, where the error lives in {-1,0,1}) reported "bad=92" although the CVP had already succeeded — the intermediate failure was bookkeeping, not math.

## Sources
- Server source cached `_pq/13413.py`; solvers `_pq/nc_solve3.py` (+ fetch/debug scripts as listed in section 6). NOT consulted: solutions/writeups (self-solve rule, recorded in the original AAR section 2). Peeling = textbook lattice game-playing; no external writeup used.
