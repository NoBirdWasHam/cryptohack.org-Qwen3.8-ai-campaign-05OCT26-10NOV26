# AAR — challenge-323 spongebob_squarepants__battle (CryptoHack / HTB Cyber Apocalypse crossover)

## Game (server-verified)
- Statement: "Wait, `spongebob` and `squarepants` don't hash to the same thing?" — `archive.cryptohack.org 37916`.
- Protocol: prompt → hex line a → hex line b. Server runs the provided file verbatim
  (traceback line numbers match); wants `a != b` and `H(a) == H(b)` → prints FLAG.
- Local `spongebob.py` md5 == `4bf92623d1ebd0c31eb94f70b824328c` == downloaded file hash. VERIFIED byte-identical.
- No input trick: length assert is live server-side (tested: odd-length hex → AssertionError traceback).

## Cipher
Sponge: 18-byte state, INIT fixed, rate 8 (XOR into bytes 0..7), per block 8 rounds of
(permute: bit b of byte i → bit b of byte PBOXES[b][i], rows all permutations ⇒ bijection; then byte SBOX).
Output = FULL 18-byte state. SBOX random (DDT max 12, no AES-like structure); backward cones full in 1 round ⇒ no
invariant/free-lunch truncation (probe.py: linear rank 80/80 on capacity, 144/144 full state).

## Attack (derived)
R bijective ⇒ 2-block collision: H(m1‖m2)=H(m1'‖m2') ⟺ s1[8:18]==s1'[8:18] and m2' = m2 ⊕ s1[:8] ⊕ s1'[:8]
(m2=0). I.e. birthday on the 80-bit **capacity** of the post-block-1 map f: {0,1}^64 → {0,1}^80.
Wall ≈ 1.4·2^40 evaluations (any 2-block/capacity-equality formulation). No preimage shortcut exists (output=full state).

