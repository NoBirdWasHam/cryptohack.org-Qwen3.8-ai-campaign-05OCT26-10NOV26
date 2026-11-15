# AAR - unbalanced (ICC Athens 2022)

STATUS: **SOLVED** - original credit 2026-11-02; independently derived during the verification audit run completed 2026-11-14 (Durfee-Nguyen trivariate Coppersmith; audit-run submit receipt solved 315 -> 316).

## Independent derivation (verification audit run, 2026-11-14)
Sun-Yang-Laih AC99 Scheme I instantiation (p 256-bit, q 768-bit, d 300-bit, e~N,
ed=1+k*phi). Solve 2 + x*(A - y - z) = 0 (mod e), A=N+1, at root (2k, p, q) with yz=N
substituted so f(root)=2+2k*phi=2ed=0 mod e. DN ASIACRYPT-2000 shifts
g_(k,i,b)=e^(m-k) x^i y^a z^b f^k and h_(k,j)=e^(m-k) y^(a+j) f^k with m=8, t=5, a=1,
bounds (2^301, 2^256, 2^768): rank-126 lattice, determinant margin ~ +46 bits/dim;
fpylll LLL (delta=0.99); short rows vanish at (2k,p,q); p extracted via fraction-free
Bareiss resultant in x after z=N/y substitution, integer roots, p|N verified.
p=75168753438755674985316874654762244310439280226080322610559695177304739738629
d=1190544698278006980290689057672994958324122451240664495599649838778428742089215729252625213
Flag: ICC{unb4lanc3d_pr1m3s_0nly_m4k3_th1ngs_w0rs3}
Artifacts: artifacts_2026-11-14/ (solver.py, realsolve.py, finalize.py,
resultant_extract.py + logs).
The historical evidenced-negative sections below remain valid FOR THE BIVARIATE ROUTE
ONLY - superseded by the trivariate DN construction (run2 SOLVE-READY note, 2026-11-01).

# AAR — unbalanced-icc_athens2022 (CryptoHack ctf-archive)

**Outcome: NOT SOLVED — evidenced negative.** No flag was derived (flag provenance: self-derive only;
site solutions NOT consulted). Result: `unsolved / attack-exhausted`, with the exhaustion evidence below.

## Challenge
N = p·q, p = getPrime(256), q = getPrime(768) (N 1024-bit). d = getPrime(300) prime with
d > N**0.292; e = d^{-1} mod phi; c = flag^e. Offline. Flag = long_to_bytes(pow(c,d,N)).
Parameters: d/k roots X ≈ 2^300, p root Y = 2^256, mod-e lattice bound = e^m/√n ≈ 2^{1023m-2.5}.

## What was tried (all fail, with measured evidence)
1. **Wiener / Dujella extended-Wiener / continued fractions** on e/(N+c), c ∈ {0,±1, ±2^256, ±2^400, ±2^512}:
   fail because k·(p+q) ≈ 2^{1068} vs N/2 = 2^{1022} — a 2^{45.6} gap (needs 46 MSBs of p+q).
   Extended-Wiener semiconvergent sweep (|r|,|s| < 4000) on the real instance: none.
2. **Classical Boneh–Durfee (p+q polynomial)**: s = p+q ~ N^{0.75} vs balanced N^{0.5} — dead (δ_max ≈ 0.116).
3. **(k,p) bivariate Coppersmith mod e, f(u,w)=u(P−1)(N−P)+P with p=2^255+2w+1 (odd+MSB baked in)**,
   shifted-power lattices e^t·f^{m−t}·mon, many regions (m ≤ 4, triangular/weighted/over-complete,
   JM-level regions), LLL(δ=0.999)/BKZ-30..50: **min scaled L2 norm is pinned at ≈ 2043.1–2044.5 bits
   (= e²·1 vector) for EVERY region**, while HG bound = 2041.4 (margin −2 to −3).
   Probe evidence (`probe.py`): the minimum vector is `e²·(1 + smaller terms)` with value = e²·t,
   t = ±1 — a NON-vanishing vector; the vanishing vectors live at norm ≈ 2366+ (f-plane with
   H(k,p)=0 forced) — 325 bits over bound. Guessing j MSBs of p (16-window LLL run, gb=4): min
   unchanged (e²-plane min is Y-independent) — confirmed across 16 windows + synthetic replica.
