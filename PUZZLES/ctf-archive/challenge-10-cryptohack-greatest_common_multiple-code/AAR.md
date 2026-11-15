# AAR — Greatest Common Multiple (CryptoHack archive, `greatest_common_multiple-code`)

**Result: UNSOLVED (second run, verdict re-derived independently).** No flag obtained; nothing submitted.
Consolidates and extends the first attempt (artifacts also on disk at `challenge-317-cryptohack-greatest_common_multiple-code/`;
campaign queue assigns this slug nn=263 — this folder is the canonical one, scripts copied from 317).

## The challenge
Interactive listener `archive.cryptohack.org:2762`, source `chall.py` (PoW 26, alarm 20).
Per connection: `key(16B)`, `nonce=urandom(12)`, `s=[gen(), gen()]`, `gen()=urandom(12)`.
Commands: `tag` → GCM tag of AAD=`s[0]`, ciphertext=`s[1]` (fresh cipher object, **same key+nonce always**);
`u1` → `s[randbit()] = gen()` (replace entry with one fresh 12B block); `u2` → `s[randbit()] += gen()`.
Empty line exits; win check is `input("tag: ") == new().digest().hex()` = tag of a **fresh empty-data**
GCM cipher = **E = AES_K(J0)**, J0 = nonce‖0⁴00000001 (numerically verified in run 1 with pycryptodome 3.24).
The state `s` is irrelevant to the check: the task is to extract E from tags `T = GHASH_K(A,C) ⊕ E`.
(The title "greatest common multiple" is misdirection — this is not an RSA/batch-gcd challenge.)

## Why it resists (this run's fresh derivation, `identifiability_check.py`)
Every server block is a 12-byte block ⇒ a GF(2)-linear GHASH over unknown coefficients drawn from the
96-dim subspace V ⊂ GF(2^128) (zero-padded blocks). Writing T = Σ a_i H^{n+m+1-i} ⊕ Σ c_j H^{n+1-j} ⊕ L H ⊕ E:

1. **No linear combination of tags cancels the fresh blocks while keeping E.** Each `u1`/`u2` injects a
   fresh uniform V-block; any E-free combination still carries one fresh block × a power of H.
2. **Alternate-world kernel (new, this run, numerically verified):** E′ = E ⊕ Δ is consistent with the whole
   transcript (shift the fresh blocks accordingly: δ = (H⊕1)Δ for u2-chains, ΔH⁻¹/ΔH⁻² for u1-pairs) iff Δ
   lies in the operation-type subspaces: u2-chain on s1 ⇒ Δ ∈ (H⊕1)⁻¹V; on s0 ⇒ Δ ∈ H²(H⊕1)⁻¹V;
   u1-on-s1 pair ⇒ Δ ∈ HV; u1-on-s0 pair ⇒ Δ ∈ H²V. For random H: two types leave a **64-dim**
   (2⁶⁴-candidate) ambiguity in E; three/four types **32-dim** (`identifiability_check.py`, 3 trials,
   dims 64→32, stable). So **without knowing H, E is information-theoretically hidden** — no strategy over
   short transcripts can beat ~2⁻³². With H known, branch coins become detectable (32-bit V-membership)
   and diverse operation types shrink the kernel toward {0} (run-1 AAR: needed ~16-long known-path chain).