## Implementation
- `gen_tables.py` → `tables.h` (generated, no hand-typed tables — avoids prior unit's PBOXES IndexError trap).
  SPREAD[i][x] = 144-bit bit-placement table; T1[i][x] folds INIT^m into round-1 permute; C0_* constants.
- `fast.c`/kernel `cap_of_m`: reduced final round (only capacity bytes SBOXed). **Matches python H exactly**
  (full-state + capacity vector 1122334455667788). 6.1–6.6 M/s/core vs prior unit's 2.66.
- `walker.c` — VOW parallel Pollard-rho (van Oorschot–Wiener) on G(x)=cap(x) over 80-bit states,
  16 pthreads, DP criterion (lo>>40)==0, shared open-address DP table (2^24 slots, mutex), stores the m that
  produced each DP; hit from a different walk with different m ⇒ cap collision; found_pair recomputes both caps
  (full kernel) before writing `found.txt` (`m1 m2 cap_lo cap_hi` hex).
- `harvest.py` — reads found.txt, rebuilds `a = m1‖0`, `b = m1'‖(s1[:8]^s1'[:8])`, verifies H(a)==H(b) with the
  real python H, then socket exchange and auto-submits via ../submit_flag.py. Toy pipeline test (walker 20 =
  truncated 20-bit cap) passed: detection, false-pair rejection, output file, harvest guard all verified.

## Status at handoff
- Production hunt RUNNING in background: `./walker.exe > hunt.log && python3 harvest.py` (auto-submits on find).
- Throughput measured: ~51.3 M/s aggregate (16 thr, Ryzen 5800X3D). `hunt.log` progress lines every 60 s
  (`steps=… (x.xx%)`, 100% ≈ 1.37e12 steps ≈ ETA ~7.5 h from start).
- On success: `flag.txt` + submit result appended to `hunt.log`.
- Manual finish if hunt already done: `python3 harvest.py` (with found.txt present), or
  `cd .. && python3 submit_flag.py spongebob_squarepants__battle '<flag>'`.

## Files
walker.c/.exe, fast.c/.exe, bench4.c, gen_tables.py, tables.h, harvest.py, live_probe.py, probe.py,
real_spongebob.py (downloaded, md5-matches), hunt.log. Prior-unit files kept (rho.c, rho_kernel.h, tv.c, solve.py —
solve.py was wrong: it XORed 18-byte diffs as m2', violating the 8-byte rate).

## Lessons
- Server == challenge file (asserts live); fingerprint by triggering a traceback, but don't infer bypass from line
  text — re-verify the file by hash.
- For "full-state output" sponges: capacity birthday / parallel-rho is the ONLY collision route; the rate XOR gives
  exactly 8 free bytes and no more.
- Rho for functions: iterate over states padded to |Y| (here 80-bit) so a cycle merge IS the collision; DP rate 2^24.

## DIAG 2026-11-01 — hits=344k / fires=0 anomaly: ROOT CAUSE = invalid walk construction (rho over folded 64-bit state), plus one latent harvest bug
### Verdict per hypothesis
- (a) hit-VERIFICATION bug: **NOT in C path** (found_pair recomputes exact caps; consistent convention). **BUT harvest.py had a real latent bug**: rebuilt messages with `to_bytes(8,'big')` while the C walker's message convention is little-endian → a real found.txt would have died on its own `capacity mismatch` assert. FIXED (little-endian). Byte-level proof: C cap `55af512f9fdc91cb:48f5` == python `H(m.to_bytes(8,'little'))[8:]` == `cb91dc9f2f51af55 f548` (LSB order).
- (b) hit-DETECTION over-report: **symptom, not bug**. Keys are the EXACT 80-bit capacity (DP ⇒ lo>>40==0 ⇒ keylo|0xFFFFFF.. holds full cap) ⇒ false different-m hits impossible. All 344,367 hits were same-state re-encounters (wid==wid self, or cross-walk same-m): correctly not fired.
- (c) capacity model: **correct**. 2-block collision ⟺ full 10-byte post-block-1 capacity equal, m2'=d=s1[:8]^s1'[:8]. C kernel == python H slice verified byte-for-byte.
### Root cause
Walker iterated the FOLDED map m ↦ cap_lo(m) ⊕ cap_hi(m)<<48: {0,1}^64→{0,1}^64 (state kept 64-bit; hi folded in). A random mapping on 2^64 ⇒ every walk μ+λ≈1.25·2^32 ≈ few·10^9 steps then cycles forever; 16 walks on ONE random mapping merge onto shared cycles (VOW-over-X is only valid when |X|≥|Y|; here |X|=2^64≪|Y|=2^80 ⇒ birthday on Y is unreachable by functional-graph walks over X — coverage plateaus at ~W_eff·2^32 ≈ 2^35, needs 2^40).
### Evidence
- hunt.log: ins=345,873 ≈ steps·2^-24 ✓; distinctDP=ins−hits≈1,506 FLAT from 11% to 418% ⇒ all work after ~6 h was cycle re-traversal. Distinct coverage ≈ 1,506·2^24 ≈ 2.53e10 messages ⇒ P(collision)=(2.53e10)²/2^81 ≈ 2.6e-4. **fires=0 was mathematically expected; steps metric was the lie — the 2^40 ETA number itself was fine.** Asymptotic P even at infinite runtime ≈ 0.03%.
- walker_dbg.c (instrumented, NT=2, hit-reason counters): at TEST_BITS=22/20 reproduces pathology at tiny scale: distinctDP stuck (4176/2189), hits→100% self, fires=0. Original toy (NT=16, TEST_BITS=20) fires only because 16 chains collide in the 2^20 subspace; at NT=2 they miss (disjoint small attractors) — toy pipeline test at 20 bits still validates found_test write + rejection guards (found_test.txt pair from 10-30 run: m=…00000000000fafed/…00000000000660fd, both <2^20 ✓).
- diag_small.c (FIXED construction at small scale): random SAMPLING, K=2^17, reduced 24-bit match: 493 hits, 493 different-m, 493 accepted by recompute-verify, 0 same-state revisits, 0 full-80-equal (production FP rate = 0 by key exactness). PLANTED: m1=fa03f6b467c480b7 m2=c7e738fb956c7237 (caps share low-8-bits-of-lo+hi). ⇒ table+hit+verify pipeline ACCEPTS real pairs when coverage exists.
- brent.c (cycle length of folded map, seed 12345): see brent_1.log (running at append time; μ+λ expected ~1e9–1e10).
### Fix (built, smoke-tested, NOT relaunched big)
walker2.c: random-sampling birthday (splitmix64 per-thread, seed mixed with stack addr — NOTE: first smoke had a self-inflicted bug: thread seeds offset by exactly the splitmix golden-ratio increment ⇒ thread1 replayed thread0's stream ⇒ hits=reinsert=17 same-message; fixed). NT=2 smoke 60 s: 5.16e8 steps, ins=35≈steps/2^24, hits=0, reinsert=0 ✓. Fire rule now `different m` (wid ignored; old code dropped same-wid different-m hits — negligible probability but wrong). DP 2^-24, table 2^24 (8.2e4 DPs at full ETA — ample). found.txt format + harvest unchanged except endianness fix.
### Revised realistic cost (sampler, correct construction)
- Required: median ≈1.21e12 evals (50%), ≈7.4 h @51.3 M/s(16 thr) / ≈44 h @NT=2 (8.6 M/s measured). P success = 1−exp(−k²/2^81).
- Do NOT relaunch big hunt this session (host-load rule). Files: walker2.c/.exe (hunt candidate), diag_small.c/.exe, walker_dbg.c/.exe, brent.c/.exe, brent_1.log, brent_2.log.
### brent cycle measurement (folded map, folded 64-bit state map)
Two seeds ran Brent's algorithm; both terminated mid-μ-phase (no DONE; host-quiet). Last λ-doubling windows: seed12345 lam=2.05e9 @1.06e10 evals; seed987654321 lam=9.3e8 @5.2e9 evals. Order of magnitude confirms the random-mapping prediction μ,λ ≈ 1–3·10^9 ≈ 2^32-scale — i.e. each 64-bit folded-map rho walk closes its cycle after ~2–4e9 steps, matching the observed distinctDP plateau (≈1,506 DP keys ≈ 2.5e10 distinct messages ≈ 16 walks' merged tails). Conclusion unaffected: the walk, not the verify stage, is the anomaly.

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## The challenge (plain words)
The server runs the provided `spongebob.py` hash verbatim and prints the flag for any two distinct hex messages with equal digests ("spongebob vs squarepants"). The sponge has an 18-byte state, rate 8, a bit-permutation + random-SBOX (bijective) round, and outputs the FULL 18-byte state after absorbing two blocks. Because the round map is a bijection and nothing is hidden at output, there is no preimage or truncated-differential shortcut: collisions must come from the 80-bit **capacity** — a birthday search for `f: {0,1}^64 -> {0,1}^80` (post-block-1 capacity), where the second message absorbs the rate difference as `m2' = s1[:8] XOR s1'[:8]`. Expected cost ~ 1.2e12 hash evaluations (birthday on 2^80).

## Current state of the attack
**OPEN — unsolved, hunt NOT running.** The end-to-end pipeline is built and stage-verified: C kernel hasher byte-matches the python H (6.1-6.6 M/s/core, ~51.3 M/s at 16 threads), harvest/verify/submit chain works after a real endianness fix, and the plant-test `diag_small.c` proves the table+hit+verify machinery accepts genuine pairs whenever coverage exists. What stopped the production hunt was **coverage, now root-caused** (see DIAG): the original walker ran Pollard-rho over the FOLDED 64-bit state `m -> cap_lo(m) XOR cap_hi(m)<<48`, a random mapping on 2^64 — functional-graph walks on 2^64 cannot birthday a 2^80 range; every walk cycles at ~2^32 scale, distinct coverage **plateaued at ~1,506 DP keys ~= 2.53e10 messages** (P(collision) ~= 2.6e-4; the observed fires=0 was mathematically expected and the steps-metric was the lie). The replacement `walker2.c` — random-sampling birthday (splitmix64 per-thread streams, DP 2^-24, fire-rule = different-m) — is **built and smoke-tested** (NT=2, 60 s: 5.16e8 steps, ins ~= steps/2^24, reinsert=0). Cost model for launch: median ~= 1.21e12 evals ~= 7.4 h at 51.3 M/s (16 thr) or ~= 44 h at NT=2 (8.6 M/s measured); P(success) = 1 - exp(-k^2/2^81). NOT relaunched per the host-load rule (>5-min sustained CPU needs the two-job budget); brent_1/2.log confirm the folded-map cycle lengths (mu,lambda ~ 0.9-2.05e9) behind the plateau.

## What has been ruled out and why
- **Input-format tricks / assert bypass**: the server == the provided file (traceback line numbers match; local md5 4bf92623d1ebd0c31eb94f70b824328d byte-identical to the download); odd-length hex raises AssertionError live, so the length check is real.
- **Preimage / invariant / free-lunch-truncation routes**: output is the full state (no hidden bytes to grind); backward cones saturate in 1 round; linear rank 80/80 on capacity and 144/144 on the full state (probe.py) — no exploitable structure in the random SBOX (DDT max 12) or the bit-permutation.
- **Hit-verification bug (DIAG hypothesis a)**: cleared — `found_pair` recomputes exact capacities before firing; all 344,367 hits were same-state re-encounters (correctly rejected). The real bug found there was harvest.py's big-endian message rebuild vs the C little-endian convention — fixed with byte-level proof, so a future found.txt cannot die on its own capacity assert.
- **Hit-detection over-report (hypothesis b)**: impossible to false-fire — DP keys carry the exact 80-bit capacity; the hits=344k/fires=0 pattern was a symptom of the construction flaw (c), not of detection.
- **The folded-rho construction itself**: invalid because VOW-style rho over X needs |X| >= |Y| (here 2^64 << 2^80); measured with Brent (two seeds), instrumented small-scale runs (walker_dbg.c reproduces the plateau at TEST_BITS=22/20), and the 2.53e10 coverage plateau. Asymptotic P(collision) of the old walker even at infinite runtime ~= 0.03% — abandoning it is proven, not a preference.

## Sources
- Self-derived per logs (server-verified protocol, own kernel/walker code, hunt.log/brent_*.log/walker2 smoke data). Named math references: van Oorschot-Wiener 1999 parallel rho (the |X| >= |Y| condition explains the failure mode); birthday median ~1.2e12 for a 2^80 collision space. No writeups/solutions consulted; no flag exists for this folder.
- Upgrade-time note (batch #9, 2026-11-02): plain-words wall-map consolidation from existing AAR/hunt logs only — nothing re-run or relaunched; the `## Status at handoff` section above reflects the superseded pre-DIAG state and is preserved verbatim per append-only rules (walker2.c is the live candidate; the running-hunt sentence there is historical).

---

## EXECUTION 2026-11-03 — capped 4-CPU-h birthday run (unit nn=294): ran, no collision, model intact

### Fresh structural re-verification (this unit, before any compute)
Independently re-checked the "no shortcut" claims against `spongebob.py`: every PBOXES row IS a
permutation of 18, SBOX IS a 256-bijection, 20k random 1-block hashes all distinct (injective).
2-block collision condition re-derived: R8 bijective ⇒ H(m1‖m2)=H(m1'‖m2') ⇔ post-block-1 capacity
bytes 8..17 equal (rate XOR absorbs the 8 free bytes into m2). Longer messages give no better route
(any merge point still demands a full 80-bit capacity match at some boundary). Wall = birthday on
2^80 capacity, confirmed, not assumed.

### Run (budget-capped)
- Server LIVE: `archive.cryptohack.org:37916` answered the prompt line (single connect, no attack traffic sent — no pair to submit yet).
- `walker2.exe 7200` (self-capping), NT=2, one process, `hunt3.log`, chain auto-harvest on found.txt. 60 s smoke first: 8.3 M/s, ins≈steps/2^24, reinsert=0 (healthy profile verified before committing budget).
- **Result: FINAL ins=3941 hits=0 fires=0. No collision, no found.txt, no flag.**
- Measured: ~6.02e10 steps in 7200 s wall × 2 thr = **4.00 CPU-h exactly**; 8.5 M/s aggregate = 4.18e6 evals/CPU-s.
- Budget probability (correct sampler): P = 1−exp(−k²/2^81) at k=6.0e10 → **0.15%** (run consumed 4.4% of the 1.37e12 median; median needs ~1.29e12 = ~86 CPU-h at this rate).
- Zero-hit inference: 0 collisions at k=6.02e10 ⇒ 95% upper-bound excludes effective collision space **N_eff < 1.2e21 ≈ 2^70** — fully consistent with the 80-bit capacity model; no hidden truncation, and confirms the old folded-rho "344k hits" pathology cannot recur under walker2 (its hits=0 is EXPECTED at this k, unlike the old construction where it was structurally unreachable).

### Discovery: a LIVE stray walker2 — do NOT kill, harvest is armed
While checking host load post-run: `walker2.exe` **PID 12492** (this folder's binary — only this challenge uses it), started **2026-11-02 01:52 EST**, sustained 2.0 threads, **237,394 CPU-s ≈ 9.9e11 samples ≈ 77% of median ⇒ P(collision by now) ≈ 33%** (surviving that long has probability ~66% — unremarkable). No checkpoint ⇒ killing it discards 33% outright. It predates this unit (this session started later; my process self-capped and exited with FINAL). Its stdout goes to a dead session's pipe; on fire it writes `found.txt` to its cwd (presumed this folder) and exits — but no harvest chain may survive behind it.
**Mitigation armed (persist_on_release watcher, session proc_ef216a357f76):** every 5 min, for 20 h, scans the site tree for any `found.txt` newer than `hunt3.log` (also catches a stray-cwd drop), copies into the folder, and runs `harvest.py` (re-verifies the collision with the reference python H, then live-exchange + `submit_flag.py` auto-submit). Parent: keep PID 12492 alive; median reached after ~+10 wall-h; if the watcher times out and the stray is still alive, either re-arm the watcher or extend the hunt deliberately.

### Verdict for the ledger
STAYS OPEN (no flag). Not a negative-result wall — the sampler is correct, the run was the honest
4-CPU-h cap, conflict-rate measurement (0 @ 6.0e10, bound 2^70) matches the 2^80 model, and a live
hunt with ≈33% banked probability is still running under an armed harvest chain. Next close path =
that hunt fires (auto-submits), or a deliberate ~80-CPU-h extension decision by the owner.

### Configuration (this execution)
2026-11-03 13:30–16:00 UTC; Windows 11 + MSYS bash; user OWNER; python3 3.10.11; gcc 16.1.0
(MinGW-W64 ucrt); dir `Practice_runs/cryptohack_org/challenge-323-cryptohack-spongebob_squarepants__battle`
(folder 294 does not exist — queue row nn=294 = this folder per its note); walker2.exe (Nov 1 build, verified newer than walker2.c);
network: 1 TCP connect to archive.cryptohack.org:37916 (prompt read only). Files: hunt3.log (full run log).

### Sources (this execution)
Self-derived; no writeups/solutions consulted. Server contacted once for liveness only; no flag obtained, none leaked to these notes.

---

## VALIDATION 2026-11-05 — live-door audit of the running hunt (walker2 PID 24588, hunt_r1.log): CRITICAL — walk is detection-blind (2^24 penalty); harvest unarmed

State at audit (read-only, nothing touched): `walker2.exe 0` running since 11-04 03:10 EST; last log line steps=1.8999e12 = **138.68%** of the log's 1.37e12 marker (true birthday median sqrt(2^81·ln2)=1.2945e12 ⇒ actually 146.8% of true median), 12.7 M/s, ins=120011, hits=0 fires=0 reinsert=0.

### Per requirement {have|missing}
1. **Correct collision target {have}**: collision ⇔ full 10-byte post-block-1 capacity equality + m2'=s1[:8]⊕s1'[:8]; f: {0,1}^64→{0,1}^80; re-derived from walker2.c found_pair + prior server-verified protocol. No shortcut family exists for this shape (full-state output, rank 80/80/144/144, 1-round cone saturation).
2. **Published-technique-family match {have — family confirmed; only this family can apply}**: Daemen et al. *Sponge Functions* / Keccak main doc: expected inner-collision cost 2^{c/2}; collision complexity lower bound min(2^{n/2}, 2^{c/2}) ⇒ exactly 2^40 here (c=80 bits, output 144 bits). The structure-beating families in the same literature (truncated-differential inner collisions with workload 2^{w_min}−r; fixed-key-sponge internal-collision attacks) all need exploitable round trails — ruled out by this cipher's probes (random SBOX DDT≤12, bijective bit-permutation round, no free-lunch truncation). Memory-light published construction at 2^40 = Pollard rho collision search for a function with |X|≥|Y| + van Oorschot–Wiener parallelization + trajectory distinguished points. ⇒ the 2^40 capacity birthday IS the intended path (hours on C/GPU — consistent with live site solve links/solves counts on the card).
3. **Hunt implements that family {MISSING — CRITICAL BUG}**: walker2.c line 78 `if ((lo>>40)==0)` applies the DP filter to the **capacity VALUE** while sampling messages randomly. A true collision is detected only if the shared capacity value itself lands in the 2^-24 value mask (both sides are stored iff masked). E[detected] = k²/2·2^-80·2^-24 = **k²/2^105**, not the modelled k²/2^81. At k=1.9e12: banked P(fire by now) ≈ 2^-23.4 ≈ **1e-7** — the ~640 CPU-h run is worth ~1e-7, not ~70%. Meanwhile E[true pairs already sampled and discarded] = k²/2^81 = 1.49 (P≈77% a collision pair has already been thrown away). fires=0 at 138.7% is bug-implied, not bad luck; this run's expected first fire needs ≈2^52.5 samples ≈ 14 y at 12.7 M/s. Corroboration: ins/steps = 2^-23.91 (mask accepts ✓; +6% over 2^-24 = minor capacity-bit non-uniformity, harmless). The 11-03 unit's "P=0.15%" budget claim was likewise ~1e-12 (same bug, was already compiled in).
4. **Second independent mask = cheap probability doubling? {NO — premise fails}**: value-mask count never changes the k²/2^105 scaling; each extra masked stream contributes its own 2^-24-penalized detections (linear stream factor, still ≥2^24 short of nominal). Detection probability depends on *what gets stored/compared* — the masks are exactly what the bug hides behind. The cheap correct lever is constructional: Pollard-rho on the 16-byte message space X={0,1}^128 (⇒ |X|≥|Y|=2^80, which is why folded-64 and 64-bit-domain walks fail), partition rule G(x)=g_{π(cap(x))}(x) with injective g_i on X, VOW-parallel, DP filter on the TRAJECTORY (valid there, detection-lossless). Achieves the nominal 1.25·2^40 median at 2^24 DP memory; re-aims the banked ~640 CPU-h at a real ~70% (median ≈ 28 h at 12.7 M/s).
5. **Harvest armed on fire {MISSING}**: process tree = bash → `./walker2.exe 0 > hunt_r1.log` only — no `&& harvest.py` chain, and the 11-03 20-h watcher expired ~noon 11-04. If found.txt ever appears nothing runs harvest/submit (no found.txt anywhere now; log has no FOUND line).

### ONE next move
Owner decision (not mine — job live): retire the current run (win prob ≈1e-7, not ~70%) and relaunch with the trajectory-DP VOW-rho construction above (kernel, found_pair verify, harvest endianness fix all reusable), arming the harvest chain in the same action. Do not launch during validation.

## LAUNCH — walker3 trajectory-DP VOW-rho, 2026-11-06 ~10:50 EST

**FILE-NAMING SAFETY RULE (external watcher, applied before launch): production-detection files are named `found_PROD_<n>.txt` only; self-tests write ONLY into `./selftest/`; the harvest chain matches `found_PROD*.txt` exclusively — never bare `found*.txt` — so test artifacts can never trigger live harvest/submit.**

### Construction (supersedes the 11-05 spec rule where it is provably dead)
- VOW'99 §2 requires a random MAPPING with closures = collisions. The literal rule G(x)=g_{π(cap(x))}(x) with injective g_i on X={0,1}^128 is a **bijection** ⇒ no merges ⇒ fires ≡ 0. Control mode 2 (X~=2^24, 20-bit cap~, T=20-bit XOR-shift walk) measured it: **707 M steps → ins=2, hits=0, fires=0** (orbits are also DP-degenerate: the mask essentially never fires on the attractor). Healthy-looking stats hiding zero detection — exactly walker2's failure class.
- VOW footnote-1 form f=g∘cap1 rejected too: |im(cap1)|=2^64 ⇒ closures dominated ~2^63:2^46 by trivial pairs sharing the 64-bit block-1 channel.
- **Production walk: F(x)=g(cap2(x)) over 2-block prefixes** (3-block messages): cap2 = capacity bytes 8..17 of the post-block-2 state, {0,1}^128→{0,1}^80, full image; g injective (c_lo64, c_hi16<<48). Image = the collision space itself ⇒ every rho closure IS a capacity collision; x' = x⊕r2⊕r2' completes the pair to full-state collision H(a)=H(b), a,b 24 bytes (server assert = 8-byte blocks ✓). Trajectory DP mask 2^-24 (detection-lossless), T-blend table 2^24×48 B, VOW restart-on-DP, abandon cap 20/θ (e^-20), NT=2, mutex on table.

### Validation gates (all passed before launch)
- **TV3 kernel gate: 50/50 byte-exact vs python H** (mode 9 vectors, tv3_check.py). Caught two real bugs: (1) block-2 absorb must use SPREAD not T1 (T1 folds INIT into head bytes; re-XORed INIT); (2) TV printer endianness (kernel is self-consistent little-endian via to_bytes('little'), print was word-order).
- **Mode 1 harness (T=20, θ=2^-8): FIRES** at rho scale (~10 DP ins, hits=1, fires=1, rejects=0), writes selftest/found_TEST.txt only. End-to-end hit→traceback→found_pair verify→file pipeline proven.
- **Mode 60-s production smoke (mode 0, full 80-bit, θ=2^-24)**: `SMOKE-DP-CHECK ins/steps=5.4165e-08 model(theta)=5.9605e-08 ratio=0.909 OK` — DP consult rate matches the DP-mask probability, NOT lower (certifies the filter; collision detection itself is certified by mode 1). Rate **6.46 M F/s combined (NT=2)**, ETA_med = **59.1 h**. NB: spec's 12.7 M/s / ~28 h assumed ~2× this per-thread rate; ≤2-thread constraint holds, so honest median ≈ 59 h (table-load effects trim the true median somewhat below the 1.374e12/rate figure).
- harvest3.py negative-test: garbage pair ⇒ `cap2 mismatch` assert before any network I/O ✓.

### Run state
- `bash launch_walker3.sh` (bash PID 21432 → walker3.exe PID 27160), loop: walker3 mode 0 until fire → `harvest3.py found_PROD_<n>.txt` chained IN THE SAME process — rebuilds a,b, re-verifies H(a)==H(b) with reference python, then submits to archive.cryptohack.org:37916 and runs submit_flag.py on success; restarts walk on socket failure. Log: walker3_run.log. -O3 -funroll-loops (faster than -O2 here, unlike walker2's regression).
- Live line at first tick: steps=2.71e9 ins=152 ⇒ ins/steps=5.6e-8 = θ ✓; hits=0 expected (E≈2e-6 by then).

---

## DETECTION SMOKE ASSERTION 2026-11-07 (challenge-294) — PASSED: detector fires planted hits, rejects near-misses; live walker3 completion is detection-trustworthy

### Hit predicate pinned (walker3.c / harvest3.py / launch_walker3.sh, read this session)
- Mode-0 hit: DP point (`mixf(point)&0xFFFFFF==0`) matches an existing table entry on EXACT `(lo,hi)` → traceback → `found_pair3` recomputes cap2 on both merge predecessors and demands distinct 16-byte messages AND full 80-bit capacity equality (`c1lo==c2lo && c1hi==c2hi`) → fire → `found_PROD_<n>.txt` (`y1lo y1hi y2lo y2hi` hex).
- Chain: `launch_walker3.sh` runs `harvest3.py` ONLY on `found_PROD_*.txt` after walker exits rc=0; harvest3 rebuilds `a=y1||0^8`, `b=y2||(r2a^r2b)`, re-verifies `H(a)==H(b)` with the reference python before opening any socket, then flag extract + submit_flag.py. Self-tests write only under `./selftest/`.

### Planted-hit / near-miss probe (zero drift: probe compiles walker3.c VERBATIM via `#define main` rename; run from scratch cwd so every file write lands in scratch/selftest)
`detprobe.c/.exe` (scratch `detprobe323/`) — **19/19 checks PASS**:
- C0–C4 PLANTED HIT: brute-forced capacity-equal pair at 20-bit truncation (m=3193,3025, low20 cap=0x4e61 both, full caps differ — cross-checked against reference python H), fed through the production hit path dp_event→hit→traceback→found_pair3→file: fires==1, rejects==0, and the file content is exactly the planted pair (traceback returned the true merge predecessors).
- D1–D4: single-trail rho self-closure (same-start revisit) also fires with a verifying distinct pair.
- A1–A3/B2–B4 NEAR-MISS: 1000 random production-width (T=80) pairs all rejected, 0 fires; capacity-differing near-miss rejected; identical message rejected; disjoint trails (F(m1)≠F(near-miss)) insert into the table but never hit → no fire. E1: full-width encoding F=(clo, chi<<48) exact (mode 1 never exercises the hi16 path; production does).
- Cross-validation against the binary: `walker3.exe` mode 1 (scratch cwd) FIRES end-to-end (ins=17 hits=1 fires=1 rc=0); `tv3_check.py` 50/50 kernel==python H; `harvest3.py` refused a garbage found_PROD-named pair with `cap2 mismatch` AssertionError BEFORE network (rc=1).
- Safety verified: probe never wrote `found_PROD*` (checked after every fire phase); production PID 27160 untouched (alive in tasklist; walker3_run.log advanced to steps=4.446e9, ins/steps=5.8e-8≈θ ✓); no found_PROD in challenge dir.

### Detection-rate math — P(real search misses a valid solution)
- The DP mask is a POINT predicate: two merged trails follow the identical suffix after the merge point, so both stop at the SAME first masked point z* (one inserts, the other hits; entries are never evicted). A sampled collision is missed only if one of its two trails is abandoned (MAXTRAIL=20/θ with no DP): P=e^-20=2.06e-9 → union bound over two trails: **P_miss(collision | collision pair sampled) ≤ 4.12×10⁻⁹**.
- Structural corner (first shared point coincides with a trail start → predecessor pair not both sampled; found_pair3 correctly rejects): ~2^24/2^80=2^-56 per trail pair, negligible.
- Verification can never reject a true merge: F(pa)=F(pb) with injective g ⇒ exact capacity equality on the same kernel (probe C2/D3 certify acceptance); harvest3's python re-verify is a second independent gate.
- ⇒ **P(fire by k) = (1−4.1e-9)·(1−e^(−k²/2^81))**; at median k=1.3744e12 nominal P=54.2% — detection coverage 1−4×10⁻⁹. The walker2 failure class (value-mask DP: per-collision detect 2^-24, miss 0.99999994) is excluded by construction (trajectory mask) AND by this planted-hit assertion.
- Coverage limits (honest): the planted end-to-end fire is at 20-bit truncation (only plantable scale — a real full-80-bit equal-capacity pair IS the search target). Production shares the identical code path at T_BITS=80; that path's encoding is gated by E1, its kernel by tv3 50/50 vs python, its reject gate by 1000 T=80 random pairs. The one branch combo not planted end-to-end: equal-clo64-with-equal-chi16 accept at full width (mathematically the same `&&` predicate, exercised accept-side only at T=20).

### Verdict
**ASSERTION: PASS.** Walker3's detection path fires planted true hits and rejects near-misses on the exact production code; completion of the running search (PID 27160, ETA_med 59.3 h at 6.45 M F/s) is trustworthy at detection coverage 1−4.1×10⁻⁹. **No rebuild needed** — walker3.exe (Nov 6 10:45) is newer than walker3.c (10:41), and the probe compiling walker3.c with the build-script flags (-O3 -funroll-loops -Wall -pthread, gcc 16.1) reproduced the expected behavior exactly.

### Configuration (this assertion)
2026-11-07 EST; Windows 11 + MSYS bash; gcc 16.1.0 (winlibs mcf); venv python ~/tools/crypto-ctf/venv; probe + artifacts under `~/AppData/Local/hermes/cache/scratch/detprobe323/` (detprobe.c, detprobe.exe, selftest/found_TEST.txt); challenge dir read-only except this AAR append; extra compute = one 30-s 2-thread mode-1 exe run (512 MB) + probe (~2 s) + tv3 (instant) — smoke budget; production walker3 (PID 27160) untouched; NO network contact this session (harvest guard tripped pre-socket).


## LIVE-COUNTER AUDIT 2026-11-08 17:47 EST (reviewer pass #2; gdb read, zero restart)
walker3.exe PID 27160: gsteps T1=0x110ac0752e8 -> T2(+30s)=0x110b77e4771 = 6.41 M F/s (full launch rate);
k=1.1713e12=2^40.09 (85.2% of nominal median); g_hits=g_fires=0; g_ins=69,986 (ins/steps 5.97e-8 vs launch
self-cert 5.76e-8 — DP filter profile intact). 54-h silent log explained: stdout pipe died with its launching
session ~2.5 min post-launch; disk was never the channel except FOUND writes.
Model status: P(fire by now)=43.3%; P(zero-hits-so-far)=56.7% => NOT falsification. Registered gates:
G1 median k=1.3744e12 ~11-09 02:35 EST; G2 5%-falsification k>=2.693e12 (2^41.29) ~11-11 11:30 EST at measured
rate (+66h, ~132 CPU-h). Deadline-control stop at Nov 10 banks only P(miss)=29.2% (WEAK) — owner decision
logged (extend-to-G2 vs weak-bound stop). Erratum: '77% of 2^40 zero-hit' = walker2 Nov-2 run figures, not
walker3. Details: campaign-root ERRATA_E5_20261108_evening.md.

## CLOSURE (2026-11-10): SOLVED — walked collision, service-derived flag
- 03:05:42 EST gate_keeper logged FIRED: found_PROD_1.txt appeared between 02:50 and 03:05 ticks (walkers pid21244 k=5.155e11, pid27160 k=1.925e12). Early relative to the pre-registered gate milestone (Σk²/2^81 was ~1.3-1.6 overnight; Poisson P(fire) 58->72%% across the evening) — a lucky early draw inside the model, not an anomaly; model survives.
- harvest3.py: rebuilt 3-block messages, verified H(a)==H(b) under the reference python sponge BEFORE any network contact, submitted pair to archive.cryptohack.org:37916 -> service printed CHTB{...} on acceptance. harvest3's flag filter only matched crypto{ and reported 'NO FLAG'; the service's flag is CHTB-format. Same morning (post-reboot) the filter was widened (crypto{ | CHTB{).
- submit via submit_flag.py: accepted; solved 312 -> 313 (API before/after); independently re-verified post-reboot via verify_progress.py (spongebob no longer open; sole remaining point-bearing open row = 237 sigma-hamiltonicity2, the owner's course blocker).
- Provenance: WALKED — flag produced solely by our own collision fed to the named service; no writeup/source assistance; ledger + this AAR are the record.
## Host incident (2026-11-10 ~03:04-03:07 EST)
BSOD: Kernel-Power 41 + WER bugcheck 0x154, EventLog last heartbeat 03:04:43, dirty restart; machine back ~08:43. Correlation note only (no causation claim): ~18 h of sustained dual-walker CPU load was running; both walkers died with the crash and were intentionally NOT resurrected (row closed). Fleet-watchdog cron paused; 294-reporter/294-watchdog crons removed. Owner ruling recommended before any future sustained-load fleet on this host.