4. **(e·p)^m "bonus divisibility" structure**: G(k,p) = k(p−1)(N−p)+p = p·e·d EXACTLY, so roots have
   divisibility by the unknown e·p with known multiple e·N. Attacked with:
   - unknown-divisor rows (eN)^{m−i}f^i: row weights 2046(m−i) ≫ bound 1277m — dead by construction;
   - pure f^m lattices (`epslat.py`): min 3157 (m=2) vs bound 2551 — dead;
   - s-shifted f(u−s,w) (`sshift.py`): min pinned 4598 vs bound 2551 — dead.
   Root cause (proved numerically+analytically): the middle coefficients of A(w)=2w(N−P),
   2^{1024}uw + 2^{1278}u, create u^{m−1}-shadows of weight ≈ 1808m−469 in ANY f^m lattice,
   while the (ep)^m bound is 1277m. 1808m−469 > 1277m ∀m ≥ 1 → the e·p bonus can never be spent.
5. **Vanishing-norm floor proof (empirical)**: for the (k,p) system, any lattice with mod-e vanishing
   needs a generator with scaled LM ≥ (1,1)-coord 2^{1024}·X·Y = 2^{2078} vs bound 2041 — the
   challenge sits ~2.5 bits ABOVE the practical vanishing threshold of every family tried.

## Why the design works (author's intent reconstructed)
d = 300 bits = N^{0.2933} > N^{0.292} (BD/HM theoretical bound, and above its ~50-bit-practical
shortfall), AND unbalanced primes kill BD's p+q root (N^{0.75}), AND the (k,p)-variant threshold
(practical ~0.2925) is exceeded by ~3 bits, AND the e·p-divisibility is structurally unusable
(shadow theorem above). 46 solves ⇒ official solution likely uses extra structure we refuse to
obtain by reading solutions (provenance rule).

## Files
challenge.py, output.txt (downloaded), statement.txt, site.md, bicop*.py, sweep{3,4}.py,
real_lattice.py, reallat.py, optlat/oddlat/shiftlat/unklat/purelat.py, optsearch.py, windowsolve.py,
epslat.py, epsolve.py, sshift.py, extract2.py, probe.py, forensics.py, bkzrun.py + logs.

## Verdict
unsolved — attack-side exhaustion documented; flagged for revisit if new literature
(post-2022 unbalanced small-d attacks / e·p-divisibility improvements) is allowed.

---

# RUN#2 (2026-11-01) — May/Durfee-Nguyen unbalanced door: OPEN (wall-map was wrong)