3. **Hence the attack reduces entirely to H-recovery** from membership equations D = v·H^k, v∈V unknown
   (each observed `u1`-pair tag-xor D gives 32 quadratic GF(2) equations in H's 128 bits + 96 aux vars).
   P≈5 samples ⇒ square-ish quadratic system (~600 vars) — F4/F5 territory; no Sage/Magma on host,
   fpylll F4M at that size is hours+ (run 1 also hit the pip/python f4py mismatch).

## Live facts (run 1, probes runnable here: probe1–3.py incl. md5 PoW solver)
- Server matches `chall.py` exactly; current-state tag and `"0"*32` rejected at the final prompt; per-connection
  salt/key/nonce (cross-session reuse ruled out); no error/traceback channel; silent close on wrong final answer.

## Limitations / honest negatives
- 2 solver runs now; zero flags; nothing submitted (a guessed flag would be rejected and is also disallowed).
- Did NOT consult /solutions/, /solves/, or writeups per SOLVER_BRIEF; all math self-derived
  (standard refs: McGrew-Viega GCM spec for GHASH structure).
- Not executed (out of budget): F4 Gröbner solve of the H-membership system in Magma/Sage-class tooling,
  and joint (H, branch-path) disjunctive solving. If a future run has real Magma/F5, that is the only door.
- Loop-guard respected; no server hammering (≤1 session/attempt class in run 1, 0 new sessions this run —
  verdict is provable offline: the hiding argument is a theorem about the tag algebra, independent of transcript).

## Files
- `chall.py` server source; `statement.txt`, `site.md` statement/metadata; `probe1.py`–`probe3.py` live probes
  (run 1, include PoW solver); `identifiability_check.py` **this run's** GF(2^128) kernel-dimension check
  (self-contained, no deps: `python3 identifiability_check.py` prints ambiguity dims per constraint-type stack).

## The challenge (plain words)
Interactive listener (archive.cryptohack.org:2762, source chall.py; PoW 26, alarm 20): the win check is submitting the tag of a FRESH empty-data GCM cipher -- exactly E = AES_K(J0) -- while the only thing the server gives you are tags T = GHASH_K(A,C) XOR E over two 12-byte-block state slots s=[s0,s1], via commands `tag` (current state's tag), `u1` (replace a random slot with one fresh block) and `u2` (add a fresh block to a random slot). The state s is irrelevant to the check, so the task is to extract E from masked tags. The title "greatest common multiple" is misdirection -- not an RSA/batch-gcd challenge.

## Current state of the attack
Evidenced negative, provable offline. The attack reduces ENTIRELY to recovering GHASH's H from membership equations D = v*H^k with v in V unknown (V = the 96-dim subspace of zero-padded blocks in GF(2^128)); each observed u1-pair tag-xor D gives 32 quadratic GF(2) equations in H's 128 bits + 96 aux vars; ~5 samples -> square-ish quadratic system (~600 vars) -- F4/F5 territory with no Sage/Magma-class engine on this host (fpylll F4M at that size hours+; run 1 hit the pip/python f4py mismatch). Without H, E is INFORMATION-THEORETICALLY HIDDEN: the alternate-world kernel (identifiability_check.py, numerically verified, 3 trials, dims stable 64->32) shows E' = E XOR Delta is consistent with the whole transcript for Delta in the operation-type subspaces (u2-chain on s1 -> Delta in (H+1)^-1 V; on s0 -> H^2(H+1)^-1 V; u1-pair on s1 -> HV; on s0 -> H^2V): two operation types leave a 64-dim (2^64-candidate) ambiguity in E, three/four types 32-dim -- no strategy over short transcripts can beat ~2^-32. With H known, branch coins become detectable (32-bit V-membership) and diverse operation types shrink the kernel toward {0} (run-1 note: needed a ~16-long known-path chain).

## What has been ruled out and why
- Canceling the fresh blocks by any linear combination of tags while keeping E: every u1/u2 injects a fresh uniform V-block; any E-free combination still carries a fresh block times a power of H.
- Transcript-only strategies without H: the alternate-world construction above -- a theorem about the tag algebra, independent of the transcript, so no further live sessions are needed (verdict provable offline; respected no-hammering: <=1 session/attempt class in run 1, 0 new sessions run 2).
- Server-side degeneracies (run 1, probes runnable): server matches chall.py exactly; current-state tag and "0"*32 rejected at the final prompt; per-connection salt/key/nonce (cross-session reuse ruled out); no error/traceback channel; silent close on wrong final answer.
- NOT executed (out of budget, the only remaining door): F4 Groebner solve of the H-membership system in Magma/Sage-class tooling, and joint (H, branch-path) disjunctive solving.
- Failed attempts ledger: 2 solver runs, zero flags, nothing submitted (a guessed flag would be rejected and is disallowed).

## Sources
chall.py (server source); statement.txt/site.md; probe1-3.py live probes (run 1, incl. md5 PoW solver); identifiability_check.py (this run's self-contained GF(2^128) kernel-dimension check, no deps). Standard reference named in AAR: McGrew-Viega GCM spec (for GHASH structure). Did NOT consult /solutions/, /solves/ or writeups per SOLVER_BRIEF; all math self-derived.

## RUN section 2026-11-02 (SAT pricing) — append-only
- Built SAT mirror of the largest on-disk H-membership instance: challenge-317 b4true.in
  (512 quad vars = h0..h127 + 4 samples x 96 aux coeffs; 1024 quadratic eqs) -> gcm_b4true.cnf
  (208,256 vars / 728,128 cl, msolve2cnf.py, load 1.1 s into pycryptosat 5.17) and ran
  arsenal/gcm_sat.py (confl_limit chunks of 2M, CAP 6600 s, witness auto-verified against ALL
  1024 polys; h_i = DIMACS var i+1). Status at handoff: RUNNING (chunk 1); no H-model, nothing
  submitted. Exit codes: 0=SAT+verified model (gcm_b4true_Hmodel.txt), 2=UNSAT, 3=cap UNKNOWN.
- Honest gaps: (1) wall-map target is the REAL >=1024-var system; it needs live u1-pair tag-xor
  samples and model.membership_pols k=2/k=3 (not coded) — not built; no live session opened
  (loop-guard; E remains info-theoretically hidden without the connection's H). (2) Even a valid
  b4true model is synthetic-H throughput evidence only — the H-member -> digest -> flag chain
  in "Current state" is per-connection and unrunnable offline.

## CONVENTION-FIX RETEST 2026-11-06 (corrected-witness re-timing, nn=263 follow-up)
Prompt: progress.json VALIDATION/WITNESS-BUG note (2026-11-06) — membership_pols bit-reversal
convention; re-run engines on the CORRECTED system before citing old bounds. (Dispatch-named
files membership_pols.py/planted512.py/m4gb_planted_test.txt do not exist; real artifacts are
317-folder `model.py`, `m4gb_prep.py`, `m4gb/`. The "6438 s @320" figure has NO backing in any
disk artifact or session history — recorded envelope was U1=3.4 s / killed@90 s; only numbers
below (measured this run) are citable.) All offline, live service untouched; scripts + instances
in 317 `m4gb/convention_fix_retest.py`, `m4gb/retest_timing.py`, `m4gb/retest/`.

**Witness verification (corrected convention, semantic):** on-disk controls planted320/416/512
evaluate to **0/256, 0/384, 0/512** violations at their recorded roots ⇒ the 2026-11-05 M4GB
boundings ALREADY ran on corrected-witness systems; "old bounds may have used the wrong
convention" is disproved for the M4GB family. Fresh regenerated corrected systems (seeds
2026110601/2): 0/256 and 0/512; wrong-convention twins violate 127/256 and 254/512 (per-constraint
61–67 of 128) — reproduces the historical 263/512 exactly.
**msolve small-dim end-to-end gate (f-pinned, 224 vars):** corrected system ⇒ msolve recovers the
planted H_field **exactly** in 0.32 s; wrong-convention twin returns **reflect128(H_field)**
exactly (convention flip demonstrated). Sweep: 6/6 random-H corrected gates MATCH, every root
semantically verified (all polys vanish). Gate also exposed a **latent live-run blocker**:
`run_h_solve`'s parametrization parser did not match msolve 0.11.0 output and returned a NON-ROOT
H — silently, because every real-size run timed out before output. Fixed in `model.py`
(`param_root_011` decoder verified on all 4 two-var roots + 3-var case; `run_h_solve` now
semantic-verifies candidates, new VERIFY-FAIL status).

**Re-timing (15 s alarm, 120 s/cap, 1.8 GB RSS guard, kills own child only, 16 cores):**
| engine | instance | result |
|---|---|---|
| M4GB n320 | corrected fresh 320 (256 quad) | 15 s: KILLED-MEM @6.0 s (3.23 GB), U1=3.53 s, then lcmdeg-3; 120 s: KILLED-MEM @5.3 s (3.41 GB) |
| M4GB n320 | old on-disk 320 | KILLED-MEM @5.5 s (3.46 GB), U1=3.42 s — identical to fresh |
| M4GB n512 | corrected fresh 512 (512 quad) | 15 s: KILLED, first update NOT reached; 120 s: KILLED-MEM @33.3 s (1.91 GB), U1=30.73 s, lcmdeg-3 |
| msolve -t 2 | corrected fresh 320 | KILLED-MEM @8.3 s (1.89 GB), no result |
| msolve -t 2 | corrected fresh 512 | KILLED-MEM @7.3 s (1.78 GB), no result |

**VERDICT — door stays subalarm-budget-open, unchanged by the fix.** Corrected-convention solve
is NOT <15 s: at 512 vars the first linear-algebra update alone (30.7 s ≈ old 30.1 s) exceeds the
alarm; at 320 vars the lcm-degree-3 selection demands >3.2 GB within ~6 s, violating the <2 GB
host rule before anything closes; msolve hits the memory wall at ~8 s. Timing invariance vs the
old convention (U1 within 2%) is expected: the bit convention only relabels WHICH root is
planted — system shape (and hence engine cost) is convention-independent. No live ~40 s u1-pair
stream: it would produce a transcript the offline solvers cannot exploit inside any per-connection
budget; the ≥1024-var k=2/k=3 formulation remains further out than anything measured here.

**Banked lesson:** test the witness BEFORE timing the engine — engine cost measured on a system
the target never defined is fiction. Symmetric half discovered this run: a verified INPUT is still
not enough — gate the whole pipeline end-to-end on a SMALL planted solve (planted root in ⇒
recovered root out, semantically checked); ours was broken at the OUTPUT parser for three runs and
only a 224-var planted solve would have (did) catch it. Convention ≠ complexity: re-timing under a
witness relabeling cannot move an engine wall; budget goes to formulation/structure, not re-measurement.


## THREAD/RAM SWEEP 2026-11-06 (parent) — door stays OPEN; next move = owner-priced RAM exception
Extending the retest (whose wall was MEMORY at 320 vars): knob sweep on 320-var corrected instance
(retest/planted320.m4gb / .in), self-kill guards, host jobs otherwise idle-compatible:
| config | peak RSS | when | note |
|---|---|---|---|
| M4GB n320-build nt=16 (default) | 3.23-3.46 GB | ~6 s (rising) | retest child's number, reproduced |
| M4GB nt=8 | >2.2 GB | @5.0 s (2.46 shown) | self-killed at 2.2 GB guard |
| M4GB nt=4 | 3.11 GB | @5.3 s | |
| M4GB nt=1 | 20.18 GB | @15 s (rising) | threads PARTITION memory; fewer threads = WORSE |
| msolve -t 2 | 1.89 GB | @8.3 s (rising) | retest child |
| msolve -t 1 | 2.22 GB | @11.3 s (rising) | this sweep |
Verdict: NO engine configuration fits the standing <=2 GB/proc host rule at 320 vars. The
monotone thread->RAM curve says the honest requirement is ~4-6 GB for a ~20-30 s one-shot solve.
ARMED NEXT MOVE (owner decision, priced): one-time RAM exception — M4GB nt=8 on 320-vars,
6 GB hard self-kill, 30 s window, one call; if it solves, the live route (collect u1-pairs ->
offline solve, no per-connection alarm) reopens. Without the exception the door stays OPEN but
no-compute. Banked lesson: on dense F4 engines, thread-count is a MEMORY knob that moves the
WRONG way for conservation — reducing threads conserves cores, not RAM.

## RAM-EXCEPTION RUN 2026-11-06 (owner: "you have ram to run") — M4GB build defect-class finding
Free RAM at launch: 24.8/64 GB. Owner-authorized ceiling probes, then owner lift; M4GB n320-build,
nt=16, planted320.m4gb: RSS is a STEP, not a curve — 0.91 GB flat through the U/M sparse phases,
then at the lcm-3 dense switch: 6.75 GB @ ~6 s, 14.6 GB @ 7.8 s, 40.3 GB @ 36 s and STILL GROWING
(no plateau; would exceed the box and evict the fleet — killed at 40 GB guard).
Corrections to this AAR's earlier numbers: the "3.23-3.46 GB @ ~6 s" and nt=1 "20 GB (rising)"
figures were SELF-KILL truncations at whoever's guard value — they understate the explosion badly
and must not be used for pricing. The n12 build parse-fails 320 vars (maxvars); the generic
solver_m4gb.exe silently no-ops (loads polys, exits rc=0, zero output) = third Windows-build defect
on this binary. VERDICT: this host's M4GB build (internal bitslicing, no m4rie per build skill) is
NOT VIABLE >= 320 vars regardless of machine RAM. Door path = msolve -t 4 under 12 GB/600 s
cap, running now; outcome appended below when it lands.

## FULL-RAM LADDER 2026-11-06 (owner: "use all the ram you need") — machine + engine walls measured
All runs: retest/planted320.in/.m4gb, fleet-safe guards (kill at RSS>40-52GB or machine-free<3GB),
msolve -t 8 unless noted. Result matrix:
| run | config | outcome |
|---|---|---|
| M4GB nt=16 | no cap attempted past free | 40.3 GB @ 36 s, NO plateau, killed |
| msolve | -t 8, 52 GB cap | 41.4 GB @ 633 s, killed |
| msolve | -t 8, machine-wall guard | 46.6 GB @ 633 s, free hit 1.8 GB, killed |
| msolve | -m 8000 (pairs/matrix) | 37.2 GB @ 1992 s, still growing — chunking DELAYS, does not bound |
| msolve | -l 44 -q 1 | ENGINE DECLINES: "characteristic is too low for probabilistic linear
  algebra — option set to 2". The memory-bounded block-Lanczos path is mathematically
  large-characteristic-only. On GF(2) this msolve build HAS NO bounded-RAM variant. |
deg-3 matrix measured: 131,328 x 3,981,633 at 0.01% density (65 GB as pure bitmap; lazy-dense
always eventually wins the race on this design).
VERDICT: solving 320-var GF(2) at this shape on a 64 GB workstation is CLOSED BY HARDWARE+ENGINES
(owner's RAM order executed to the last GB; the box answered no). NEXT MOVE = STRUCTURE: with
ncons=2 (more streamed u1-pair sets) the system gets denser; if the shape's degree of regularity
drops to 2, the deg-2 matrix (204 x 19585, 0.7 s, trivial) finishes the solve. Cheap offline probe:
build ncons=2 and ncons=3 planted systems, compare deg-regularity + deg-2 matrix size. If reg-dec
hits 2: LIVE ROUTE = stream more pairs (server alarm governs collection speed, solve is offline).

## STRUCTURAL-ELIMINATION 2026-11-06 — THE DOOR OPENS: inversion-linearization kills the aux blowup
Full offline suite + planted self-tests in 317 `m4gb/structural_elim.py`, evidence
`m4gb/structural/structural_report.json` (+ run.log/run2.log/tail.log, probe_seed10.py). No live
contact this run; every engine call < 15 s, < 2 GB.

THEOREM (verified 400/400 vs model.in_HKV oracle): membership "Z in H^k V" (V = 96-dim zero-padded
blocks, Z known, f existential) becomes, under the birational substitution y = H^{-1}, the LINEAR
system bits_{0..31}(Z·y) = 0 for k=1 (rows of P·T(Z)), and bits_{0..31}(Z·y^2) = 0 for k=2 — linear
via Frobenius: y^2 = SUM_j y_j·e_j^2, cross terms die in char 2. Elimination over GF(2)[h] in the
"matrix condition" sense: M(h) = T(h)|_V has rank 96 for ALL h != 0 (field injectivity, 200/200
checks), so consistency Z in colim M(h) = vanishing of the Fitting ideal I_97([M(h)|Z]) — degree-96
generators, still dead — but the h -> 1/h substitution collapses all of it to 32 LINEAR rows per
block. The F4 wall (512 vars, reg-deg 3, 131,328 x 3,981,633 matrix, 40-65 GB) was the shape of the
(h,f) formulation, NOT of the problem; the aux vars are eliminated exactly by inversion, in KB of RAM.

PLANTED EVIDENCE (k=1, same H_field per stream, convention_fix_retest builder + eval_poly verifier):
24 seeds: kernel dim ladder 96 -> 64 -> 32 -> {1..3} -> 1; first-unique N: 4 -> 16/24, 5 -> +6,
6 -> +2 = 24/24 unique by N=6; recovered h and recovered f's give 0/1280 violations in the ORIGINAL
planted bilinear system (semantic end-to-end). msolve on the eliminated h-only system (128 linear
h*y*=1 + 128 Boolean, 128 vars) returns the planted H_field EXACTLY in 0.17 s (5 blocks, rank_y=127)
while the same 4 blocks in the original 512-var bilinear form reproduce the >14 s wall (AAR numbers
confirmed). Honest negatives: msolve -t2 on the 256-var h+y linear+bilinear hybrid TIMEOUT >14 s —
[flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt] IS the solver here; no Groebner engine is wanted or needed.

STRUCTURAL FINE-PRINT (measured, banked): near rank saturation stacked blocks CAN be dependent
(SUM_c Z_c mu_c = 0 with mu_c supported on the 32-bit V-complement), so N=4 is the 2^0 borderline:
kdim 2-3 (3-7 legitimate candidates!) at N=4-5 happens for ~1/3 of streams (seed 20261110: kdim 3
through N=5, unique at N=6). Protocol must be ADAPTIVE: collect until kernel dim == 1, never fix N.
Limit structure closes the book: {y : V·y subset V} = {0,1} (rank 127, dim 1) — infinitely many
blocks provably isolate y*, recovery-by-collection always terminates.

LIVE RECIPE (offline-validated; live route = collect in ONE connection, solve offline, no per-
connection compute at all):
0) Convention fix (offline pycryptodome probe, own key): u1/u2 tag-deltas are DT = delta·H^2 on the
   CT slot and delta·H^3 on the AAD slot — identifiability_check.py's "HV / H^2V" labels are shifted
   one power (its kernel-dim conclusions are invariant under the uniform H-shift, stand unchanged).
1) One connection (alarm(20) = 20 s wall-clock; PoW once): `tag`, then repeat [`u1`,`tag`]; each pair
   gives D_i = T_i xor T_{i-1} = fresh-uniform delta_i · H^{k_i}, k_i in {2,3} (slot coin hidden).
   u1-only keeps the length block constant. m = 12 pairs = 25 commands (ms server-side; fits the
   wall-clock budget; m=20 = 41 commands as headroom).
2) Offline: DFS over pair-type assignments (k=2 adds 32 linear rows; k=3 adds none), prune at kernel
   dim 0; at dim 1 test the unique nonzero vector against ALL remaining pairs and prune; enumerate
   leaves with dim <= 8; SEMANTIC disjunctive filter (D·y^2 or D·y^3 in V, every pair); unique
   survivor y* -> H = y*^{-1} by field inversion. Sim results: k in {2,3} m=12: 11/12 exact (sole
   miss = coin ran only 3 linear pairs: FAIL-OPEN = zero candidates, never a wrong H); m=20: 4/4;
   control k in {1,2} m=12: 6/6. Seconds-to-minutes of pure linear algebra, KB RAM.
3) With H known the branch coins become detectable (32-bit V-membership tests) and the run-1 design
   (known-path chain ~16 steps, E-kernel -> 0) extracts E = flag. THAT last stage is the only link
   this run did not re-verify — everything upstream of it is planted-proven.
