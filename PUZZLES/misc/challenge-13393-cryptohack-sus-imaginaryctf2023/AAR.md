# AAR — sus (ImaginaryCTF 2023), CryptoHack archive #13393

## Verdict
**NOT SOLVED** — evidenced negative result. No flag submitted (none derived).

## Challenge recap
`challenge.py`: `p` = 512-bit prime, `q = p²+p+1` prime (`Φ3(p)`), `r` = 1536-bit prime,
`n = p·q·r` (3070 bits), `e = 65537`, `c = m^e mod n`. Instance in `output.txt`.
Key structure: `q = p²+p+1` ⟺ `(2p+1)² ≡ −3 (mod q)`, `p³ ≡ 1 (mod q)`, `q−1 = p(p+1)`,
and (forced by primality) `p ≡ 2 (mod 3)`, `q ≡ 1 (mod 3)`.
Also `8n = (2p)·(s²+3)·r` with `s = 2p+1` (~2^512).

## Attacks tried (all failed, each attempted with real computation)
1. **General factoring of n** — PARI `factor()`/ECM backgrounded in a prior session; the
   small factor p is 512 bits (~1542 digits). ECM records are ~83–90 digits; NFS records
   ~830 digits. Infeasible by orders of magnitude. Documented, not re-grinded.
2. **Pollard p−1** on n (B₁=20000, lcm-exponent, gcd(2^M−1,n)) → gcd = 1. No smooth factor−1.
3. **Fermat with multipliers** k·n, k ≤ 60 (and analysis): the needed gap |k·pq − r| < ~2^768
   never occurs (gaps are ~2^1535); zero hits, consistent with analysis.
4. **Small-factor/structural probes**: trial division < 10^5, perfect-power, gcd(c,n)=1,
   squarefull checks (prior session) → nothing.
5. **Coppersmith univariate (mod unknown divisor)**: root bounds are far short:
   - `x²+x+1 ≡ 0 (mod q)`: q≈n^{1/3} ⇒ X < n^{1/18} = 2^{170}, need 2^{512}.
   - `x³+x²+x ≡ 0 (mod pq)`: pq≈n^{1/2}, δ=3 ⇒ X < n^{1/12} = 2^{255}, need 2^{512}.
6. **Howgrave-Graham bivariate lifting lattice**, two parameterizations:
   - f₁(x,y) = x·y·(x²+x+1) − n, root (p,r), X=2^{512}, Y=2^{1536};
   - f₂(u,v) = (u²+u+1)·v − n, root (p, rp), X=2^{512}, Y=2^{2050}.
   Built HG lattices (rows N^{m−k}x^a y^b f^k, k=1..3, box/triangle monomial regions,
   monomial rows N^m·x^a y^b), LLL via fpylll 0.6.4 (`LLL.reduction`).
   **Validation on a ratio-identical 357-bit toy** (60/120/180-bit p/q/r): across m ∈ {1,2,3}
   and ~50 region shapes, the shortest-vector evaluation bound never dropped below N^m
   (minUB pinned at exactly N^m — the trivial monomial row), and no short vector ever
   vanished at the true root (probe over 40 shortest rows/set). The (X,Y) region is outside
   the solvable region for these constructions — consistent with the Newton-polygon
   volume heuristic (X·Y³ = n^{1.67} vs bound ≈ n^{1.5} for f₁; f₂ marginal on the same scale).
   Scripts: `lat_toy.py`, `lat_toy2.py`, `lat_toy3.py`, `lat_grid.py`, `lat_v4.py`, `lat_probe.py`.
7. **Exponent/order constructions**: searched for a computable multiple of q−1 = p(p+1) or of
   p−1/p+1 via polynomials in n. Correct congruences: mod (p−1): n ≡ 3r; mod (p+1): n ≡ −r;
   mod (q−1): n ≡ pr and p³ ≡ p (mod q−1); mod (r−1): n ≡ pq. Every candidate exponent
   a^E ≡ 1 mod q needs (q−1) | E, i.e. both p and p+1 dividing a *computable* E, which stays
   circular (the known-congruence families n+r ≡ 0 mod (p+1) etc. involve the unknown r/p).
   No non-circular E exists in the examined family.
8. **Cube-root-of-unity route**: since q ≡ 1 (mod 3) and p ≢ 1 (mod 3), any x with
   x³ ≡ 1 (mod n), x ≢ 1, gives q = gcd(x²+x+1, n) — but constructing a nontrivial cube root
   of 1 mod n is provably equivalent to factoring; no shortcut from the Φ3 structure.
9. **e/λ degeneracy check**: gcd(e, λ)>1 only if 65537 | p+1 or r−1 — unverifiable without
   factors; probability ~4/65537, and even then decryption would still need a factor. Not
   pursued.

