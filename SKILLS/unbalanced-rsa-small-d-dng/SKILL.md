---
name: unbalanced-rsa-small-d-dng
description: Use when RSA primes unbalanced and d small.
version: 1.0.0
author: Hermes campaign solver
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, lattices, rsa]
    related_skills: [ctf-lattices, ctf-crypto-attacks]
---

# Unbalanced RSA + small d = Durfee–Nguyen (Asiacrypt 2000), NOT Wiener/BD

## When to Use
N=pq with p ≈ N^0.25 (e.g. p 256b, q 768b, e full-size) and d ≈ N^{0.29..0.36}.
Wiener/CF and classical BD (p+q ~ N^{0.75}) provably fail — do NOT loop on them; that
family's practical cap is ~N^0.2925 (measured, challenge-13401 run#1).

## Core facts (cited math)
- Challenge params p=256b,q=768b,e full ARE Sun–Yang–Laih (Asiacrypt'99) variant I; Durfee–
  Nguyen Table 2 breaks it to δ_max=0.364 at logN(p)=.25, logN(e)=1.0. Theorem applies
  WITHOUT any secret-bit exposure — the design is broken in principle.
- System: f(x,y,z)=1+x((N+1)−y−z) ≡ 0 mod e root (k,p,q), k<d; PLUS integer relation yz=N.
  Keep BOTH — the trivariate-with-relation family is strictly stronger than the bivariate
  (k,p)-mod-e cubic G(k,p)=k(p−1)(N−p)+p (caps 0.2925).
- Paper lattice: primary h_{m,j}=y^{a+j}f^m (j≤t); helpers g_{k,i,b}=e^{m−k}x^i y^a z^b f^k
  (k<m, 1≤i≤m−k, b∈{0,1}), h_{k,j}=e^{m−k}y^{a+j}f^k (k<m, j≤t). dim=(m+1)(m+t+1).
  Apply yz→N reduction to polynomials BEFORE vectorizing; dim matches (m=3,t=1)→20 ✓.
- Extraction: z=N/y on short rows then EXACT root-finding (see Pitfalls/Extraction bullets
  below; the "gcd(N, const term)" shortcut fails due to p<->q symmetry). Built: resultant_lib.py,
  dng4.py at challenge-13401 dir (solved pipeline).

## Pitfalls (measured cost)
- After LLL, convert vanishing polys with z=N/y (Laurent in y), then shift by y^D into Z[x,y]; vanishing at (k,p) preserved exactly.
- p<->q SYMMETRY: every vanishing poly also vanishes at (k,q). So gcd(N, any resultant coefficient) = N always — all gcd-on-coefficients extraction routes are structurally dead.
- WORKING: exact Res_x(Q_i,Q_j)(y) over Z -> strip overall y^s factor -> flint fmpz_poly.roots() returns EXACT integer roots -> p and q both appear -> factor via N % root == 0. This is what DNG's "standard root finding" really means.
- Compute Res_x with dict-polynomial Bareiss; content_reduce polys first; skip exact matrix det_of for r>80 (20+ min stalls, informational only).
- fmpz_poly.real_roots() NOT implemented in python-flint; .roots() IS (exact; integer roots come back as ints).
- A pdiv helper must return the QUOTIENT for exact division (a remainder helper silently returns {} and breaks gcd-layer logic).
- LLL (delta 0.99) often succeeds even when raw volume margin/vec is negative (-52 bits/vec worked at d=300); guard per-vector, skip configs only below ~-100/vec, try small (m,t) first.
- SOLVED 2026-11-14 (cryptohack unbalanced-icc_athens2022, flag recovered): the earlier
  "no vanishing vectors ever" conclusion applied to small (t,a) regions only. Use the DN00
  Appendix-A EXACT determinant exponents Ce=Cx=m(m+1)(4m+3t+5)/6, Cy,Cz polynomials (a>=0 branch),
  grid (m,t,a) on margin = ebits*m*r - (ebits*Ce+Xbits*Cx+Ybits*Cy+Zbits*Cz) over r=(m+1)(m+t+1)
  and pick margin/r > 15 bits: for p256/q768/d300/e1022: m=8,t=5,a=1 gives +46 bits/dim at rank 126
  and LLL'd rows vanished EXACTLY at (2k,p,q) (toy: 102/124 nontrivial rows vanish). a must be
  ~alpha0*m (>=1 for m>=8); t ~ tau0*m. LLL 126x126 @ 9.5k-bit entries: 4551 s (fpylll, delta=0.99).
- C=2 form f=2+x(A-y-z) pairs with root x0=2k (f(root)=2ed≡0 mod e); strict HG gate (norm*e^m
  threshold, omega-scaled) fails even when rows DO vanish — never gate on it; verify by extraction.
- Extraction (validated, exact): z=N/y with y^{Dz} clearing -> Sylvester matrix in x -> fraction-free
  Bareiss over Z[y] (flint fmpz_poly, exact division via //, assert quo*prev==num) -> Res(y) deg 224,
  ~120k-bit coeffs -> fmpz_poly.roots() exact integer roots -> p = root | N. msolve -P 0 over QQ also
  solves {h1,h2,yz-N} but returns isolating INTERVALS (not exact) and [-1] spurious for >2 polys;
  Bareiss route is preferred. Working code: scratch/unbal/{variants,realsolve,resultant_extract,finalize}.py.
- Old Durfee-thesis Figure-1 hunt NOT needed: the survey's helper set + Appendix-A C formulas are
  complete and sufficient once (m,t,a) are chosen from the margin grid.
- Extraction: see "Extraction (validated)" section below — the old "p = gcd(N, const term of H(y))"
  claim is WRONG for this family (p↔q symmetry makes gcd = N). resultant_lib.py, dng2.py at
  challenge-13401 dir.
- fpylll 0.6.4: LLL.reduction(M, delta=0.99) (LLL.red gone); IntegerMatrix can't multiply
  non-square — use python-flint fmpz_mat(n,m,FLAT list) for Gram/det.
- HG check per-vector: scaled max-norm < e^m/√(mons); volume via Gram det (flint, exact).
- ring-eval/quotient collapse: inapplicable here (no homomorphic quotients of Z[u,w]/(G,e)) —
  the yz=N integer relation IS the dimension-collapsing structure for this system.

## Verify on own ground truth first
Synth p=256b q=768b d=300b prime, run full pipeline, assert p recovered exactly before
real instance (dng2.synth()).

## Canonical references (owner list 2026-11-02)

[R42] Boneh-Durfee, 'Cryptanalysis of RSA with private key d less than N^0.292', IEEE TIT 46(4), 2000 (the bound the DNG unbalanced variant is measured against). https://dl.acm.org/doi/10.1109/18.850673 | [R38] Coppersmith J.Crypto 1997 (method base).