Pairs needed vs alarm budget: k=1 corpus: median 4, max 6 (24 seeds). Live k in {2,3} mixed: 12
pairs -> 92% single-shot, 20 pairs -> ~99.9% (failure only if <4 of 20 coins land CT; adaptive
top-up in the same connection, then new connection if needed — H is per-connection so pairs never mix
across connections, which is also what makes each solve self-consistent).

WHY THIS BEATS THE FULL-RAM LADDER VERDICT: "box answered no" priced the WRONG system. Same variety,
projected onto h via a rational change of variables, is a rank-127 GF(2) matrix. The F4/M4GB wall
survives as a true theorem about the bilinear formulation (worth keeping above as history) but is no
longer on the attack path.

BUG-CLASS LESSONS (banked to groebner-mq-toolkit): (a) GF(2) nullspace basis must use the
pivot-BITS-only vector (v = e_jf + sum of pivot-column units where piv[i]_jf = 1); XORing whole RREF
rows silently produces NON-kernel vectors (passes ~50% of nodes, corrupts kdim silently) — caught
only because candidates were re-checked against the original rows and against the field-membership
oracle. Verify kernel bases semantically before trusting any "degenerate seed". (b) A persistent
kdim > 1 claim needs a rows_ok witness per candidate, not rank arithmetic alone.

