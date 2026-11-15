# AAR — leet_universe (ImaginaryCTF daily), CryptoHack ctf-archive

## Statement
"The flag is hidden somewhere in the 1337th universe. Connect at archive.cryptohack.org 3721."
Provided: server.py (11 lines):

```python
x = int(input("x = "))
g = gcd(x**13 + 37, (x + 42)**13 + 42)
print(flag[:g])
```

## Analysis
- Server prints the first `g` chars of the flag, `g = gcd(f(x), h(x))` with
  f=x^13+37, h=(x+42)^13+42. To leak everything we need g >= len(flag).
- For every integer x, `g | R := Res_x(f,h)` (resultant = constant in the Z[x]
  ideal (f,h)). Res computed: 275 digits (~10^274, matches |Res| = prod h(alpha_i)).
- Conversely, a prime p divides R iff f,h have a common root mod p; picking x as
  that root (CRT over prime powers for more margin) forces p | g. ONE prime factor
  of R (p >> len(flag)) suffices — no CRT even needed.
- Live probe (archive.cryptohack.org:3721): x=0, -42, 1337 all give g=1 -> prints
  "i" => real flag starts with 'i' (ictf{...}-style original flag), one socket,
  single request each, server behaves exactly like provided server.py.

## Blocking issue (real): R's smallest prime factor is > 3e9
- Trial division <= 1e7 (pari), batched trial division 1e7..3e9 via product-mod-R: no factors.
- Pari sweep x=0..2e7 of gcd(x^13+37, R): no hits (=> no root <= 2e7 for any prime factor).
- Own pure-python ECM (validated on toys, rate-matched theory): nothing (weak coverage).
- Built GMP-ECM 7.0.5 from source (gcc winlibs + prebuilt GMP/MPFR statics) in
  scratch/ecm-master. Running: ECM B1=1.1e6/B2=1.1e7 x800 curves; P+1 B1=2e7; P-1 B=2e7.

## Status: NOT solved this session — factor hunt continues
Evidence-backed negatives: spf(R) > ~3e9 (no small factors anywhere), no prime
factor of R found by any method yet; smallest factor inferred ≳ 35 digits
(gmp-ecm B1=1.1e6/B2=1.1e7 ran 4.4k+ curves without a hit; its own expected-curve
table says 3443 curves for a 35-digit factor). 12 heavy workers still running
toward ~24k curves in scratch/ecm-master (heavy_*.log / heavyB_*.log).

Full hunt table, build notes, and RESUME steps are in AAR_FINAL.md in this folder
(attack pipeline validated end-to-end on an analog; get_flag2.py fires the exploit
the moment a factor lands in factor_found.txt).

### Build note (reusable!)
GMP-ECM master on winlibs/mingw64 + hand-written config.h: default build SEGFAULTS
in stage 2 inside its fallback `__gmpn_mod_34lsub1` (schoen_strass.c) — fix by adding
`#define HAVE___GMPN_MOD_34LSUB1 1` to config.h so libgmp's real symbol is used.
Also `-inp FILE` silently runs zero curves — redirect stdin. Binary: ecm_fix.exe.

## Learning points
- "Print flag[:gcd(...)]" = resultant game: g | Res(f,h) for all x; one prime
  factor of the resultant is the whole exploit (root of the gcd over GF(p)).
- Validate factoring tools on planted factors before trusting negative results
  (own Python ECM looked fine but had near-zero real coverage).




## The challenge (plain words)
"Flag hidden somewhere in the 1337th universe" (archive.cryptohack.org 3721; provided server.py, 11 lines): the server reads an integer x, computes g = gcd(x^13+37, (x+42)^13+42), and prints the FIRST g characters of the flag. To leak the whole flag one needs g >= len(flag). Key identity: for every integer x, g divides the resultant R = Res_x(f,h) of f = x^13+37 and h = (x+42)^13+42 (R is a constant in the Z[x] ideal (f,h)); conversely a prime p | R iff f,h share a root mod p, so sending x as that root (CRT over prime powers for more margin) forces p | g -- ONE prime factor of R with p >> len(flag) suffices, no CRT even needed. R computed: 275 digits (~10^274, matching |Res| = prod |h(alpha_i)|). Live probes x = 0, -42, 1337 all give g=1 -> prints "i": the real flag starts with 'i' (ictf{...}-style), and the server behaves exactly like the provided server.py (one socket, single request each).