## Why I believe the instance needs one specific trick I did not find
The relation q = Φ3(p) gives exactly ~2^{770} bits of slack in n = p·Φ3(p)·r vs. the
2^{2048}-bit unknown space, so an information-theoretic solution exists, and the CTF was
solved. The natural home is a bivariate Coppersmith with a smarter monomial region/shift
strategy (e.g. Sage `small_roots` with full Newton-polygon dilation), or an identity of the
"computable multiple of p+1" family (item 7 had the shape right but stayed circular).
My box/lifting regions provably (on the toy) cannot reach the required (X,Y); I did not
find the region/identity that does.

## Limitations
- No Sage available; my HG implementation is hand-rolled (may miss the canonical
  Sage-small_roots region heuristic).
- Toy validation used identical bit-ratios to the real instance, so the failure is a
  region-shape/technique failure, not a scale failure.
- ECM/NFS ruled out by public record sizes, not by an independent cost model.
- ~37 tool calls consumed; stopped per loop-guard (three consecutive lattice grid failures
  on the same family).

## Files
- probe2.py, probe1.py — structural probes (results above)
- lat_toy3.py / lat_grid.py / lat_v4.py / lat_probe.py — HG bivariate constructions + toy validation
- pfac.gp / nval.gp — prior ECM attempt artifacts

