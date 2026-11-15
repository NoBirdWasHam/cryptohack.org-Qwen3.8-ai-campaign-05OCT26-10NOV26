---
record: agent-aar
puzzle: challenge-181-cryptohack-lwe-noise-cheap
category: post-quantum
url: https://cryptohack.org/challenges/lwe-noise-cheap/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/post-quantum/challenge-17-cryptohack-lwe-noise-cheap/flag.txt"
flag_sha256: bad6834d681f681c11acabe9d0f3ee14a16eabef51d274214d2b1b899a69abd7
skills: []
human_twin: AAR.md
---

# AGENT — Noise Cheap (challenge-181-cryptohack-lwe-noise-cheap)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "3. Attack (what worked)" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
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

## anti-patterns / limits
- **e is per-sample**, not shared — read `randint(-1,1)` inside `encrypt()`.
- **fpylll `babai` is float64**: at 256 dim it accumulated ~2e5 error and returned a wrong (but lattice) nearest point. Use `closest_vector(..., "proved")` when the true offset is tight (exact and fast — 0.07 s here).
- **Scaling by p^{-1} before CVP** shrinks the target offset by p — the peeling step makes the tight-CVP regime available.
- **Verification values must match the scaled error space**: after `p^{-1}` the error lives in {-1,0,1}, not {-257,0,257}. The intermediate "bad=92" result was a verification bug (checking the wrong set), not a CVP failure — the CVP had already succeeded.
- Block-triangular basis `[I_n  C; 0  qI_{m-n}]` for `{A c + q d}` (with `C = A_bar * A_top^{-1} mod q`) is an exact basis (det = q^{m-n} = covolume) — no HNF needed; sympy `hermite_normal_form` (row-style: pass `M.T`; needs the `D` param for speed) was the fallback.
- S is module-level in the listener: **shared across connections** (verified empirically), so data can be fetched and solved in separate sessions.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Socket `socket.cryptohack.org:13413`; server source cached at `_pq/13413.py`.
- **NOT consulted:** solutions/writeups (self-solve rule).