## PARENT VERIFICATION 2026-11-06 — independent fresh-seed reproduction CONFIRMED
Parent re-ran live_route_sim with seeds NOT in the unit's 24: 555000 (m=20): 6/6 exact, mean 36.1 s;
313131 (m=12): 8/8 exact, mean 4.0 s. Note: dfs_solve is validated for mixed k in {2,3} live-slot
streams; single-slot k=1 sims return out-of-semantics candidates (parent probe, documented so the
next reader doesn't false-alarm). Door status: OPEN, offline core PROVEN; LIVE route dispatched
(m=12 -> escalate m=20, one-connection budget; post-H E-extraction = last unverified link,
synthetic-gated before live).

## E-PHASE CLOSE-OUT 2026-11-06 (parent) — win-check corrected; coin-luck retry plan armed
1) WIN-CHECK SEMANTICS (source chall.py, resolved the run-1 'current-state tag rejected' mystery):
   final answer compares against new().digest() on an EMPTY cipher = E = AES_K(J0) itself — NOT the
   current-state tag (which is GHASH(s)^E). Run-1's probe submitted a state-tag -> rejection expected.
   E is uniform 16 bytes: NO ASCII/printable gate on E is possible (a prior synthetic gate used one
   — invalid criterion, discarded before any live use).
