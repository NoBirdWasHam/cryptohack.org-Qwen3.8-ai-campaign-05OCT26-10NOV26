# AAR — Origami (NNS CTF 2025), cryptohack slug `origami-nns_ctf_20252025`

## Challenge
Static archive challenge (no listener), 0 pts. Statement: "Origami is a ntruly
marvellous artform" ("ntruly" = NTRU pun). Files: `source.sage`, `output.txt`.

## Method-provenance annotation (owner ruling 2026-11-07; REQUIRED annotation added 2026-11-08 per external audit)
Attack-FAMILY direction was supplied by the owner in the 11-07 ruling (PROVENANCE_2026-11-07.md:
"NTRU key recovery — Lambda_q^h uSVP, Atamagorodov-Coster folding, May/Silverman projection,
Howgrave-Graham hybrid, dense-sublattice / overstretched, subfield attacks, symplectic structure,
CVP formulations"). Per that ruling this is NOT contamination: the directions name published attack
families from the general cryptanalysis literature, not this instance's writeup content, and no
per-challenge solution details were provided. Everything downstream — implementation, parameter
choice, the final k=3 symmetric ring-fold construction, the parity-recovery finisher, and the flag —
was independently executed and re-derived on synthetic instances before the real one, from
service-given data. Classification per campaign taxonomy: SELF_DERIVED_METHOD with OWNER-DIRECTED
family guidance, per the ruling's mandated "Honest annotation" clause.

## What the vuln was
Toy **NTRU** `n=512, p=2, q=127, df=35, dg=35, dr=22`. `h = g/f` in
Z_q[x]/(x^512−1), `ct = 2·h·r + m mod q`, flag bits as 0/1 coefficients
(`bytes_to_long` bit order). Two weaknesses:
1. Key recovery: NTRU lattice L = {(a,b): b ≡ a·h mod q}, dim 1024, det = q^512.
   Secret (f,g) has norm ≈ 8.4 vs det^(1/1024) ≈ 11.3 — λ1 ≈ 10× below the
   Gaussian heuristic (~87): routine BKZ territory on normal hardware.
2. p=2 tiny-parameter NO-WRAP parity decryption (removes r entirely):
   lift(f·ct mod q) into [0,126] is EXACTLY the integer 2·(g*r) + f·m
   (per-coeff ≤ 2·22+35 = 79 < 127), so B := lift mod 2 = f·m over
   GF(2)[x]/(x^512−1). df=35 odd ⇒ f(1)=1, and x^512−1 = (x+1)^512 over F2 ⇒ f
   is a unit ⇒ m = B/f by a 512×512 GF(2) linear solve. Holds for ANY lattice
   vector (f′,g′) with {0,±1} coeffs, odd weight f′, 2Σ|g′|+Σ|f′| < 127.

## Attack pipeline (implemented)
- solve2.py / solve5.py: build L → fpylll BKZ (25/30/40) → scan for {0,±1}
  rows → parity decrypt.
- dec.py / dec2.py: standalone decryptor for any candidate (f,g) vector.
- selftest.py: end-to-end synthetic validation of step 2 (lift + GF(2) solve).
- solo3.gp: PARI scramble+partial-LLL fallback chain (host workaround).

## Validation actually done
Synthetic round-trip: lift exactness confirmed (max coeff 29–35 « 127); GF(2)
solve recovers m with 0 bit errors. Two decoder bugs caught by it: byte order
(LSB-indexed bits of a big-endian int) and circulant non-symmetry.

## Result: UNSOLVED this session — flag NOT derived, NOT submitted.
Blocked by host capability only (dim-1024 lattice reduction):
- fpylll 0.6.4 works ≤512 dim (LLL 19 s, BKZ-20 42 s) but BKZ at 1024 dies with
  STACK_OVERFLOW 0xc00000ff (Application event log), even with a 64 MB-stack
  thread (died ~25 min in; solve5.log/err).
- PARI qflll exact LLL on the true lattice: 447 s, min norm² = 16129 = q²
  (`(0,q·e)` family) — plain LLL reach can't touch an 8.4-norm target below GH.
- python-flint: no deep/BKZ; conda-forge fpylll: no win-64 build; micromamba
  sage env: unsolvable specs.

LEFT RUNNING (detached, outlives this session): `gp64 -q solo7.gp` → solo7.log (parisize 8G; solo6 2G overflowed qflll).
UPDATE (session 3): solo7/solo8 gp jobs DIED at a `break>` loop (interrupted; no gp64 left).
Pivoted to fpylll. ROOT CAUSE of the solve6 `IntegerMatrix(rows)` TypeError:
fpylll 0.6.4 has NO list-of-lists constructor — build via IntegerMatrix(1024,1024) +
per-entry set (0.1 s for 1M entries). fpylll lives in `~/tools/crypto-ctf/venv`
(Scripts/python.exe), NOT base Python312. solve7.py = fixed staged runner:
192MB-stack thread, checkpoint (gzip round-trip verified) + resume per block size,
p.max_time=2400/stage (EasyParam takes no timeout arg), scan+parity-decrypt after
each stage, non-zero exit on thread exceptions. run_bkz.sh = stage loop
(20→25→30→40, 2 attempts/stage) → run_bkz.log; launched detached.
FINISH PATH unchanged: flag file `flag_origami-nns_ctf_20252025.txt` written by
solve7.py on NNS{...}; then `python3 submit_flag.py origami-nns_ctf_20252025 "<flag>"`.
CORRECT qflll convention now verified on a mini instance: lattice vectors are
the COLUMNS of V where `V=transpose(M); V=V*qflll(V,0)` (qflll(M,3) output is
useless; rows are not the lattice). Chain: ~7 min initial LLL, then up to 300
scramble+re-LLL rounds; prints "round r best norm2" on improvement and
`DUMP <512 ints | 512 ints> END` for any vector with norm² ≤ 200.
FINISH PATH: when a DUMP line appears, run `python3 fixdec.py` (parses
solo6.log, parity-decrypts) → on `NNS{...}`: from workspace root
`python3 submit_flag.py origami-nns_ctf_20252025 "<flag>"`.
NOTE: keep exactly ONE gp64 running; each uses ~1.5–3 GB.

## Learning points
- gp 2.17 on Windows: statements must be SINGLE-LINE (multi-line for() bodies
  are parse errors); `lll`→`qflll`; `clock()`→`gettime()`; no `transpose` → `M~`;
  NO `flush` function; `random(a,b)` invalid — `random(n)` = [0,n).
- `qflll(X,3)` reduces COLUMNS of X. My first matrices reduced the trivial
  column-lattice {(a,b): q|b} — membership-test any candidate (b ≡ a·h mod q)!
- p=2 NTRU: try the no-wrap parity decryption first.
- Silent background deaths here were (a) 3 zombie gp64 × 3.2 GB → 0xC0000142
  init failures, (b) genuine stack overflow in fplll enumeration. Use
  `tasklist | grep -a`, powershell Get-Process counts, and
  Get-WinEvent 'Application Error' for the exception code.

## Limitations (honest)
- No flag this session; nothing submitted. No writeups/solution files consulted.
- Failed: fpylll BKZ-40/25/20 @1024 (stack crash ×3), fpylll LLL @1024 (>7 min,
  killed under memory pressure), PARI exact LLL (reach), first three scramble
  scripts (gp syntax/column/flush bugs), python-flint, micromamba fpylll/sage.
- Math fully worked and unit-verified; only the BKZ execution is missing
  (minutes on Linux).

## SESSION 4 (BKZ resume; crash root-caused)
- run_bkz deaths NOT memory (reproduced with 39 GB free) and NOT wall-clock.
  ROOT CAUSE: precision. fpylll wheel `float_types=('d','ld','dpe','mpfr')` (no 'dd'),
  auto picks 'd'; 'd' AND 'dpe' hard-kill the process ~60-120 s into enumeration at
  dim 1024 (ill-conditioned GSO; 192 MB stack irrelevant). float_type='mpfr'
  precision=200 SURVIVED a full BKZ-20 max_time=400 slice (returned clean at 1894 s,
  min norm2 still 16129 — one slow tour, mpfr-1024 is ~10-20x slower than native).
- exit=127 via bash is NOT diagnostic (clean fplll errors also surface as 127).
- solve7.py bugs fixed: `scan` NameError (now defined, n2<=200 prefilter); `max_time`
  is ctor-only (`BKZ.EasyParam(k, max_time=…)`); try_vec now also tries (-f|-g) and
  (-g|-f): source.sage `random_poly` uses **+1 only** ⇒ y=2gr+fm ∈ [0,105] nonneg ⇒
  [0,127)-lift parity is exact (synthetic GF(2)+bytes round-trip: MATCH, max S=29).
- ENGINE COMMITTED: solve8.py = staged mpfr chain k=20→25→30→40, 900-s slices,
  per-stage checkpoint M_s<k>.txt.gz + resume, scan after every slice, 192 MB thread.
  Launched detached → run8.log. On `NNS{...}` it writes
  flag_origami-nns_ctf_20252025.txt; then
  `cd ~/Practice_runs/cryptohack_org && python3 submit_flag.py origami-nns_ctf_20252025 '<flag>'`.
- Fallback prepared (not installed): MSYS2 native fplll CLI (auto d→dd→mpfr ladder,
  much faster than pure mpfr). fplllpipe.py ready: M_lll → cur.txt → `fplll.exe
  -b k -t 1500` → scan/decrypt. MSYS2 installer downloads kept failing this session
  (github via curl AND powershell); retry: pacman -S mingw-w64-ucrt-x86_64-fplll.
- PARI on this host lacks FpX_invMod/FpXQ_inv (older build) — synthetic mod-q inverse
  cross-check not completed; GF(2) core + lift lemma verified instead.
- STATE AT HANDOFF: solve8 mpfr chain RUNNING (session handed to parent). Flag not yet
  derived; nothing submitted. Files added: solve8.py, fplllpipe.py, probebkz.py,
  probebkz2.py, mattest.py, mattest2.py, paritytest.py, paritytest2.py, run_bkz2.log.

## SESSION 5 (2026-11-03, unit continuation)

**Crash root cause (fixed by workaround):** in-process fpylll 0.6.4 BKZ hard-kills
the interpreter (exit 127, NO catchable Python exception) with `float_type="d"`,
`"ld"` AND `"mpfr"` on the dim-1024 basis (probe12.py). Engine moved OUT OF
PROCESS to fplll CLI — the original queue-note `IntegerMatrix(rows)` TypeError was
ragged rows from truncated stdout; fixed in Session 4, not re-triggered.

**QD (double-double) engine built from scratch:** MSYS2 gcc-16.2 rejects
hex-float literals with a SIGNED exponent (`0x1p+53`, `0x1p-53`) in C++11 mode —
this is what killed the October QD configure. Fix: sed `0x1p+`→`0x1p` and
`0x1p-53`→exact decimal `1.1102230246251565404236316680908203125e-16` in
dd_inline.h/td_inline.h; also delete the stale `prefix/include/qd` that shadowed
fresh headers; build env needs `msys64/ucrt64/bin` FIRST on PATH. Result:
`prefix3/bin/fplll.exe` with `FPLLL_WITH_QD 1`, `-f dd` works.

**Toy gates (both PASS):** (a) planted NTRU lattice (n=64,q=127,w=5): CLI BKZ-20 dd
returns the planted (f,g) vector exactly; (b) toy_decrypt_check.py proves the no-wrap
parity decrypt + GF(2) circulant solver + bit assembly recover a planted message
exactly. Entire pipeline except real-lattice recovery is verified correct.

**Why 40h of mpfr BKZ-20/25/30/45 produced nothing:** λ2/λ1 gap ≈ 87.25/8.37 ≈
10.4 at dim 1024 ⇒ core-SVP dimension ≈ 55-60 ⇒ blocks below ~55 CANNOT find (f,g)
no matter how many tours. And mpfr BKZ-20 can't even finish one loop at dim 1024 in
1500s (CLI rc=7 "time limit exceeded"; toy512 mpfr stage likewise killed at 25min).
The dd engine (native speed, 106-bit precision) at β=60 is the attack; mpfr is out
of its depth at this dimension.

**fplll CLI quirks (new):** (1) `-bkzmaxtime` hit ⇒ exit rc=7 but reduced basis IS
written to stdout — chain gate must be "output non-empty", not rc==0. (2) Segfault
(rc=139) for `-a bkz -b 60 -f dd -bkzdumpgso` on the dim-1024 lattice (dump path
bug; β60 works fine WITHOUT dumpgso; toy dim-128 fine WITH it). (3) `-f dd` requires
the new prefix3 build. (4) scan_cli row parser crashed on fplll file format
(`][` adjacency, no whitespace) — the per-slice scan would have been SILENTLY blind
(chain pipes it through tail, loop continues). Fixed to regex `\[([^\[\]]+)\]`;
verified on both file and stdout formats (1024x1024 parses, scan done in 2.2s).

**STATE AT END OF SESSION-5 UNIT:** chain60b_dd.sh RUNNING: BKZ-60 dd, 24×1200s
slices from real.fplll via cur60b.fplll, scan_cli.py after each slice; writes
flag_origami-nns_ctf_20252025.txt on any row/CVP hit that passes membership+decrypt
then parent submits via `submit_flag.py origami-nns_ctf_20252025 '<flag>'`.
Wall: BKZ-60 @ dim 1024 on this CPU; dd slices are the only engine+block combo that
meets the gap math. Files added: probe10-12.py, toy_ntrugen.py, toy64_truth.json,
toy64.fplll, run_cli_toy.py, mk_real_fplll.py, real.fplll, scan_cli.py,
chain_dd.sh, chain60_dd.sh, chain60b_dd.sh, toy512_run.py, toy_decrypt_check.py.

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.

---

## VALIDATION 2026-11-05 — live-door audit of the BKZ-60 dd chain: slice healthy; short-vector threshold + BKZ-60 margin recorded; ZERO real-lattice slice-scan evidence exists on disk

State at audit (read-only, nothing touched): `fplll.exe -a bkz -b 60 -nolll -f dd -bkzmaxtime 43200` (PID 27964) started 11-05 16:29:06 EST — **slice 1 of chain60c is the first slice ever to run with the real 12-h budget** (parent bash 14264 alive, err60c_1.txt 0 bytes). First real-lattice scan_cli output lands in chain60c_relaunch.out at the first boundary ≈ 04:30 EST 11-06.
**Context correction (flagged)**: the parent framing "short-vector for NFS-DLP GF(2^607)" does NOT belong to this door — folder-wide grep finds zero NFS/607/descent artifacts; the running cado-nfs DLP client (~/dlp_work, dlprun5.sh → WORKSTATION) belongs to challenge-305-unevaluated-tetctf2021, a different door. This door's lattice = the dim-1024 NTRU key-recovery lattice (re-parsed: real.fplll and cur60b.fplll both exactly 1024×1024).

### Per requirement {have|missing}
1. **Threshold the descent actually needs {have}**: ONE row (f',g′) with {0,±1} coeffs, odd-weight f′, Σ|f′|+2Σ|g′|<127 (scan_cli try_f gate; norm² ≲ 70–127), decryptable by the verified p=2 no-wrap parity trick (Babai center-CVP with resid²<300 fallback is wired into scan_cli). Planted (f,g): weights (35,35) ⇒ target norm ≈ 8.37 (norm²=70). Lattice det=q^512 ⇒ det^{1/1024}=11.27, GH=87.3 ⇒ need ≈ **10.4× below GH** (gap λ2/λ1≈10.4).
2. **Does BKZ-60 reach it {have — margin on heuristic + β-60 toy anchor}**: uSVP-gap heuristic (δ^{(n+1)/(β−1)}): BKZ-60 needs gap ≥ 1.0119^{17.4} ≈ 1.23 vs 10.4 available — large margin (β=40 ≈1.44, β=20 ≈3.1 also pass on paper: their prior failures were mpfr/ld engine speed & crashes, not block size). Toy anchor at exactly β=60 dd: gtoy60.json first ‖b*‖² = e^{2.30} ≈ 10 = planted vector norm² (toy64 BKZ-20 dd recovers planted (f,g) exactly). β=60 dd is not at capability edge; residual risk = tour throughput at dim 1024 and heuristic overpromise — unmeasurable mid-slice (dumpgso segfaults at β60 on dim-1024).
3. **Prior-slice scan_cli output to extrapolate from {MISSING — none exists}**: no real-lattice slice ever reached the scan step (β60 chains: rc=139 dumpgso segfault / rc=1 empty-out instant fails; scans then parser-blind). Disk truth re-measured now: min row norm² = **16129 = q²** in BOTH real.fplll and cur60b.fplll (only the trivial (0,q·e) family; 0 rows ≤ 400 gate); run8.log: flat 16129 across ≥13 mpfr slices β 20→40; GSO dumps (b20ld/chain_1/60_1/512_20) all share mean ln‖b*‖² = 4.844 = 2·ln(det)/n ⇒ det untouched, 38×‖b*‖=127 plateau + tail, profile unchanged. ⇒ No positive trend to extrapolate; every past hour is zero-progress-at-the-q-floor; tonight's slice-1 scan is the FIRST data point in this door's history.
4. **Engine/chain health {have}**: 12-h budget honored; checkpoint preserved + resume-fixed (cur60b kept, not reset); fail-capped retry (5×) — the 34-h instant-fail pattern is dead; scan parser regex fix verified on 1024×1024 format; site card: solves: 10 (human path exists; df=35/q=127 recovery is routine on working engines — Windows-engine-only blocker here).

### ONE next move
At ≈04:30 EST 11-06 read the first scan_cli block in chain60c_relaunch.out: min row norm² **< 16129** ⇒ q-floor broken, let the 48-slice chain run; still exactly 16129 after a full 12-h BKZ-60 dd tour ⇒ escalate (β≥70, CVP-embedding of the {0,±1} target, or off-host reduction) BEFORE committing the remaining ~47 slices.

## SESSION 6 (2026-11-07) — escalate-branch waiver: GPU audit NEGATIVE, pruned-enum engine FOUND on-host (no build), CVP-embedding dead by math, beta>=70 pruned chains LAUNCHED

### (1) GPU branch — impossible on this host, every route documented
- GPU = **AMD Radeon AI PRO R9700** (Win32_VideoController); **zero NVIDIA devices** (Win32_PnPEntity NVIDIA → empty); `nvidia-smi` nowhere on host.
- `C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.2` exists but ships **no nvcc.exe** (partial install) — moot without a CUDA device.
- **g64 folder does NOT exist** under tools/ (prior-brief premise wrong; tools/gp64.exe = PARI/GP 2.17, not GPU BKZ). pyf64 not importable in venv. g64 (Team-NSN) is CUDA-only; a HIP/ROCm port = multi-day project, out of scope.
- WSL unavailable (WSL2: virtualization disabled in firmware; WSL1 unsupported) — no Linux-on-GPU escape hatch either.
=> g64-vs-fplll benchmark substituted by pruned-vs-unpruned benchmark on a moderate planted instance (see 3).

### (2) PRUNED-ENUMERATION ENGINE: already present in the host's own fplll build — chain60c was NOT using it
- **Root finding**: `fplll -a bkz` WITHOUT `-s` passes an EMPTY strategy vector; BKZParam ctor then builds `Strategy::EmptyStrategy` (bkz_param.h:124-130) = pruning coeffs all-1.0 (UNPRUNED) and no preprocessing recursion. The running chain60c = plain non-recursive BKZ-60.
- `prefix3/share/fplll/strategies/default.json` (installed with the QD dd build; path baked in binary) carries the REAL pruned tables: blocks 60/70 have 21 entries, gh_factor 0.907–1.103, coeffs descending 1.0→~0.30, uSVP probability metric, pre-processing 60<-40 / 70<-50. **`-s <that file>` == the pruned+recursive engine the escalate branch believed missing.** No rebuild needed (brief item 2 satisfied by discovery: fplll 5.5.0 ships pruner module + strategy JSON; a 2h rebuild was never the gap).
- CLI smoke: `-a bkz -b 60 -f dd -nolll -s default.json` on toy64 => **planted (f,g) norm²=10 recovered, rc=0, 18 s** (maxRSS modest, stderr silent = strategy loaded).
- `fplll -a pru` also wired (GGO pruner, -prustart/-pruend/-bkzghbound); `-a svp/-a cvp` = SINGLE full-dim enumeration at Babai/min-row radius (svpcvp.cpp closest_vector, no BKZ) — dead at dim 1024 (same wall class as failproof_revenge CVP_ARSENAL measurement).

### (3) Engine benchmark, moderate planted instance (BKZ-60 dd, tour-granularity caveat)
- New instance t280_mid256.fplll: n=256, q=127, df=dg=10, planted norm²=20, GH≈61.6, gap≈13.8 (real instance: dim 512->1024 gap 10.4). Arms (all -f dd -nolll): b60 empty-strategy (= chain60c behavior), b60 unpruned-twin (t280_strat_noprune.json), b60 default.json pruned, b70 default.json pruned — results to t280_bench_results.txt as tours complete.
- **Measured engine-behavior fact (this session)**: fplll checks `-bkzmaxtime` ONLY at full-tour boundaries (bkz.cpp:588) => every `-bkzmaxtime` slice actually runs >=1 whole tour. This explains chain60c slice-1 overshooting its 43200 s budget at 43.4 h CPU without output (tour-1 not done; deep-block rate for recursive beta-70 on the real lattice measured ~1.2 blocks/min => tour ~15–20 h). Slices must be budgeted per-tour, not per-second.
- Real-lattice beta-70 pruned probe (300 s cap, scratch copy): healthy descent, 42 blocks logged, dd GSO+enum private RSS = **115 MB** (cap 2000 MB honored x5+ margin); killed on purpose once behavior+RSS measured (fplll 20580/27828 terminated at 14:40 by this unit — own process only).

### (4) fpylll CVP-embedding branch (3) — measured, then killed by math not engine
- fpylll 0.6.4 in-process on toy64: **BKZ-20 dim128 SURVIVED 0.7 s; BKZ-64 dim128 SURVIVED 46.4 s; Kannan-embed dim129 beta64 SURVIVED 26.4 s** (probe_fpy_*.log). So the host's BKZ crash wall is (dim,entry-size)-dependent, NOT universal at beta>=64 — but dim-1024 all-float-type crash (probe12) + exit-127 class stands; never run fpylll BKZ at 1024/1025 in-process.
- **Hint-target degeneracy (t280_cvp_math.txt)**: scan_cli target t=(35/512)·1^1024 has ||t−0||²=4.79 vs ||t−(f,g)||²=65.21 => CVP(t,L)=ZERO vector — the {0,1}-weight-35 hint CANNOT be a BDD target (zero lies closer); Kannan-embedding it returns (0|w). ct-based target: lift-norm ~1400 >> λ2. **CVP-embedding is vacuous for this challenge; escalation = pruned BKZ tours only.**

### (5) LAUNCHED (detached, persist; NEVER touch chain60c PID 27964 — left running per owner rule)
- `t280_chain70p_dd.sh` TAG=70p K=70 and TAG=60p K=60: pruned+recursive BKZ dd on the REAL lattice from cur60b seed (=real.fplll content), 12 tour-slices, scan_cli.py gate after each tour, FLAG-FILE gate -> flag_origami-nns_ctf_20252025.txt -> `python3 submit_flag.py origami-nns_ctf_20252025 <flag>`; private-RSS watchdog 2000 MB (kill+retry, 5-fail cap); own checkpoints t280_{70p,60p}_{cur,next}.fplll; logs t280_chain{70p,60p}.log.
- Threshold sanity: documented floor **16129 = q²** (re-verified in AAR VALIDATION-11-05 section); any row norm² <400 already auto-routed by scan_cli try_f gate; 16129-break alone (no decrypt) = trend signal for the next session.
- Files added this session: t280_gen_mid.py, t280_mid256.fplll(+truth), t280_mk_noprune.py, t280_strat_noprune.json, t280_bench.sh, t280_bench_results.txt, probe_fpy_t280.py, t280_fpy_probe.sh, probe_fpy_{bkz20,bkz64,embed64}.log, probe_fpy_rc.txt, t280_cvp_math.txt, t280_chain70p_dd.sh, t280_smoke.out/err.
- BENCH PARTIAL (2026-11-07 15:2x): ARM b40_empty rc=7 wall=901s minnorm2=16129 planted=False —
  one empty-strategy beta-40 tour on mid256 already exceeds the 900 s budget (recursion/pruning arms
  land in t280_bench_b40.txt / t280_bench_results.txt as their tours complete, asynchronously).
  q-floor held at beta40 exactly as the session-5 gap math predicts (beta<~55 cannot reach 8.4).

## SESSION 7 (2026-11-08) — STRUCTURAL ATTACK: idempotent RING FOLD (the actual "Origami")

**Key idea (verified, deployed):** over Z_127 (q odd), x^512−1 = (x^256−1)(x^256+1) are
coprime ⇒ R = Z_127[x]/(x^512−1) ≅ R⁺ × R⁻ via f ↦ f± = f0 ± f1 (fold of the two halves;
h± = h0 ± h1 in rings y^256∓1). φ± are ring homomorphisms (machine-verified against the real
pk for random 35-sparse f: plus=True minus=True). Each component gives a dim-512 q-ary lattice
M± = {(u,v) ∈ Z^256²: v ≡ u·h± mod (127, y^256∓1)}, det = 127^256, GH = 61.7, planted
(f±,g±): ‖(f⁺,g⁺)‖² = 2(35 + 2·E C(n,2)) ≈ 79 ⇒ gap ≈ 6.9 vs dim-1024 gap 10.4/dim-1024
engine wall. Required β ≈ 50 ⇒ BKZ-60 dd PRUNED at dim 512 is inside host capability (vs
15-20 h/tour at 1024). Recovery needs only small rows, not exact f: glue f⁺ (coeffs {0,1,2},
Σ=35, ±, rotated) with f⁻ (coeffs {0,±1}) via (f⁺±f⁻)/2 ∈ {0,1} alignment test over all
(k,l) rotations; verify h·f ≡ g (mod x^512−1, 127) exactly; parity-decrypt unchanged (f is
then the true f up to ring rotation x^j, and x^j·f decrypts to the SAME flag: B and solve are
both consistent, unit over F2 preserved).

**Validation done:** (a) homomorphism check on real pk; (b) GLUE+DECRYPT unit test on planted
n=256 toy (odd df — needed for F2-unitness; real df=35 is odd ✓): recovered planted flag from
rotated fold parts; (c) FULL TOY PIPELINE incl. fplll CLI: n=256, df=dg=9, fold lattices dim
256, CLI `-a bkz -b 45 -nolll -f dd -s default.json` recovered exact planted folded vectors
(min norm2 = 18 = planted, 87 s) → glue → FLAG EXACT MATCH.

**Engine/host findings:**
- IN-PROCESS fpylll BKZ (d AND ld) HARD-KILLS (rc=127) even dim-256 PLANTED fold lattices
  (toy reproduction deterministic); random-h q-ary lattices of same dim are fine — the crash
  is (planted-structure × enumeration)-dependent, not just (dim, entries). Never run in-proc
  BKZ on these lattices; LLL is safe (17 s @512).
- float64 Gram of the LLL-reduced fold lattice is NUMERICALLY SINGULAR (λ_min = −1e−9 at
  ‖G‖=3.8e7): GS profiles need ≥ longdouble. Seed LLL profiles (t280_fold_profiles.json):
  head log2‖b*‖ = 6.99 (=log2 127, q-e family), linear decay to −2.3 (plus, pos 511) / −2.0
  (minus, pos 417); NO width-≥2 step at the planted scale yet (LLL reach). Tail <log2 3 spans
  ~242 positions = q-ary presentation artifact (top (I|H) block nearly spans the tail
  directions over reals), NOT the submodule.
- fplll CLI `-f dd -b 60 -s default.json` = the engine for these lattices.

**Launched:** t280_foldchain.sh (detached, PID tracked): β60 pruned dd alternating slices on
t280_fp_cur.fplll / t280_fm_cur.fplll (LLL seeds written by t280_fold_mk.py), t280_foldscan.py
(exact pattern scan + glue + parity decrypt + flag-file) after every slice pair, RSS cap
2 GB, external hard kill 4 h/slice, -bkzmaxtime 3600 (tour-granular). Legacy 1024-dim chains
(60p/70p/chain60c fplll PIDs) left untouched as backup; host has 16 cores.
Files added: t280_fold.py (core fold/glue/decrypt lib), t280_fold_mk.py, t280_foldscan.py,
t280_foldchain.sh, t280_fold_toy.py, t280_foldtoycli.py (TOY FULL SUCCESS), t280_gluecheck.py,
t280_dbg2-5.py, t280_fold_profiles.json, t280_fp_cur.fplll, t280_fm_cur.fplll.
Note: parent-context framing for this task (dim 512, q=32749, Φ60, planted norm²=4252,
threshold 11177, flag=80-bit x0) does NOT match this challenge's files/AAR (dim-1024 NTRU,
q=127, planted norm²=70, df=35) — AAR+files treated as authoritative.
- OPS NOTE: during process cleanup I killed the t280_chain70p_dd.sh bash loops (23920/2764/11524/15576/25204/21720) and their current fplll slices (7556 beta60, plus earlier orphan 4912). Their 12h checkpoints survive; slice fplll 9696 (b70) and 7764 kept running. Unintended, disclosed.

## SESSION 7b — ladder execution, fplll rc semantics, v2 runner
- fplll dd semantics (this build): -bkzmaxtime exhaust => rc=7 "time limit exceeded"
  BUT full valid reduced basis IS written to stdout; -bkzmaxloops N => rc=8
  "loops limit exceeded", also valid output. v1 discarded both as failures and
  burned 2x45 min of beta-40 work (truncated retries). t280_run2tag.sh accepts by
  row-count regardless of rc.
- Tour cost @dim512 dd pruned: B20 ~1-2 tours/5min (converge), B30 ~21-26 min
  (converge, several tours), B40 ONE tour 31s, B50 ONE tour ~184s, B60 ONE tour
  ~760s and climbing.
- Best NON-q-row norms2 after B20+B30: fp 553202, fm 509033 (norm ~744/713) —
  min-row norm2 stays 16129=q^2 (q-row pinned, NOT the right progress metric).
  B40/B50 full tours changed bestnorm by <1% (553202->554260): unique-SVP gap 6.9
  NOT being touched by full beta<=50 reduction on the folded dim-512 lattices.
- EXACT GS profile (Bareiss minors, beta30 fp): head 6.99 (127), mid 3.7-3.9,
  tail -2.61..-2.23, det^(1/n) log2 3.494 (=11.27 ✓), ZERO steps >0.5 anywhere:
  NO dense-submodule STEP at planted scale at beta<=30. (longdouble classical GS
  drifts on these bases — exact-Bareiss is the reliable profiler here.)
- Negative result forming: fold gap 6.9 at dim-512 is NOT reachable by
  BKZ<=50-full; beta-60 tours in progress (run2tag p/m, FLAG_FOUND.txt signal).

## SESSION 7c — parent notes (delegation incident + live state)
Delegated structure-ladder unit was cut by the watchdog at 07:14 (mid real-fold2toy debugging);
work before cut, verified by parent from transcripts + files:
- t280_fold2toycli.py: circulant rotation-SIGN bug fixed (i+k vs i-k); planted toy FULLY solves
  (planted f++ norm2 9 recovered via fold+GF2-glue+decrypt) -> pipeline logic sound at toy scale.
- Real instance: candidates passing "GLUED f+ valid" decrypt GARBAGE -> open thread: glue-vs-wrong-
  vector triage (norm ~509033 vectors are ~2^6 too long for weight-35 f; garbage is EXPECTED
  unless kernel enumeration is used — needs decisive control: planted real-shape toy through the
  same fplll runner scripts).
- LIVE right now (do not disturb): dd beta70 tours on folded lattices, p and m sides
  (t280_run2tag v2; fplll PIDs 22396 fpp-t2 since 07:08, 20344 fpm-t2 since 07:05;
  signal file FLAG_FOUND.txt; t1 tours DONE rc=8, minnorm2 still 16129 q-row, cands 0).

## SESSION 8 — decisive planted-control + REAL f++ recovered + deterministic finisher
DECISIVE CONTROL (planted real-shape toy through the SAME runner/tour path):
- t280_ctl_mk.py builds planted toy lattices (n=512 fold family, q=127, df=dg=35): level-1/2/3,
  det log2 600.68, 2 q-rows (matches real lineage exactly).
- t280_ctlrun.sh ladder (same fplll flags as real: -a bkz -nolll -f dd, default.json, maxloops 1):
  LEVEL-3 toy (dim 128, rank-64 module): planted FOUND, mins 84/64, subq=128/128, l3_planted_found
  true, tours 1-2s each -> runner/tour path is NOT the bug.
  LEVEL-2 toy (dim 256, rank-128 module, real shape): LLL/60/50/65/65/65 tours all DONE rc=8,
  mins 16129, subq 0, cands 0 -> TOY STALLS EXACTLY LIKE REAL (beta70 x2). Root cause is reduction
  adequacy on rank-128 modules, NOT the construction and NOT the runner.
SCAN-GATE BUG (quantified, fixed): fold2scan level-2 gates reject planted vectors with high prob:
  plus gate max<=2 passes only 86.4% (DP over 4-into-128 folds, exact), minus gate |c|<=1 passes
  only 1.94% (planted f+- HAS pm-slots of +-2; E[#level-2 pairs]=4.65). Level-1 gates are exact.
  Relaxed gates used here: plus 0..4 sum35, minus |c|<=2 & |sum| in 20..35, then membership test.
REAL BREAKTHROUGH: level-3 REAL lattices t280_real3.py (x^64-1, x^64+1 rings, dim 128):
  LLL seeds min 12974/13057; beta50/60/70 tours all DONE; mins 80/72; subq 128/128; 28+128 cands;
  bitset-parity glue (k,l in 64^2, sign) -> 201 valid, 62 unique f++ -> ALL ONE ROTATION CLASS
  (canon dedup). REAL f++/g++ RECOVERED (up to rotation+sign): cdist [97,27,4], g++ [95,31,2],
  ringmul(f++,hpp,128,+1)==g++ verified. Saved REAL_FPP_RECOVERED.txt.
DETERMINISTIC FINISHER t280_fin2.py (validated on toy pilot incl. toy-flag decrypt):
  f++ + f+- (from level-2 minus lattice rows) -> F256=f mod x^256-1, G256=g mod x^256-1 (g side from
  PAIRED scan row g+-; glue file g++ + row g+-) -> residual = ~35 split bits sigma in {+-1};
  PAIR-SUMS are sigma-invariant (x^256=1 quotient, E-matrix verified ZERO); pair-DIFFERENCES give
  256 linear eqs mod 127 on sigma: rows G!=1 force rhs 0 (225 eqs), G==1 rows must give +-1;
  Gaussian rank 34/35 (1-dim kernel: the f <-> roll(f,256) twin) -> 2^d sign enumeration, verify.
  Twin ambiguity is benign: BOTH twins decrypt the toy flag correctly (verified).
WATCHER: t280_watch.py polls t280_fpm_h.cur.fplll mtime (parent bheavy chain owns writes);
  on tour update runs fin2 automatically -> FLAG_FOUND.txt if f+- appears in reduced basis.
CP-SAT priced and rejected: full quarter-lift model UNKNOWN after 240s/32k conflicts even TOY.
BEST NORMS (min norm2, q^2=16129):
  real fp/fm  : 20881 / 21369 (level-1, dim 512, untouched this session)
  real fpp    : 16129 after beta70 x2 t-tours (07:48)  | real fpm: 16129 after beta70 x2, beta75 t1 RUNNING since 07:44
  ctlpp/ctlpm : 16129 after beta65 x3                 | ctl ppp/ppm: 84/64 (solved shape)
  real r3ppp/r3ppm: 80/72 (SOLVED, f++ recovered)
PRICED NEXT STEP (only unblocked path to flag): fpm ladder at beta 75/80 x 2-3 more t-tours,
  ~45-90 min/tour host-contended => 3-9h wall; relaxed gates + fin2 run automatically via watcher.
  If beta80 x3 no fall: expect needed beta in 85-95 (Gama-Nguyen style), ~2-6 days single dd;
  alternative then is a dedicated C/bf-variant or accepting priced-unsolved.


## SOLVED_ACCEPTED — 2026-11-08 (17:22:25-05:00, API 311->312)
Flag: [flag — recorded in FLAGS/ctf-archive/challenge-280-cryptohack-origami-nns_ctf_20252025/flag.txt] — locally derived, self-derived method (provided
materials only, per earlier Source sections of this AAR).
Terminal chain: REAL_FPP_RECOVERED.txt (f++,g++ from L3 glue, 08:43) + beta-75 tour #2 of the level-2 MINUS
lattice (t280_fpm_h.cur.fplll, 14:40:37) -> t280_fin2.py deterministic finisher: scan (member gate) ->
pair with saved f++ -> solve_sigma (35 split bits, 256 linear eqs mod 127) -> g-binary verify -> try_f decrypt.
Watch fired 14:41; FLAG_FOUND.txt written.
Contract verification 17:2x: frozen inputs (cur.fplll b652717c…, output.txt 99f979f0…, REAL_FPP cc752411…) copied
to isolated dir; fin2 re-run WITHOUT reading FLAG_FOUND.txt -> regen byte-identical (cmp pass), Bw_cands=8,
228 SIGMA-FOUND lines. Single submission HTTP 200; receipt SUBMIT_RECEIPT_280_2026-11-08.json (score +0 = archive
0-pt card; name "Origami (NNS CTF 2025)" on /api/user).
Same-day errata (full text in ERRATA_E4_manifest_refreeze_20261108pm.md): (1) morning false-SOLVED carried the
297 flag — withdrawn; (2) afternoon 'f+- NOT found' note read the fplll wrapper tally while the finisher had
already fired — withdrawn; state machine + anti-confabulation rules adopted in TAXONOMY.md.
Compute disposition: all beta>=75 chains stopped post-acceptance (17:35, respawn-verified); evidence dirs frozen
in sha256_manifest_20261108_pm.txt.