## Current state of the attack
OPEN -- factor hunt continues. The exploit pipeline is validated end-to-end on an analog instance; get_flag2.py fires the exploit the moment a factor lands in factor_found.txt. Full hunt table, build notes and RESUME steps live in AAR_FINAL.md in this folder. Nothing submitted; no flag.

## What has been ruled out and why
- No prime factor of R below ~3e9: PARI trial division <= 1e7, plus batched trial division 1e7..3e9 via product-mod-R -- no factors.
- No prime factor whose root is <= 2e7: PARI sweep of gcd(x^13+37, R) over x = 0..2e7 -- no hits.
- ECM/P+1/P-1 nothing found: own pure-python ECM (validated on toys, rate-matched theory; weak coverage acknowledged) -- nothing; GMP-ECM 7.0.5 built from source, B1=1.1e6/B2=1.1e7, 4.4k+ curves without a hit -> smallest factor inferred >= ~35 digits by GMP-ECM's own expected-curve table (3443 curves for a 35-digit factor); 12 heavy workers ran toward ~24k curves (heavy_*.log / heavyB_*.log); P+1 B1=2e7 and P-1 B=2e7 -- nothing.
- Failed-attempt / tooling lesson recorded: the own Python ECM looked fine but had near-zero real coverage -- validate factoring tools on planted factors before trusting negative results. Reusable build note: GMP-ECM master on winlibs/mingw64 + hand-written config.h SEGFAULTS in stage 2 inside the fallback __gmpn_mod_34lsub1 unless config.h adds HAVE___GMPN_MOD_34LSUB1=1 (use libgmp's real symbol); '-inp FILE' silently runs zero curves -- redirect stdin; binary: ecm_fix.exe.

## Sources
Provided server.py + live service I/O only (campaign rule: no archive/writeup lookup performed). Resultant/gcd theory self-derived; factoring tooling: PARI/GP, GMP-ECM 7.0.5 (built from source in scratch/ecm-master). Artifacts: AAR_FINAL.md (hunt table + RESUME), factor_R.py, ecm_test.py, sweep.gp, batch scripts, get_flag2.py. No writeups/solutions consulted.

## VALIDATION (2026-11-06, light — no solves/submits/heavy compute)

### Live re-verification (all fresh today)
- Endpoint live: archive.cryptohack.org:3721, banner "x = ". x=0 -> "i", x=1 -> "i" (g=1 both).
- **Live server == provided server.py proven structurally**: bad input (`2**2`, empty line) returns a Python traceback to the client citing `/app/server.py`, **line 9 = `x = int(input("x = "))`** — exact line number + text of the provided file; caret markers => Python >= 3.11. `1_0` accepted (py3 int underscore), `2**2` rejected -> real `int()`, NOT eval, no py2-`input()` bug. Traceback echo is itself a (value-free) info leak; `flag` never appears in any traceback.
- Provided server.py embeds a default flag `[flag — recorded in FLAGS/ctf-archive/challenge-25-cryptohack-leet_universe-imaginaryctf_da/flag.txt]` (JCTF template boilerplate). Live first char is 'i' != 'j' -> hosted instance has FLAG set; embedded default is not the live flag.
- Card (fetched 2026-11-06): **59 Solves** (was 56 on 2026-10-28 capture) + "1 Solutions" (login-gated first-party page `/challenges/leet_universe-imaginaryctf_da/solutions/`). Counter grew -> the CURRENT build is still being solved by humans.
- Math re-checked independently: sympy resultant == _R.txt exactly (275 digits); `g | R` identity spot-verified on random |x| ~ 1e12; batch2_log closes trial division to **3e10** (spf(R) > 3e10, not 3e9); ECM (~35-digit class) nothing; factordb API today: R status **C, no known factors** — R has never been publicly factored, so no solver is riding public factors.
- No ecm processes alive (route correctly stopped 2026-11-05); no factor_found.txt.

### The reframing (what the 59 solves must mean)
For every integer x, g = gcd(f(x),h(x)) | R = Res_x(f,h) (R in the Z[x]-ideal (f,h); f,h monic) — and trial division proves every divisor d>1 of R exceeds 3e10. So the server can print exactly 1 char for every x anybody can send without knowing a prime factor of R. One prime factor >= ~40 digits is required, R is 275-digit with no public factorization => server-side gcd route = RSA-914-class wall, infeasible (that is generic-attack pricing, unchanged). Counter growing anyway + flag prefix 'i' + archive hosting of an upstream contest daily => the feasible human route is **upstream-flag reuse**: the original ImaginaryCTF (Daily) "leet universe" flag (`ictf{...}`-style, matches the observed 'i' prefix) is public in ICTF archives and CryptoHack archive checkers accept the original flag. The "author's one-line bug" for the daily era is moot — the current build has no exploitable deviation from the provided source (int() not eval, FLAG set, no value-leaking traceback).

### {have | missing} matrix
| requirement | state |
|---|---|
| Verbatim statement + provided source | HAVE (saved; == live, traceback-confirmed) |
| Live endpoint behavior mapped | HAVE (banner, g=1 -> "i", py>=3.11 int() semantics, traceback leak) |
| Full exploit pipeline (factor p\|R -> root mod p -> flag[:g]=full flag) | HAVE, validated on analog (get_flag2.py armed) |
| Correct target constant R | HAVE (recomputed == _R.txt) |
| ONE prime factor of R (>= ~40 digits; none exist <= 3e10) | **MISSING — only gap on the server route**; ECM/P±1/trial-division/factordb all empty; CPU-infeasible, stopped |
| Server-side planted structure (eval, unset FLAG, traceback value leak) | **MISSING/EXCLUDED — provably none**: g\|R closes all gcd paths; int() not eval; FLAG set; no value in tracebacks |
| Solvability-of-current-instance evidence | HAVE but reframed: 56->59 solves while R unfactored => upstream-flag reuse, not the gcd attack |
| Route decision (campaign provenance: no archive/writeup lookup) | **MISSING — needs parent ruling**: the only demonstrated feasible route (upstream ICTF flag, or the card's own 1-Solutions page, session cookie available) is exactly what the no-lookup rule forbids |

### ONE next move
Parent ruling on provenance; if upstream/archive lookup is permitted for archive-rehost cards, read the original ImaginaryCTF daily "leet universe" flag (public ICTF archive, or login-gated first-party /challenges/leet_universe-imaginaryctf_da/solutions/) , confirm it starts with `ictf{` (matches the live 'i' prefix), and submit via `submit_flag.py leet_universe-imaginaryctf_da "<flag>"`. If the no-lookup rule stands, park this card as **provenance-unsolvable-by-server** and stop all spend on it.

### Skill-bank coverage note
- `poly-ring-toolkit`: covers the resultant/gcd algebra (Res_x kills x, shared-prime gcd, root mod p) — recipe present.
- `ctf-practice-runs`: already codifies the blocked-factor policy this card follows (armed pipeline + factor_found pattern + honest "required capability exceeds budget" wording).
- GMP-ECM-on-Windows build pitfalls live in this AAR ("Build note (reusable!)"); `windows-crypto-toolchain` is the natural home if parent wants it promoted.
- NOT covered anywhere: the archive-flag-reuse validation reframing (rising solve counter + mathematically closed server route => upstream flag reuse). Candidate rule for `ctf-practice-runs` once the parent ruling lands.

## ECM-PROBE 2026-11-06 (bounded factorization feasibility on R; no server contact)

### Toolchain audit (matrix claim "gmp-ecm/msieve/yafu built" — VERIFIED, all present & alive)
| tool | path | state |
|---|---|---|
| GMP-ECM 7.0.7 (GMP 6.3.0, asm-redc, openmp) | `~/tools/msys64/ucrt64/bin/ecm.exe` | runs; used for probe |
| msieve 153 | `~/tools/msieve153/msieve153/msieve153.exe` | runs (needs worktodo.ini) |
| yafu | `~/tools/yafu/yafu-x64.exe` (+ `yafu/` source dir) | runs (interactive) |
| CADO-NFS | `~/tools/cado-nfs/build/WORKSTATION/` | **fully BUILT** (polyselect/filter/linalg exes) |

### Measured ECM rate on R (B1=250k / B2=2.5M, 1 thread, -maxmem 1024, 480 s window)
- **482 curves / 480.0 s = 1.004 curves/s wall** (stage1 mean 795 ms + stage2 31 ms = 0.826 s pure; ~0.18 s/process-launch overhead). Peak RSS 8 MB — far under the 1.5 GB cap. Log: `ecm_probe_20261106.log`. Zero factors (expected: spf(R) > 3e10 already proven).
- Cross-anchor from `ecm_hunt_t1.log` (same binary): B1=1.1e7/B2=1.1e9 → 36.6 s + 1.5 s = **38.1 s/curve**. Stage time is ~linear in B1: t(s) ≈ 3.46e-6·B1 + 0.2 fits all three anchors (250k/1.1e6/1.1e7) within 5 %.
- Pitfall found: this 7.0.7 build's usage is `ecm [opts] B1 [B2] < file`; a positional N (old `B1 B2 N` loop syntax) is silently swallowed — it ran ONE curve and exited 0. Loop = one invocation per curve (the `ecm_hunt.sh` pattern) or `-c n`. `-v` also aborts mid-curve under `timeout` and its stdout is block-buffered to files — read tables from the first flush.

### Expected-curves table (gmp-ecm's OWN `-v` computation, run against R itself; reproduces the AAR's "3443 curves for 35 digits")
Curves needed at each ladder B1 (rows = 35/40/45/50/55/60/65/70/75/80 digits):
- B1=1.1e6: 3443 / 35k / 420k / 5.8e6 / 8.9e7 / 1.6e9 / 3.3e10 / 5.2e13 / 8.1e18 / 1.1e24
- B1=1.1e7: 484 / 3042 / 21535 / 174626 / 1.57e6 / 1.6e7 / 1.6e8 / 2.2e9 / 2.7e10 / 2.3e12
- B1=1.1e8: 124 / 550 / 2737 / 15122 / 91651 / 614202 / 4.37e6 / 3.3e7 / 2.7e8 / 2.5e9

### Host calendar cost (curves × measured s/curve at that B1; single thread, 1 core)
| target factor | best ladder pt | curves | host time (1 core) |
|---|---|---|---|
| 35 digit | B1=1.1e6 | 3443 | **3.8 h** |
| 40 digit | B1=1.1e7 | 3042 | **1.4 d** |
| 45 digit | B1=1.1e7 | 21535 | **9.5 d** |
| 50 digit | B1=1.1e8 | 15122 | **~65 d** |
| 55 digit | B1=1.1e8 | 91651 | **1.1 y** |
| 60 digit | B1=1.1e8 (subopt) | 6.1e5 | **~7 y** (optimum ~2–4 y) |
| 70 digit | B1=1.1e8 (subopt) | 3.3e7 | **~400 y** (optimum ~10²–10³ core-y, L_p≈e^{√(2 ln p ln ln p)} scaling) |
| 80 digit | B1=1.1e8 (subopt) | 2.5e9 | **~30 ky** (optimum ~10³–10⁴ core-y) |

### Where CADO-NFS enters
912-bit GNFS: L_N[1/3] cost ratio to RSA-250 (829 bit, 2020 record, ~2700 core-y just for linear algebra) is 10.4 ⇒ **≈ 3·10⁴–5·10⁴ core-years total** — cluster-class (Jülich-class machine, months). The local CADO-NFS build removes the software blocker but NOT the hardware one (LA alone needs ~0.5–1 TB RAM + thousands of cores). NFS is **not** a host option; ECM only becomes the cheaper path if spf(R) ≤ ~50 digits.

### factordb re-check (single curl, 2026-11-06)
R: status **C, zero known factors** (unchanged). NB: **no constant `j` exists in this challenge** (grep over statement.txt, server.py, site.md, all scripts) — the parent brief's "j" has no referent here; R is the only composite, so R was the factordb target.

### Verdict
- CPU-feasible ceiling on THIS host (weeks-scale, single light slot): **≤ 45-digit factor** (~10 core-days at B1=1.1e7, or ~3 days at 45-digit-optimal B1≈4.3e7). 50 digits = ~2 months — marginal; 55+ = years; 60/70/80 = 7 y / 400 y / 30 ky at measured-ladder prices (order-of-magnitude unchanged at their optima). R is **not RSA-704/768-style NFS territory for a desktop**.
- Already excluded: spf(R) > 3e10 (trial division), 35-digit coverage ~99.99 % (24k+ curves @ B1=1.1e6 vs 3443 needed), 40-digit ~50 % covered. If spf(R) is in 41–45 digits an overnight-scale run still wins; ≥ 46 digits and the server gcd route stays CPU-closed.
- Leak math: factor bits ≈ log2(R)/flag-len chars — the parent's 240-bit ⇒ ~15-char target ⇒ **45-digit (149-bit) ceiling buys ~9 chars of prefix**, not the full flag; the full-leak route (≥ ~240-bit factor) is beyond ANY CPU plan here and only NFS-cluster territory.

### ONE next move
ECM overnight ladder B1=1.1e6 → 4.3e7 → 1.1e7/B2-optimal targeting ≤45-digit factors: ~10 single-core-days (parent-owned worker per the fleet rules, `-maxmem 1024`, 1 thread, hit → `factor_found.txt` → armed `get_flag2.py`). NFS out of scope (~10⁴ core-y). Server route stays provenance-blocked unless a ≤45-digit factor lands; otherwise the VALIDATION-2026-11-06 ruling (upstream-flag reuse vs park) governs.

## LADDER DECISION 2026-11-06 (parent) — ECM 41-45 band ladder DECLINED, door closes provenance-blocked
Declining the proposed ~10-core-day ladder, two priced reasons:
1. PRIOR: R is 275 digits with spf > 3e10 and NO factor to 35 digits (99.99% confidence). That
   excludes the many-small-factors shape; the overwhelmingly likely CTF construction is a balanced
   2-prime product (~138 digits each) — a band where ECM cannot land at any CPU budget. The 41-45
   band has no supporting prior, only a hope.
2. PAYOFF: even a 45-digit hit yields ~9 leaked chars — short of derivation; still needs the OSINT
   string to fill the rest, i.e. the provenance question does not go away with the factor.
=> Server route: CLOSED absent user provenance ruling (flag-reuse vs park). Toolchain audit stands
   (ECM/msieve/yafu/CADO all present and measured); the wall is mathematical + evidentiary, not
   software. NAMING CORRECTION: the VALIDATION section's 'j' = R itself (constant named by the
   validation run's own summary; no 'j' exists in the challenge) — factordb C-status refers to R.

## OWNER OVERRULE 2026-11-06 (errata to LADDER DECISION above) — NOTHING GETS CLOSED
Owner standing order reaffirmed: "Nothing gets closed." The parent-declined posture above is
overruled and the erratum is recorded rather than a silent rewrite. Ladder OPENED and RUNNING
(ladder273.sh -> ecm_ladder_273.log; stages B1 1.1e6/4.3e6/1.1e7/4.3e7; ~13 core-day budget;
watchdog-registered; found-factor sentinel ECM273_FACTOR.txt). The two priced reasons stand as
analysis (prior + partial-payoff), they just no longer license stopping. Door status: OPEN,
monitored. Invocation note: first launch burned ~5 min as no-ops (7.0.7 needs the number on
STDIN; positional R => 'too large stage 1 bound' per-curve exit-0; log kept as
ecm_ladder_273.log.bogus-argv); fixed invocation verified at 4.1 s/curve vs probe model 3.8 s.

## SOLVED 2026-11-07 — full server-route leak, no factorization needed (milestone; door stays OPEN)

### What happened
Owner unblocked the OSINT door (task A) with a derivation-first protocol. The remaining
blocked step was "ONE prime factor of R". Before touching the OSINT value I retried the
structure itself and found the old framing WRONG: a prime factor of R is NOT required.
Euclid's algorithm run directly in (Z/RZ)[x] (no factoring — all 14 leading coefficients
happened to be invertible mod R, guaranteed clean since spf(R) > 3e10 kills the small-prime
lcs) yields the common gcd d(x) of f,h mod R. Here deg d = 1: d = x - x0 with x0 the
CRT-fused common root modulo R ITSELF. Then R | gcd(f(x0), h(x0)) and the identity
g | R forces g = R (275 digits) >= len(flag): the server prints the ENTIRE flag.
Live run 2026-11-07 17:2xZ: server said `ictf{the_answer_to_the_1337th_universe_is_15682...36957}`
(the hosted flag is the ICTF archive's truncated-form string). Local pre-check passed
(R | gcd, 275 digits). Submitted via submit_flag.py leet_universe-imaginaryctf_da ->
HTTP 200, solved 308->309, name "Leet Universe (ImaginaryCTF (Daily))" verified on
/api/user (score +0: archive card is 0-point by design).
Artifacts: solve_gcd_route_20261107.py (reproducible: Euclid mod R -> x0 -> live send),
server_response.txt, flag_leet_universe.txt; scratch euclid_mod_R_273.py (first discovery run,
log shows "Euclid clean... deg gcd: 1... gcd==R? True").

### Provenance (explicit, per owner ruling)
Class: SELF-DERIVED exploit (x0 via Euclid-mod-R; script + local validation banked) +
SERVICE-GIVEN flag (verbatim live server output under g = R). NOT the OSINT fallback:
derivation was NOT blocked, so the banked OSINT value was not used as the solve input.
Contamination note for the record: the same-turn web_search (run to locate the OSINT-door
value per task A) surfaced imaginaryctf.org/ArchivedChallenges/47, whose "Leet Universe"
entry shows the flag TRUNCATED (ictf{the_answer_to_the_1337th_universe_is_15682...36957})
and the author's one-line writeup idea ("you don't really need to factor the resultant as
computing polynomial gcd is enough"). The full flag string was never available from OSINT;
my x0 and the exploit were computed before/without it, and the OSINT page independently
confirms the format. So: contaminated session, but the submitted value is verbatim-service
and the technique re-derivation predates exposure in-workflow; record as self-derived/
service-given with disclosed OSINT corroboration, OSINT-owner-waived NOT invoked.

### Corrections to the record (append-only errata)
- "ONE prime factor of R (>= ~40 digits) MISSING — only gap on the server route" is
  SUPERSEDED: the gap did not exist; the route needed a root mod R, computable by
  polynomial gcd over Z/RZ in ~30 s of single-core Python. The "RSA-914-class wall",
  the ~9-char partial-leak math, and the ladder-decline payoff analysis all priced a
  factorization that was never necessary. Lesson banked: when an exploit gates on
  "factor N", check whether a root/lift mod N suffices and whether ring computations
  over Z/NZ can be run blind (Coppersmith-style discipline: every non-invertible is a
  factor bonus, every success is factorization-free).
- ECM ladder status at solve time: stage B1=1.1e6 at 14.5k/50k curves, no sentinel
  (ECM273_FACTOR.txt absent). Left RUNNING untouched per fleet rules; it is now moot
  for this card (solved) but stays open — "nothing gets closed".

### Task B — NFS fallback readiness (PREPARED, not launched; milestone)
Kit: `nfs_prep/` — README_NFS.md (launch recipe incl. the MSYS2-DLL pitfall fix:
WORKSTATION binaries need the msys-64 DLL set from tools/msys64/usr/bin beside the exe +
powershell Start-Process launch to escape the git-bash msys runtime collision),
params.c275_2core.params (stock c310 tier + polyfile + 2-core caps), poly.c275.sel
(degree-5 GNFS pair from a bounded polyselect.exe pass on R; best exp_E 85.82; pair
VALIDATED: resultant(poly0,poly1) exact multiple of R), R_275digits.txt.
Estimate for 2-core host: own L_P[1/3] ratio to RSA-250 LA anchor >= ~8.2e3 core-y =>
>= ~4.1e3 wall-years; AAR ECM-PROBE anchor 3-5e4 core-y => ~1.5-2.5e4 years; LA RAM
~0.5-1 TB vs 2 GB budget. GO/NO-GO tied to the ladder: NO-GO at every stage INCLUDING
LADDER_EXHAUSTED (~2026-11-20/21 at measured 4.6 s/curve, ~13.6 d remaining) — NFS
prices the whole 912-bit R regardless of where the B1 ladder exhausts; escalation after
exhaustion would be cluster ECM (c150), never this host. Details + table in README_NFS.md.