2) RANK STRUCTURE (offline, SimAES ground truth, run_group true-coin path, u1x12 prefix):
   u2-only tails saturate FAST: tail=20 and tail=26 give IDENTICAL per-seed ranks (126/127/128);
   rank is fixed by the realized COIN SEQUENCE (which slots absorb bytes / repack patterns), not by
   tail length. u1 in tails DESTROYS identifiability (each u1 orphans all prior tags' byte-vars ->
   rank collapses toward the initial-state kernel ~32: measured 32-66 for u1-heavy tails).
   => tactic: pure-u2 tail (~26), answer ONLY when leaf rank==128; per-connection success = coin
   luck, measured P below; retry across connections is the lever. Every abort is a socket close
   WITHOUT answering (runner fails closed; server just ends).
3) live_run.py (challenge-317-code dir): PoW(md5) -> 12 u1-pairs (H-phase, dfs_solve in a THREAD
   overlapping the tail) -> 26 u2+tag pairs -> coin-DFS (unique leaf) -> answer iff solve_E int.
   Provenance: y=H^-1 elimination self-derived in-campaign; coin-detection & system semantics
   mirror model.solve_E (run-1 extraction from real server source); no external writeup consulted.

## LIVE-ROUTE EXECUTION — 2026-11-06 (SOLVED, flag submitted)