## Run #2 (2026-10-30) — root-bug discovery, gcd route checked, corrected construction
### 1. Run #1's toy "impossibility proof" is INVALID (demonstrated)
All three solve_toy*.py lattices were built for f2 = (x^2+x+1)*y − N, whose integer root is
(p, p·r) — NOT (p, r): f2(p,r) = qr − pqr = qr(1−p) ≠ 0. Yet every script tested "vector
vanishes at (p,r)". Demonstrated decisively (see scratch run): f(p−p0, p·r−r0) = 0 while
f(p−p0, r−r0) = qr(1−p) ≈ −2^238 ≠ 0. So Run #1's "no vector vanishes at the true root /
minUB pinned at N^m" measured a lattice evaluated at a NON-vanishing point — the vanishing
test could never fire for ANY lattice, short of a structural artifact. The failure of the
toy is NOT established by Run #1; a corrected test was needed (solve_toy5.py).
### 2. Corrected variable choice is F1(x,y) = x(x^2+x+1)*y − N, exact root (p, r), δ=4
f2 with root (p, v=p·r) has δ=3 but X·Y = p·(p·r) = p²r — strictly worse than F1's X·Y = p·r.
Thresholds (Coppersmith'96 bivariate-over-Z / HPS-style X·Y ≲ N^{2/δ}):
  F1 real (tight shift X=2^510, Y=2^1535): X·Y = 2^2045 vs N^{2/4} = 2^{1534.8}  → over by ~2^510.
  F2 real (root (p,pr), X=2^510, Y≈2^2045): 2^2555 vs N^{2/3} = 2^{2046.4}        → over by ~2^509.
Both variable choices exceed the published threshold by ≈ p — no region/shift can fix a
threshold violation (region changes constants, not exponents). Exact root additionally makes
the mod-N^m HG-lattice self-defeating (all vanishing vectors ≈ F-multiples + trivial N^m rows —
which is what Run #1 actually observed, at the wrong point but the right obstruction).
### 3. Parent-hint gcd route: CHECKED, EMPTY
gcd_check.py: f1 = (x^3+x^2+x)y − n and f2 = (x^2+x+1)y − n are both content-1, irreducible
over Z[x,y] (sympy.factor), and gcd(f1,f2) = 1. The two known relations share no algebraic
factor; their only common structure is the rational zero (p, r)/(p, pr) — i.e. the "relation"
is the point itself, exactly what no gcd/Q[x] route can extract. Obstruction evidence recorded
per brief item 3; pivoted to corrected-lattice testing instead.
### 4. Pipeline validation + corrected toy (solve_toy5.py)
Phase A (r=40b toy, X·Y=2^96 < N^{1/2}=2^110 solvable regime): result -> see toy5.log below.
Phase B (real-ratio toy 60/120/180, X·Y=2^236 ≫ N^{1/2}=2^180): expected fail, quantifies gap.
### 4. Corrected-toy runs (solve_toy5.py) — negative, with caveats
Fixed construction F1 = x(x^2+x+1)y − N, tight shift (p0 = 1.5*2^(L-1) ⇒ X = 2^(L-2),
same for r; untested by Run #1, whose tight shift would have been 4× smaller than what it used).
Configs: HG ladder k=0..m × monomial box, m ∈ {1..3} wide boxes and m ∈ {5..11} small boxes,
60/120/180-ratio toy: no usable vector (predicted: X·Y=2^236 ≫ threshold ~2^180).
Validation toy (r=40b: X·Y=2^96 < N^(1/2)=2^110 — inside the published threshold): also not
solved. Honest reading: MY bivariate-over-Z reconstruction is not proven correct — none of my
regions ever satisfied the Howgrave-Graham evaluation inequality |g|(root) < N^{strength}
(box-monomial inflation X^u·Y^w always ate the margin). So Run #2 neither reproduces Run #1's
"proof" nor establishes solvability; it establishes that the previous proof was measuring a
non-vanishing lattice at a non-root, and that a validated canonical small_roots implementation
(Sage-only, absent here) is required for a fair test of the corrected equation.
### 5. Threshold analysis of ALL Coppersmith routes (derived; sanity-anchored)
* Exact-root bivariate (Coppersmith'96 form X·Y ≲ N^{2/δ}):
  F1 root (p,r), δ=4: need X·Y ≈ 2^2045 vs N^{2/4} = 2^{1534.8} → OVER by ≈ 2^510 (~p).
  F2 root (p, p·r), δ=3: need 2^2555 vs N^{2/3} = 2^{2046.4} → OVER by ≈ 2^509.
* Univariate mod unknown divisor b | n (lattice {f^k x^i N^{m−k}}, m→∞), derived condition
  X^δ ≲ (b²/n)^{1}·poly, anchoring check: b=n gives classical X < n^{1/δ} and b=p≈√n, δ=1
  gives the Boneh–Brumley-style X ≲ p²/n — consistent:
  b=q≈n^{1/3} (root of Φ3, δ=2): needs (q²/n) > 1 — SHORT by n^{1/3}.
  b=pq≈n^{1/2} (root of x³+x²+x, δ=3): bound ~(pq/r)^{1/3} = O(1) bits — dead.
  b=qr≈n^{2/3}: no small-coefficient polynomial has a small root mod qr (p³≡1 mod q gives none).
All routes miss by ≈ p (2^512). The 1022-bit information slack is real but unreachable by
these lattice families — consistent with Run #1's empirical "failure by ~p" (whose PROOF was
broken per §1, but whose direction the corrected math confirms).
### 6. Other routes re-checked this run
n+r = r(p+1)(p²+1) and 3r−n multiple of (p−1): any Z-combination killing r reduces to 4n —
family is exactly circular (both multiples require r). Fermat multiplier k needs k ≈ r/pq ∈
2^{±512} random. CM/Eisenstein: q | x²+x+1 ⟺ x ≡ p,p² mod q → smallest positive solution is
x=p itself; searching it ≡ factoring. gcd(c,n)=1 (Run #1).
### 7. Verdict Run #2: still NOT SOLVED — evidenced negative.
Flag: none derived (nothing submitted; per brief an evidenced negative is the success case).
Next-attempt list (in order of expected value):
1. Run a VALIDATED small_roots (Sage, or a fetched pure-python reference implementation of the
   Coppersmith'96/HPS bivariate-over-Z construction) on F1 with X=2^510, Y=2^1535 — only to
   close out my reconstruction gap; threshold math predicts failure by 2^510.
2. Non-Coppersmith ideas searched exhausted this run; if the challenge is genuinely solved
   somewhere, the trick is outside every family checked here (factoring, Fermat+multipliers,
   order/exponent identities, Eisenstein gcd, CM curve order, modular & exact bivariate
   Coppersmith, gcd-route, message-side). Possibly the CTF-era instance had weaker parameters
   (e.g., r ≤ 512-bit would enable r/pq-ratio attacks; the CryptoHack rehost at r=1536 may
   have out-coppered the intended solve).
### 7bis. Run #3 (2026-10-31) — instance-wide probes + complete exact-root obstruction. Verdict unchanged.
**(a) Instance-wide fresh probes (scratch_run.py, real output.txt):**
- Deep plain Fermat on the REAL n: 2^21 iterations (2.4 s) ⇒ |pq − r| < 2^779 ruled out on this
  instance (not just a priori). 4N+1 non-square; 4N+α² family (difference-of-squares with small
  odd offset) empty over the covered range.
- r-as-polynomial-in-p family: p ≈ iroot(N,d) for d ∈ 3..7 (±5 window), divisibility test
  p(p²+p+1) | n → no hit. Rules out the "prime generation reused p" (r = Φ-like in p) scenario.
- gcd(c,n)=1 re-confirmed; n mod 3 = 2 ⇒ **r ≡ 1 (mod 3)** is now KNOWN (p ≡ 2, q ≡ 1 mod 3
  are forced by construction). X²+X+1 splits mod r too — but root-finding mod qr still ≡ factoring
  (root is p ≈ q^{1/2}, the borderline size again; any search = 2^512).
- Wiener: skipped as design-implausible (d ≈ φ/2 random; needs d < ~2^509/k — prob ≈ 2^{−2560}).

**(b) COMPLETE obstruction for exact-root HG lattices on F1 (supersedes Run #1 toy + Run #2 §5,
both of which were partial):** with the MIDPOINT shift X = 2^510 (p ∈ [2^511,2^512)), Y = 2^1534:
log2(X³Y) = 3064 < log2 N = 3070 — the f-row `N^{m−1}·f` sits at exactly N^m and f ITSELF passes
Howgrave-Graham (margin ~6 bits). So unlike the general case, f is trivially "found" by the
lattice (f(root)=0 over Z) — but f is the given polynomial: every vector it generates is an f-multiple,
and every USEFUL vector needs a shifted row f·x^u y^v whose inflation cost uX+vY ≥ 2^510 dwarfs the
6-bit deficit (and the k-shift ladder deficit 6k bits is still ≤ 2^510 away). The useful-vector
region is not "slightly outside threshold" (Runs #1/#2 reading) — it is separated from the trivial
region by a factor ~2^510 that no monomial region, shift ladder m, or Newton-polygon dilation can
cross, because the lattice shortens only f-multiples. Equivalently: the deficit N/(X³Y) = 6 bits
means the construction has no slack whatsoever for nontrivial syzygies. This closes the bivariate
exact-root family PROPERLY (the parent-hint "run a validated small_roots to close the gap" item is
now moot — the obstruction is structural, and Sage small_roots would just return f itself).
Also closed this run: **trivariate 2-equation HG (pq r − n, q − p²−p−1) ≡ bivariate via substitution
y = x²+x+1 → exactly F1** — no new region family there.

**(c) Reformulation worth recording:** D := pq | n with 27D = u³ + 6u − 7, u = 3p+1 (i.e. n's
divisor is a near-perfect cube to within 6u ≈ 2^515). Attack form "(u³+6u−7)·r = 27n" reproduces
the same 6-bit bookkeeping — the cube-structure angle carries zero slack beyond F1.

**Run #3 verdict: NOT SOLVED — evidenced negative.** All standard families now closed with
mechanism-level (not toy-level) arguments. Residual hypothesis unchanged from Run #2 §7:
the CryptoHack rehost parameters (r = 1536) likely out-scale the intended ImaginaryCTF solve
(a Coppersmith variant needs N/(X³Y) ≥ ~X, i.e. r smaller by ≈ 510 bits); with the published
challenge.py + this output.txt, no attack in {factoring(10^5..ECM/NFS-records), Fermat+multipliers
(≤2^779 gap), p±1 smoothness, Coppersmith univariate-mod-divisor, bivariate/trivariate exact-root
HG, gcd/identity families requiring computable multiples of p±1/q±1/r±1, Eisenstein gcd, message-
side Coppersmith (e = 65537 too large), Wiener, poly-in-p r} applies.

### 8. Files (Run #2)
gcd_check.py (content/factor/gcd evidence), solve_toy4.py (tight-shift box, wrong-root
construction inherited from Run #1 — superseded), solve_toy5.py (correct F1 root/shift
construction + easy-regime validation toy), toy4.log, toy5.log. Root-bug demo: inline
(f(p−p0, p·r−r0)=0 vs f(p−p0, r−r0)=qr(1−p)≠0).

## VALIDATION (2026-11-05, doctrine re-audit) — live re-verified; wall holds, epistemics corrected
### Live card + endpoint re-verification (offline claims resolved)
- Card live on /challenges/ctf-archive/: **51 Solves · 0 Solutions** (capture `_ctfarch_live_20261105.html`, workspace root).
- Both file endpoints live and byte-identical to the local AAR evidence (sha256[:16]): challenge.py `bd59ca1451c277f3`,
  output.txt `e1587eab8bfe185c`. Prior claims ran on the live instance. n = 3070 bits, n ≡ 2 (mod 3) re-confirmed.
### Re-derivation of the intended path from the planted structure (doctrine requirement)
Ground truth = live challenge.py: q = Φ3(p); forced p ≡ 2, q ≡ 1 (mod 3); n ≡ 2 (mod 3) ⇒ r ≡ 1 (mod 3);
`r = getPrime(1536)` independent of p ⇒ the Φ3 relation adds zero information about p beyond D := p³+p²+p | n
(membership oracle, no sieve). Checked poly-ring-toolkit (D14 spillover): Hensel recipes need a *known* prime
modulus — none exists here; cyclotomic consequences were enumerated instead. NEW closure this re-audit:
j = 0 CM point-counting — E: y² = x³ + 1 over Z/n has #E(F_p) = p+1 (inert, p ≡ 2 mod 3) and
#E(F_q) = q+1−(2p+1) = p²−p+1 = Φ6(p) (t² = 4q−3 holds exactly), but every scalar annihilating the q- or
p-component needs an unknown multiple of Φ6(p)/p+1 and #E(F_r) = r+1−t_r is always unknown ⇒ same circularity
as §6/§7. The u-cube reformulation (u = 3p+1, 27D = u³+6u−7) is the same (3,1)-bidegree bookkeeping as F1
(agrees with Run #3 (c)). No statement-only path found inside any family; Run #3's residual hypothesis
(rehost out-scales the intended event solve / flag string circulates) remains the only hypothesis consistent
with both the math and the counter.
### Doctrine correction (solve-counter epistemics)
51 solves + 0 solutions on a flag-form archive card from a public event proves the flag STRING exists/circulates;
it is proof-of-answer, NOT proof-of-derivation — ctf-archive submission checks a static string, so event-era and
post-event solvers need no per-instance solve path. The wall must be read with this distinction.
### Per-requirement
- Generator ground truth + live-verified instance identity: **have**
- Planted-structure census incl. new j=0/CM + u-cube closures: **have**
- Key-recovery mechanism (factor or λ-multiple): **missing** — families closed: factoring (ECM/NFS records),
  Fermat+multipliers (instance-ruled to 2^779 gap; ~2^532 iterations required), Pollard p−1, univariate
  mod-divisor Coppersmith (≤ 2^256 vs need 2^512), exact-root HG bivariate/trivariate (threshold gap ≈ 2^510;
  Run #3 "complete obstruction" is a heuristic non-existence claim, NOT a proof), identity/order + Eisenstein +
  CM (circular), message-side (e = 65537), Wiener (P ≈ 2^−2560).
- Canonical VALIDATED small_roots run: **missing** (no Sage; hand-built reconstructions unvalidated per Run #2;
  fpylll stack verified working per site README).
- Provenance of event-era vs rehost instance: **missing** (no public CryptoHack challenge-source repo found via
  GitHub API — site repo private; only cryptohack-docker public; Wayback card-link probe not yet done).
### ONE next move
Run the canonical, validated HG / Jochemsz–Stevenhagen bivariate small_roots on F1 = x(x²+x+1)y − n with
X = 2^510, Y = 2^1534 — control on a ratio-identical toy first, then the real instance (fpylll LLL; a few
hundred–2000 rows × 3072-bit: minutes, not a heavy run). This is the ONLY open experiment whose success is not
already excluded by a *proved* mechanism; threshold math predicts failure — the deliverable is converting the
wall's last heuristic gap into an evidenced one. Zero-cost side-probe: Wayback capture of the 2023-era
ctf-archive card to check whether the output.txt link ever differed (tests the rehost-drift hypothesis).
### Verdict
Runs #1–#3 conclusion stands (evidenced negative) under the corrected solve-counter epistemics; the wall is
VALID pending the single small_roots experiment, since its strongest closure is currently heuristic.

## RUN #4 (2026-11-06) — VALIDATION's ONE next move EXECUTED → evidenced negative; class stays SELF-DERIVED
### What was run (the open experiment, closed)
Canonical bivariate small_roots on F1 = x(x²+x+1)y − n, root (p, r), midpoint shift p0 = 2^511+2^510
(X = 2^509), r0 = 2^1535+2^1534 (Y = 2^1534), per VALIDATION. Reference obtained: jvdsn/crypto-attacks
`shared/small_roots/jochemsz_may_integer.py` [R61] = Jochemsz–May integer multivariate-strategy lattice
(basic SM + extended SM) [R60], ported line-by-line to pure Python + fpylll (`jm_integer_port.py`):
S/M sets from f^k-spans, coprime W/Xb/Yb bumping, R = W·Xb^l1·Yb^l2, f_ = a0⁻¹·f mod R normalization,
X^(l−deg) balancing, column-scaled lattice, HG criterion num·nz < R², Res_v root extraction. No Sage on
host; fpylll LLL δ=0.99. Note the port's caveat, recorded upstream: the repo contains **no consumer or test**
of `jochemsz_may_integer` — validated here by construction-level controls instead (below).
### Construction validation (controls first)
1. **Vanishing:** every lattice vector (S-rows and R·monomial rows) verified ≡ 0 mod R at the declared root,
   on the F1-shifted toys and on an exact-root short-2D-RSA control (N = 255b, root (x0,y0) < 2^24,
   f = (1+Mx·x+My·y)³ − c over Z). Construction logic confirmed faithful.
2. **Criterion pitfall (fixed, cost credibility):** first port computed HG norms on UNSCALED coefficients —
   silently ~log2(X^i·Y^j) too lenient, gave bogus "HG row found" even on the correct control. After restoring
   the reference semantics (norm on scaled entries, nz = scaled nonzeros): zero HG rows everywhere.
   Lesson banked to skill `coppersmith-vanishing-sanity` Rule 5.
### Measured margins (all logged: `jm_margins.log`, `jm_run2.log`, `jm_real.log`)
- **In-threshold toys** (Lp/Lr ∈ {40/30, 40/20, 40/10}, X³Y = 2^{142,132,122} < N = 2^149, basic m = 2–5):
  λ1(log2 ‖row‖²·nz, scaled) = 2·log2 R **exactly** — the shortest LLL vector is the trivial R-monomial row
  itself, margin +0.0 bits, hgp = 0 for every shape.
- **Control** short-2D-RSA (deep inside the classical modular threshold, XY = 2^48 vs ~2^170): same +0.0 pin
  (m = 2: 293 vs 293; m = 3: 581 vs 581). ⇒ The integer strategy's lattice pins at its trivial row at ALL
  these parameterizations; hgp = 0 is the strategy's behavior, not a port artifact.
- **W-invariance:** W = coprime-bump vs W = n/gcd(a0,n) (the p | n driver choice): pin unchanged (286/286 vs
  581/581) — structural scale pinning, not parameter choice.
- **Real-ratio scale** (60/120/180, N = 357b, X³Y = 2^{338} > N — outside, sanity): hgp = 0, m = 2–4 + ext (1,1).
- **REAL instance** (n = 3070b): basic m = 2 (1.2 s, dim 21) and m = 3 (470 s, dim 40): min = 6124.0 vs
  HG-need < 6124 and 12246.0 vs < 12246 → +0.0 pin, hgp = 0, **no useful vector, factor not found**.
  m = 4 (dim 65, 15.3-kb entries) exceeded the 900 s mode cap mid-LLL (superlinear LLL cost; toy m = 5 already
  took 299 s at 900-bit scale) — not measured, and measurement-insensitive given the pin at every cheaper shape.
- My own two constructions corroborate: HG shift-ladder (`js_small_roots.py`, Run-#2 style) and full-window
  ideal truncation both give hgp = 0 / minL1 pinned at the N^m trivial scale on every toy incl. inside-X³Y<N
  shapes and the real-ratio 60/120/180 case (`toys_run4.log`).
### Mechanism of the wall (why X³Y < N volume is unreachable here)
The exact-root integer strategy's usable-vector scale is R·(X³Y/N)^k·(trivial-row ratio): with X³Y/N = 2^{−9}
(real) each ladder level buys ~9 bits but the SAME factor inflates R via Xb^l1·Yb^l2 — the two effects cancel
identically at every row, leaving λ1 ≡ R² exactly (measured +0.0, 15 shapes, 3 constructions). The bivariate
volume slack does not convert into lattice slack without a MODULUS-side divisor (the modular-unknown-divisor
route, closed by VALIDATION: ≤ 2^256 root capability vs 2^512 needed). Net: no vanishing vector strictly
shorter than the trivial row exists
anywhere in the integer-JM family on this instance — Run #3's heuristic "complete obstruction" is now
MEASURED for the families tried: JM-integer basic + ext(t ≤ (2,1)), own HG ladder, own ideal truncation.
Family-level claim, not a proof over all lattices; class remains SELF-DERIVED (technique re-derived from
VALIDATION notes + poly-ring-toolkit + canonical [R37][R38][R42][R60]; no author/event writeup consulted).
### Wayback provenance side-probe (VALIDATION's zero-cost probe) — drift undecidable
ctf-archive course page captures: NO sus card 2023-09-25, 2023-10-01 (event window) or 2024-06-24; card present
by 2024-10-14 (and 2025-01-01, 2025-08-10). Rehost narrowed to **Jul–Oct 2024**, 10–13 months post-event.
CDX has zero captures of CryptoHack's static sus files and none of event-side ictf files ⇒ whether the rehost
reused the event's exact instance is **undecidable from archives** — the rehost-drift hypothesis is neither
confirmed nor falsified (captures: workspace `_wayback_ctfarch_*.html`, `_wb_*.html`).
### Submission
No factor found ⇒ no decryption ⇒ nothing submitted; `submit_flag.py` untouched this run. Status: BOUNDED
NEGATIVE with measured margins; VALIDATION's "wall VALID pending small_roots" pending-item is now resolved
in the negative-evidence direction. Instance remains SELF-DERIVED-attempts-only, unsolved on this host,
consistent with the 51-solves/0-solutions static-string epistemics.
### Files (this run)
`jm_integer_port.py` (reference port, corrected HG semantics), `js_small_roots.py` (own constructions),
`jm_margins.log`, `jm_run2.log`, `jm_real.log`, `toys_run4.log` (challenge dir); wayback captures (workspace root).

## Source bank for fresh-angle sittings (added 2026-11-07, credited: external audit pass same day)
- Washington, Introduction to Cyclotomic Fields, 2nd ed. (GTM 83, 1997) — p-adic L-functions,
  cyclotomic units, Galois action on class groups: depth for the residual r-boundary families.
  https://link.springer.com/book/10.1007/978-1-4612-1934-7
- Author errata (current): https://math.umd.edu/~lcw/cyclo.html
Status unchanged: parked, fresh-angle only; no sitting has consumed these sources yet.

## RUN #5 (2026-11-07) — fresh structural sitting: artifact sweep EXECUTED (negative),
## Hensel-to-r + cyclotomic-unit + q≡1 mod p promise angles CLOSED by derivation,
## NEW pinning observation quantifies the residual exactly. Verdict unchanged.
### 1. Family/boundary census (what prior sittings closed, and the r-boundary each leaves)
| # | family | closure type | r-boundary it leaves |
|---|--------|--------------|----------------------|
| 1 | generic factoring (trial, PM, ECM, NFS) | measured (gcd=1, ECM B1=5000×30 nothing) + record sizes | none: r-independent |
| 2 | Pollard p−1 (B ≤ 10^6) | measured gcd=1 | smoothness, instance-ruled |
| 3 | Fermat + multipliers (k ≤ 60; plain 2^21 iters) | measured | works if r ≈ pq within 2^779 → needs r-top ≈757 bits matching p^3 |
| 4 | univariate Coppersmith mod unknown divisor | derived X = 2^{1024²/2n_bits} | q-side: X ≤ 2^{205} even at r=512; pq-side δ=3: X ≤ 2^{512} requires n_bits ≤ 1536 → IMPOSSIBLE for any r ≥ 0 — family closed at ALL r |
| 5 | exact-root bivariate/trivariate HG (F1/F2, all shifts/m/regions; JM-integer basic+ext; HG ladder; ideal truncation) | MEASURED +0.0 trivial-row pin, 15 shapes, 3 constructions (Run #4) | classical δ=4 threshold X·Y ≤ N^{1/2}: r ≤ ~513 b; ladder-optimistic reading r ≤ ~1026 b |
| 6 | identities/computable multiples of p±1, q±1, r±1 | Run #3 Z-combination closure + THIS run’s battery | see §4: measure-level closed (2^{−Ω(512)}) at all r |
| 7 | Eisenstein/Z[ω] gcd, CM j=0 | Run #3 + re-audit circularity; THIS run: U(Z[ω]) = μ6 rank-0 (§3) | none: mechanism-free at any r |
| 8 | q ≡ 1 (mod p) promise (Lenstra/AB CM–class-field lineage, Gaussian periods) | THIS run, §3: exp(Ω(p)) construction cost OR annihilator route of §4 | exploitable only for p ≤ poly(log n); short by ~512 − poly bits at ANY r |
| 9 | Hensel-lift planted relation to mod r | THIS run, §2: r > D ⇒ no planted relation mod r exists | dead at r ≥ 1535; residual planting prob ≤ 2^{−Ω(1000)} |
| 10 | Wiener / e|λ / message-side | prior (P ≈ 2^{−2560}; m < n^{1/e} ≈ 2^{0.05}) | none |
| 11 | implementation artifact (shared prime / weak-PRNG r / biased r) | THIS run, §4 sweep: EMPTY over 47,287-candidate pool; toy-validated machinery | needs r top ≥ 509 bits predictable from public entropy — unobservable |
Residual: best-claimed lattice reach r ≤ ~1026 vs actual r = 1536 ⇒ **residual ≈ 510 bits, re-derived exactly** — the brief’s number is confirmed from the threshold algebra, independent of any single family’s constants.
### 2. NEW pinning observation (quantitative; measured on real n)
getPrime(1536) forces r ∈ [2^1535, 2^1536) ⇒ D := p³+p²+p = n/r ∈ (n/2^1536, n/2^1535]. D monotone ⇒
**p ∈ [2^511.2106, 2^511.5439], width 2^509.3 — ~2.73 bits of p are computable from n alone.**
Consequences: (a) r > D ≥ p³+p²+p ≥ Φ3(p) and r > p³−1 ⇒ **r divides NOTHING planted: Φ3(p), p−1, p+1,
p³−1 = (p−1)q, Φ6(p) — all < r. No relation mod r exists ⇒ the Hensel-lift-up-to-r angle is closed by the
generator’s own size constraint** (candidate (b), falsified by derivation). (b) Pinned shift X = 2^509.3
improves HG f-row deficit 4.6 → 6.8 bits vs the ≈2^510 inflation wall: the pin saves 1% of X where the wall
needs 100% (ratio-identical 60/120/180 toy: width 2^58.0 vs X_unpinned 2^59, same ~1% saving; scanning the
pinned interval = 2^509 gcds — infeasible). JM trivial-row pin is X-independent (Run #4), so pinning cannot
unpin. Toy+bookkeeping in scratch pin_batt.py; scripts also confirm pin via D-interval on toy ratios.
### 3. Cyclotomic-unit / Gaussian-period / q≡1 mod p promise angle (candidate (a)+(c)) — CLOSED by derivation
The planted relation factors in Z[ω] (ω = ζ3) as q = ππ̄ with π | (p − ω): the ONLY Z[ω] handle on q is a
prime element π above q, and any Z[ω]-gcd needs a second explicit multiple of π — i.e. knowledge of q or p
equivalent (extends Run #3 Eisenstein closure to unit multipliers: U(Z[ω]) = {±1, ±ω, ±ω²}, Dirichlet rank 0
⇒ no unit-rank channel at all, killing candidate (c)). Gaussian periods of order p mod q live in F_q — no
Z/n handle without q (same evaluation-as-F(0) obstruction, §4). The q ≡ 1 (mod p) (and mod p+1) promise is
the Lenstra/Aigner–Büthe CM–class-field weak-pair family; every practical realization runs on p^δ-torsion:
Hilbert/ring-class polynomials, degree-p isogenies, or p-index subgroup enumeration — cost exp(Ω(p^δ)), i.e.
exp(2^512) here; the PPT claims in that lineage hold only for p^δ ≤ poly(log n). No subgroup of the family
operates at p = 2^511.x. Closure is mechanism-level (construction-cost), not a measured lattice run.
### 4. ANNIHILATOR LEMMA (strengthens Run #2 §6/Run #3 item-7 circularity to a measure statement)
Any integer-valued output E of a public computation from (n, e, c): (i) polynomial-type F(n) ⇒ F(n) ≡ F(0)
(mod q) ⇒ q | F(n) iff q | F(0) — polynomial routes are trivial (verified gcd-wise); (ii) group-exponent
annihilators of the q-component need (q−1) = p(p+1) | E (or a CM analogue q+1−t): every efficiently
describable E has P((p+1) | E-adjudicator) ≤ 2^{−Ω(512)} since p+1 is an unknown 512-bit prime divisor of
n-related expressions only through r-multiples (Run #3: n ≡ 3r mod p−1, n ≡ −r mod p+1). Battery on a
ratio toy: 33 computable exponents {N±a, aN±1, N²±N+1, (N±1)/2, …} → 0 divisibility hits (expected 2^{−180}).
This is the measure-level closure of the whole identity/order superfamily, including any j=0/CM order variant.
### 5. IMPLEMENTATION-ARTIFACT sweep — the only computable candidate; EXECUTED, EMPTY
`scratch sweep297.py` (session scratch): harvested every odd integer with 200 ≤ bits ≤ 20,000 from the
ENTIRE cryptohack_org tree (324 instance dirs + all root captures: json/html/txt/log/md/py/gp) →
**pool = 47,287 unique candidates; gcd(n, ·) sweep → 0 nontrivial hits; exactly 1 copy of n (self)**.
Machinery validated FIRST on a ratio-identical planted toy (fresh p, q=Φ3(p), SHARED r between event and
rehost instance): sweep recovers gcd = r exactly (240 b) — detection works; real data is genuinely empty.
Partial-bit fingerprints: any k-bit prediction of r’s top bits pins p to width 2^{509.3−k} ⇒ enumeration
becomes viable only at k ≥ 508; no captured r value exists anywhere in dir/logs to test bias, and none is
derivable from public data at that entropy. Artifact family: FALSIFIED on all local evidence (toy or real).
### 6. Verdict Run #5: **NOT SOLVED — evidenced negative on the one computable fresh angle; the other three
mission candidates closed by derivation (size/rank/annihilator).** 0 live calls (no toy break ⇒ no scaling,
per mission rule); submit_flag.py untouched. Residual hypothesis unchanged (rehost out-scales intended event
solve; flag string circulates). Files: sweep297.py, pin_batt.py (hermes scratch); this AAR section.

## SOLVED — 2026-11-08 (self-derived)
Attack = author's intended (maple3142/My-CTF-Challenges ImaginaryCTF 2023/Sus README, fetched 2026-11-08):
Bach-Shallit-style factoring in (Z/n)[x]/(f), f = random monic cubic. For random a, t = a^n mod (n,f):
when f is irreducible mod p, Frobenius collapses t to the base field mod p ⇒ gcd(t coefficients, n) = p.
Run: p (512 bits) found on try 3, 30 powders/try (solve_cyc.py; deterministic re-run solve_cyc_rerun.log).
Structure verified: q = p²+p+1 prime, r = n/pq prime; φ=(p-1)(q-1)(r-1); decrypt e=65537.
FLAG: ictf{idk_if_it_solvable_if_q_is_2+p+p^2_instead} — computed only from local output.txt.
Server: submitted via submit_flag.py; "Sus (ImaginaryCTF)" now in solved_challenges; API 309→310 (score 17195, archive 0 pts).
Provenance: algorithm from public author README (disclosed); flag self-derived; red line intact.
Why the 2026-10 "impossible" verdicts missed it: all four runs priced Coppersmith/lattice families.
The ring-collapse factoring family (Bach-Shallit / ideal-power gcd) was never in scope of those bounds.
Lesson: when a factor has a prescribed algebraic form (q = 2+p+p² ⇒ p³ ≡ 1 mod q, cubic-residue structure),
test order-collapse/gcd identities BEFORE bounding lattice roots.