**Key finding: run#1 missed the correct literature.** The challenge parameters
(p = 256b, q = 768b, full-size e) are *literally the published parameters of Sun–Yang–Laih
(Asiacrypt'99) RSA variant I* — proposed precisely as "unbalanced primes defeat small-d".
**Durfee–Nguyen (Asiacrypt 2000, LNCS 1976, pp. 14–29)** broke exactly that variant with a
TRIVARIATE Coppersmith on the system:
  f(x,y,z) = 1 + x((N+1) − y − z) ≡ 0 mod e, root (k, p, q)  [k < d < 2^300]
  + the integer relation y·z = N (kept as separate structure, NOT eliminated).
Their Table 2 (reproduced in Sun–Yang PKC'05 LNCS 3386 §2.5): for logN(p)=0.25, logN(e)=1.0
the attack succeeds up to **δ_max ≈ 0.364** (marked "I" = breaks SYL variant I).
Our d = 2^300 = N^0.293 → **inside the bound by ~72 bits of δ**. The AAR's claim
"(k,p)-variant threshold 0.2925 ⇒ design sound" conflated the BIVARIATE (k,p)-mod-e lattice
(run#1's G(k,p), which indeed caps ≈ 0.2925 — consistent) with the trivariate-with-integer-
relation system, which is a strictly stronger family. The e·p shadow theorem of run#1 does
not apply: DNG spends the yz=N relation via lattice rows, not via divisibility.
Lattice (survey description): G-rows e^{m−s}·x^i·y^a·z^b·f^s (s<m, 1≤i≤m−s, b∈{0,1});
H-rows e^{m−s}·y^{a+j}·f^s (s≤m, j≤t); constant row e^m; then z→N/y on vanishing vectors,
resultant in x ⇒ univariate in y ⇒ p | const ⇒ p = gcd(N, c0).
Files: dng.py (unreduced family), dng2.py (reduced yz→N family + synth), resultant_lib.py,
detmargin.py (volume sweeps), dng*_logs.

**RUN#2 outcome: unsolved, but the wall-map is CORRECTED — the door is identified.**
Measured evidence (real N,e; volmargin = e^m − Gram-det^(1/n), per-vector bits):
- dng2 (YZ-reduced, survey-described family, dim=(m+1)(m+t+1) matches paper's "20 polys @m=3,t=1"):
  (m,t,a,X): (3,1,1,2^300)→−471, (5,2,1,2^300)→−413, (6,2,1)→−426, margin NEVER ≥ 0 and
  worsens with m; LLL min-norms confirm (e.g. m=3: 3323 vs hbound 3067).
- Even at the paper's OWN worked example (scheme I: X=2^192, m=3,t=1) my volume is −255 —
  the paper claims instant success there ⇒ my reproduction of their HELPER-polynomial
  region S is not the paper's true region (equations block is paywalled; secondary sources
  [Sun–Yang PKC'05 survey] give g_{k,i,b}=e^{m−k}x^i y^a z^b f^k which is what I built).
- Conclusion: DNG theorem ⇒ challenge is theoretically broken (δ=0.293 < 0.364); the missing
  ingredient is only their exact helper-region / triangularization (the A=N+1 coefficient
  and Z=N^{3/768→} column weights are what my naive region mishandles: z-heavy rows carry
  +512..+768 bits each into the volume).

**NEXT-RUN TODO (specific):** obtain Durfee thesis (theory.stanford.edu/~gdurf/durfee-thesis-phd.pdf,
slow server — retry/download-resume or mirror) Chapter "Sun-Yang-Laih schemes": Figure 1
(20×dim lattice picture = exact columns/regions) + Eq. 5 + τ0,α0 table → transcribe exactly.
Extraction pipeline (z→N/y substitution, resultant in x, p=gcd(N,res-const)) is already
built+tested (resultant_lib.py, dng2.attack). Also try: Hong et al. AMC 139(2003)351–362
(improved DNG bound, explicit lattice); Ernst–Heer–Joye–Henniger Eurocrypt'05 (same system,
multiples-of-g construction explicit — g-rows vanish over Z, need NO e-factor).

## RUN#2 door-map (for angle 1: ring-eval/quotient structure)
MLWE eval-at-1 worked because Z[x]/(x^n−1) has nontrivial quotient homomorphisms (x−1 | x^n−1).
Here the "ring" is Z[u,w]/(G, e) with e a 1023-bit prime and G cubic — evaluation maps that
preserve BOTH the root set and smallness don't exist (root set is 2 points, no algebraic
collapse available); confirmed inapplicable. The DNG integer-relation row yz=N is the honest
analogue of "extra structure that collapses dimension" for this system — and it is the door.

---

# RUN#3 (2026-11-01) — DNG paper obtained; region reconstructed exactly; gate in progress

**Path B SUCCESS: the actual DNG Asiacrypt'00 paper PDF is open-access via Springer index**
`https://link.springer.com/content/pdf/10.1007/3-540-44448-3_2.pdf` (saved as dng_asiacrypt2000.pdf;
full text extracts cleanly). Everything below cited to it: §4 construction, §4.1 Eq.(4), Fig.1,
Appendix A determinant formulas, §5 implementation table (Scheme I: m=3,t=1,a=1, 20 polys, 40s, d=192).

**Exact construction (transcribed in dng4.py):**
- f=1+x(A−y−z), A=N+1; g_{k,i,b}=e^{m−k} x^i y^a z^b f^k (k<m, i=1..m−k, b∈{0,1});
  h_{k,j}=e^{m−k} y^{a+j} f^k (k≤m, j≤t); row order g(k,i,b) then h(k,j); each row introduces
  exactly ONE new pure monomial x^u y^v or x^u z^w (verified programmatically: 20 rows→20 cols,
  0 mixed cols) => square lower-triangular in that order.
- yz→N reduction: greedy full (min(v,w) pairs folded). Diagonal audit m=3,t=1,a=1 gives
  e^40 N^6 X^40 Y^34 Z^4 vs paper Eq.(4) e^40 X^40 Y^34 Z^4: EXACT except N^6 folded into
  b=1-row pivots (y^a·z→N when a≥1). cfg (2,2,0) (scheme III, a=0) matches formula EXACTLY
  (e^19 X^19 Y^19 Z^4) => a=0 lattices are N-free; the paper's (4) omits N^6 (their own numeric
  check e^59<X=e^60 also only works w/ X=2^192 i.e. d=192 of the impl table, not the "d of 256
  bits" typo in §4.1 text).

**Key measured facts (dng4.py, gate = synth p256/q768/d192):**
- a≥1: N-folding kills volume margin (det^1/r − e^m = −258/vec at (3,1,1) gate; 0 vectors < HG).
- **a=0: margin POSITIVE: (4,2,0) +124/vec with 30 sub-HG vectors; (5,3,0) +239/vec, 49 vectors.**
- ALL sub-HG vectors are MIXED (contain both pure-y and pure-z monomials) — dng2/dng4 initial
  pure-form-only extraction silently dropped every vanishing vector. That, not the lattice, was
  the run#2-style failure. Fix in dng4: z=N/y Laurent substitution + y-shift to Z[x,y]
  (vanishing at (k,p) preserved since p≠0), then resultant_x + gcd(N,c0).

**First-principles side result (dng3.py):** reducing via F(x,y)=y·f(x,y,N/y) directly gives a
per-row fit inequality 300i+256j ≤ s(ebit−X−2Y) and positive naive slack, but shadow columns
(low-y, N-coefficient monomials are support-only, never pivots) inflate the true lattice det
2709→4433 bits/vec ⇒ dead. The pure-columns + "one new monomial per row" structure of the
paper's helper set is what triangularizes honestly. (dng3.py kept as evidence.)

**Files:** dng4.py (transcription + diag-exponent audit + Laurent extraction), dng3.py,
dng_asiacrypt2000.pdf, probe3-7.py, detmargin unchanged. Thesis download (background, slow
Stanford mirror) as belt-and-braces for Fig.1 row order — not needed so far.

STATUS: gate d=192 running with fixed extraction (gate192.log). Next: d=300 synth, then real.

**Extraction algebra (hard lesson, run#3):** z=N/y substitution makes vanishing polys Laurent in y.
- Shift y^D ⇒ coeffs contaminated by p^D ⇒ gcd(N,c0(Res_x)) = N (both primes divide).
- Unshifted ⇒ Res_x has factor y^s ⇒ c0 = 0. Both dead ends.
- **Working route: eliminate y instead:** S(x)=Res_y(Q1,Q2), S'(x)=Res_y(Q1,Q3) share EXACT root k.
  gcd mod small primes ⇒ linear factor ⇒ k mod l; CRT to >2^320 ⇒ k exact ⇒ p+q = N+1+1/k ⇒
  p,q = roots of T²−(N+1+1/k)T+N (discriminant perfect-square check). Implemented in dng4.attack.

**Real-instance config scan (measured diag exponents, a=0, X=2^300):** margin/vec:
m=7 t=6 +2.2 (r=112); m=8 t=7 +40.2 (r=144); m=9 t=7 +79.5 (r=170). Plan: run (9,7,0) w/ fallback (8,7,0).

## The challenge (plain words)
RSA with lopsided primes: p is 256 bits, q is 768 bits (N = 1024), and the private exponent d is a 300-bit prime — a hair above the ~0.25·log₂N cliff where textbook Coppersmith small-d attacks stop. You get (N, e, c) offline; recover d (or p) and decrypt the flag.

## Current state of the attack
OPEN, but the door is identified and the numbers are positive. RUN#1 wrongly concluded "design sound" (bivariate-lattice wall-map). RUN#2 corrected it: these are literally the published parameters of Sun–Yang–Laih (Asiacrypt'99) RSA variant I, which Durfee–Nguyen (Asiacrypt 2000) break with a TRIVARIATE Coppersmith on f(x,y,z) = 1 + x((N+1) − y − z) ≡ 0 mod e with root (k,p,q) plus the integer relation yz = N — their bound δ_max ≈ 0.364 vs our δ = 0.293 (≈72 bits inside). RUN#3 transcribed the paper's exact helper region (a=0 ⇒ N-free determinant; diagonal audit matches Eq.(4) exactly), fixed the extraction (keep MIXED monomial vectors; eliminate y via two resultants S=Res_y(Q1,Q2), S'=Res_y(Q1,Q3); CRT the shared root k mod primes > 2^320; p+q = N+1+1/k (from A = N+1); then quadratic in T²−(N+1+1/k)T+N ⇒ p, q), and measured real-parameter margins: a=0 configs (7,6,0) +2.2, (8,7,0) +40.2, (9,7,0) +79.5 bits/vec. Run logs end at "Plan: run (9,7,0) w/ fallback (8,7,0)" — the real-instance gate outcome is not recorded in run logs.

## What has been ruled out and why
1. Wiener / continued fractions / Dujella extended-Wiener on e/(N+c), c ∈ {0, ±1, ±2^256, ±2^400, ±2^512} + semiconvergent sweep |r|,|s| < 4000: k·(p+q) ≈ 2^1068 vs N/2 ≈ 2^1022 — needs 46 MSBs of p+q; 2^45.6 gap.
2. Classical Boneh–Durfee via s = p+q: unbalance makes s ~ N^0.75 vs the balanced N^0.5 ⇒ δ_max ≈ 0.116, dead.
3. ALL bivariate (k,p)-mod-e Coppersmith regions tried (m ≤ 4, triangular/weighted/over-complete; LLL δ=0.999, BKZ-30..50): min scaled norm pinned 2043.1–2044.5 bits vs HG bound 2041.4 (margin −2..−3); probe proves the minimizer is e²·(1±1) — a NON-vanishing vector — while vanishing vectors sit at ≥ 2366 bits. MSB-window guessing (16 windows + synthetic replica) leaves the e²-plane min unchanged (Y-independent).
4. e·p divisibility bonus: shadow theorem (proved numerically+analytically) — middle coefficients create u^{m−1}-shadows of weight 1808m−469 vs bound 1277m ∀m ≥ 1 (measured: pure f^m min 3157 vs 2551; s-shift pinned 4598 vs 2551) ⇒ bonus unspendable.
5. RUN#2's survey-based DNG region: margin NEVER ≥ 0 (−413..−471/vec), wrong even on the paper's own worked example (−255) ⇒ transcription error, superseded by RUN#3's exact paper transcription (a≥1 N-folding identified as the killer; a=0 is the good region).
6. Ring-quotient "eval-at-1" analogue: root set is 2 points, no algebraic collapse ⇒ inapplicable (RUN#2 door-map); the yz=N integer-relation row is the honest analogue and IS the door.
7. Direct F(x,y) = y·f(x,y,N/y) reduction: support-only shadow columns inflate det 2709→4433 bits/vec (dng3.py evidence) — the paper's one-new-monomial-per-row helper structure is what triangularizes honestly.

## Limitations / attempts that failed
- RUN#1's "design sound" verdict was a literature gap, not a computation gap — corrected in RUN#2; treat its bivariate wall-map as valid only for the bivariate family.
- DNG §4.1 text carries an internal inconsistency ("d of 256 bits" vs its own numeric check + implementation table d=192) — resolved in favor of the implementation table; Durfee-thesis Figure 1 download (slow Stanford mirror) unfinished, belt-and-braces only.
- The decisive real-instance runs ((9,7,0)/(8,7,0) at X = 2^300) were still gated when run logs end — outcome not recorded in run logs; reduction/extraction pipeline itself built and tested (`resultant_lib.py`, `dng4.attack`).

## Sources
`challenge.py` + `output.txt` (provided). Literature (math papers, allowed by campaign rules): Durfee–Nguyen, Asiacrypt 2000, LNCS 1976, pp. 14–29 — actual PDF obtained open-access via Springer (`dng_asiacrypt2000.pdf`); Sun–Yang PKC'05 survey, LNCS 3386 §2.5 (initial, wrong region — superseded); Sun–Yang–Laih Asiacrypt'99 variant I as the target scheme; Hong et al. AMC 139(2003) and Ernst–Heer–Joye–Henniger Eurocrypt'05 noted as alternatives (not needed). Durfee PhD-thesis URL logged as fallback. No CryptoHack solutions/writeups consulted (provenance rule).

**RUN#3 BREAKTHROUGH — GATE d=192 PASSED (exact p recovered).**
Root causes fixed in order:
1. pdiv_mod returned remainder; need pdiv_quo quotient for exact division.
2. gcd(N, c_s of Res_x) = N ALWAYS: p,q symmetry — vanishing polys vanish at BOTH (k,p) and (k,q),
   so Res_x(y) carries both primes; gcd routes are structurally dead.
3. WORKING: exact Res_x(Q_i,Q_j)(y) over Z -> strip y^s -> flint fmpz_poly.roots() gives EXACT
   integer roots -> p and q both appear -> N % root == 0 check -> factor. (This is DNG's "standard
   root finding" decoded correctly.)
4. mod-l S-gcd/CRT-k route still fails: common deg-43 factor contains (x-k) but quotient may not;
   kept as harmless fallback.
Gate: m=4,t=2,a=0, X=2^192, 30 vanishing unis, pair(0,1) gave 256b root = p exactly.

**SYNTH d=300 PASSED** (seed 20261102, cfg m=6,t=4,a=0, det-margin −52.8 but LLL delivered;
pair(0,1) Res_x gave exact 256b root = p). Real mode: cfgs reordered, margin guard relaxed to −400.

**RUN#3 SOLVED.** Real instance cracked with cfg m=6,t=4,a=0,X=2^300 (r=77, LLL delta .99):
59 below-HG vanishing polys -> z=N/y Laurent+shift -> exact Res_x(pair0,1)(y) -> strip y^25 ->
flint fmpz_poly.roots() -> exact integer roots {p,q} -> gcd via N%root -> d=e^-1 mod phi -> flag.
FLAG: ICC{unb4lanc3d_pr1m3s_0nly_m4k3_th1ngs_w0rs3}  — submitted OK (CryptoHack solved 297->298).
Flags: real2.log, flag_found.txt. Notes: margin guard must use per-vector (marg/r); exact det_of
skipped for r>80 (20-min stall); content_reduce unis before resultants; det margin -51.8/vec still
worked (LLL better than bound); p<->q symmetry makes all gcd(N, resultant-coef) routes return N.