**Outcome.** Solved on the structural-elimination route; flag submitted via
`submit_flag.py greatest_common_multiple-code` → server-side solved 307→308.
Flag (verbatim from service): `[flag — recorded in FLAGS/ctf-archive/challenge-10-cryptohack-greatest_common_multiple-code/flag.txt]`
(the `...` is literal flag prose — log repr terminates cleanly).

**Chain (all links now live-verified).**
1. PoW (pre-session, ~55 s local) → `tag` + 12×(`u1`,`tag`) → u1-pair tag-xors D_i.
2. `structural_elim.dfs_solve(Ds, ks_allowed=(2,3))` → unique H (live attempt 1 recovered
   `fea5f6a745aa9b7d571becf286010435`, self-checked H²=0-bytes on x²-reduction).
3. `detect_coins_u1` recovers the 12 hidden u1 slot-coins from the *same* pairs (membership).
4. 26×(`u2`,`tag`) + adaptive `u1`,`tag` → `Gsys` coin-path DFS over 27 free coins with
   per-tag consistency pruning → unique transcript path; E determined iff rank(E-rows)=128.
5. Answer only when rank==128 (fail-closed otherwise — every sub-128 session was closed
   unanswered; 0 wrong answers ever sent).

**New measurements this session (record, not folklore).**
- **Session alarm ≈ 30 s wall** from PoW-success, hard: alive-prompt observed at t=28.9 s;
  ConnectionAborted at t=34.7 s. Collection (~7.5 s) + solve + answer must fit ≈ 30 s.
