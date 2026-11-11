---
name: coppersmith-vanishing-sanity
description: Use for bivariate Coppersmith; assert root vanishing first.
version: 1.0.0
author: hermes-run-13393
metadata:
  hermes:
    tags: [cryptography, coppersmith, lattices, ctf]
    related_skills: [ctf-crypto-attacks]
---

# Coppersmith lattice vanishing sanity check

## When to use
Building or debugging any multi-variate Coppersmith/small_roots lattice (bivariate shifts,
mod-unknown-divisor, exact integer roots), or writing a negative-result AAR for one.

## Rule 1 (costs 30 seconds, saves a whole run)
Before measuring "no short vector vanishes at the root", assert the SHIFTED polynomial
vanishes at the declared root:
```python
assert fs.subs({X: x0-x0s, Y: y0-y0s}) == 0   # exact root
# or % modulus == 0 for modular variants
```
If this fails, every downstream "failure" (minUB pinned, zero vectors absent) is an
artifact: a lattice row that doesn't vanish at the eval point can NEVER yield a vanishing
short vector, for ANY region or shift count. A real incident: challenge-13393 run #1
"proved" impossibility for a lattice built from f=(x^2+x+1)*y - N but evaluated at (p, r);
f vanishes only at (p, p*r) since qr - N = qr(1-p) != 0. The proof measured nothing.

## Rule 2: pick the equation that minimizes X*Y and delta together
For N = p*h(p)*r type relations, candidate exact-root forms:
- F1(x,y) = x*h(x)*y - N, root (p, r)          — delta = deg x*h + 1
- F2(x,y) = h(x)*y - N, root (p, p*r)          — root Y balloons: X*Y = p^2*r
Threshold for bivariate-over-Z is ~ X*Y <= N^{2/delta}: compute the gap BEFORE coding;
if it exceeds ~2^30, no region/shift choice can save it (region changes constants only).

## Rule 3: modular-unknown-divisor sanity
Univariate mod unknown divisor b | n via {f^k x^i n^{m-k}} needs b^2/n growth:
max root ~ (b^2/n)^{1/delta}-ish (anchors: b=n gives classical n^{1/δ}; b≈√n, δ=1 gives
Boneh–Brumley scale). Modulus b < √n ⇒ the route is structurally dead regardless of lattice
size; don't sweep regions, write the negative AAR instead.

## Rule 4: exact roots defeat mod-N^m HG ladders
If the root is EXACT over Z, rows F^k*x^i*y^j*N^{m-k} all vanish trivially via F; shortest
vectors are F-multiples + trivial N^m monomial rows ("minUB pinned at N^m" symptom). Use the
bivariate-OVER-Z construction (ideal (F,N) + region, Bézout isolation), not the HG shift ladder.

## Rule 5 (run-297 incident, 2026-11-06): HG norm = SCALED entries, weight by nnz
When porting Jochemsz-May small-roots code (jvdsn/crypto-attacks shared/small_roots/), the
reference criterion is num*nz >= R^2 ELIMINATES a row, where num = squared norm of the
SCALED (column-weighted) entries and nz = nonzero count of scaled vector. Dividing by the
column scale BEFORE the norm check silently loosens the criterion by ~log2(X^i Y^j) per row
and produces false 'HG row found' on ladders that would never pass (measured on challenge-297
F1 toys AND on a correct short-2D-RSA control: both gave bogus passes unscaled, zero passes
scaled). Corollary finding: for exact-root integer-strategy lattices (JM-integer basic/SM),
LLL lambda-1 pins at EXACTLY the trivial R-monomial row scale, margin +0.0 bits, even for
parameter sets deep inside the modular threshold - so hgp=0 there is expected behavior, not
a port bug; W-invariance (W=2 vs W=N) confirms it is structural scale pinning.

## Canonical references (owner list 2026-11-02)

[R37] Coppersmith, 'Finding a Small Root of a Univariate Modular Equation', EUROCRYPT 1996, LNCS 1070. https://doi.org/10.1007/3-540-68339-9_14 | [R38] Coppersmith, 'Small Solutions to Polynomial Equations, and Low Exponent RSA Vulnerabilities', J. Crypto 10(2), 1997 (the X>=N^(1/denominator)-bound formulation). https://link.springer.com/article/10.1007/s001459900030 | [R42] Boneh-Durfee, 'Cryptanalysis of RSA with private key d less than N^0.292', IEEE TIT 46(4), 2000. https://dl.acm.org/doi/10.1109/18.850673 | [R16] Cheon-Stehle CRYPTO 2010 also treats RSA partial-key-exposure via Coppersmith (see lattice-scheme-attacks-ntru-css). | [R60] Jochemsz-May, 'A Strategy for Finding Roots of Multivariate Polynomials with New Applications in Attacking RSA Variants', EUROCRYPT 2006 (bivariate SM strategy; the integer variant of the ported code, cf. Jochemsz-May PKC 2007 multivariate integer roots). https://doi.org/10.1007/11761679_18 | [R61] jvdsn/crypto-attacks, shared/small_roots/{jochemsz_may_integer,jochemsz_may_modular}.py (Sage reference; note: repo has NO in-repo consumer/test of jochemsz_may_integer, and no test exercises integer_multivariate - validate ports with a self-built vanishing control). https://github.com/jvdsn/crypto-attacks