- **`powH` recomputed H^e from scratch per node** → leaf-DFS 50.8 s. Memoizing `powH` per-H
  table + global `gmul` pair-cache in `model.py` (pure memoization, values identical):
  **50.8 s → 2.87 s (17.7×)**, same leaf, exact E-match on planted seed. This made in-session
  answering fit the alarm. All 4-worker tree-split attempts confirmed the DFS is
  Amdahl-serial under pruning (frontier collapses); node-cost, not parallelism, was the lever.
- Live leaf ranks on 12 fresh sessions: 127×6, 125×3, +1 determined(=128) hit; H-phase once
  returned 0 survivors (retry). Offline P(determined)≈2/16 base + adaptive-u1 rescue 1/16
  (never rank-negative in 16 trials) ≈ 19%/attempt; flag landed on attempt 7 of final loop.
- Flag-format trap: service prints the flag prefixed `tag: ` in namespace `codegate2024{}`;
  the platform slug is `greatest_common_multiple-code` (submit to that slug).

**Protocol fixes that the first live attempts paid for.** Read-until-`tag` discipline
(timed-window recvs raced the prompt; use `recv_tag` hard-deadline loop), 50 ms pacing
between op and tag lines, tolerant tag regex `[0-9a-f]{32,128}`, H-thread start moved after
phase-A collection (it raced tags[] fill), `fixed` list sized from `len(spec)` post-adaptive.

**Provenance.** Self-derived. The y=H⁻¹ pairing trick, coin-path DFS, and rank-gate design
originated in this program's own AAR sessions (structural-elimination 2026-11-06); external
sources cited remain only the lineage already banked (Joux–Stern toolbox; FHKLS truncated-LCG).
No third-party writeup consulted for this challenge. Flag string is service-given verbatim.

**Verdict (milestone, not closure — owner closes).** Challenge mechanism: recover H from
u1-reset tag-deltas (truncated-LCG class), recover per-op slot coins by membership, then the
tag stream is linear in E over GF(2) — E becomes determined exactly when the coin-path
transcript yields rank 128; that event is coin-luck (~19%/session) and is bought with
connections, not compute. Remaining theoretical gap (unverified, not needed to solve): closed
form for which coin-sequences hit rank 128.
