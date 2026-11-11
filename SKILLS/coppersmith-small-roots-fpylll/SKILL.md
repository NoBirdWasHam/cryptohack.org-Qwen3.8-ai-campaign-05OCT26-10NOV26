---
name: coppersmith-small-roots-fpylll
description: Use when Coppersmith small roots are needed without sage.
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [cryptography, coppersmith, lattice, fpylll, ctf]
    related_skills: [bivariate-coppersmith-hint-factoring]
---

# Sage small_roots ported to fpylll (univariate Coppersmith, no sage on host)

> **PROVENANCE:** the *attack-path choice* for the proving challenge (univariate HG on a
> hint-derived p-approx; not the bivariate route we had priced) came from the organizer's
> published exploit + author writeup (challenge-13396 AAR cites both). The port itself,
> all pitfalls, and the modular-root extraction were engineered/validated here. Class:
> PATH WALKED — treat the path-selection as reminder that the family exists; re-derive
> route choice yourself on fresh challenges.

## When to use
A CTF/archived challenge needs univariate Coppersmith (partial key / known-high-bits factoring /
RSA variants) but the host has no sage — only python + fpylll (e.g. crypto-ctf venv). Also for
Goldwasser-Micali style bit decryption once p is known.

## Port of sage polynomial_modn_dense_ntl.small_roots (May-thesis lattice)
- Params: d=deg f (monic, over ZZ); m=ceil(max(beta²/(d·eps), 7·beta/d)); t=floor(d·m·(1/beta−1)); rows N^(m−i)·f^i (i=0..m−1, j=0..d−1) then x^i·f^m (i=0..t−1); entry (row, col j) = coeff_j·X^j. dim = m+t for d=1.
- HG sanity: log2 det = Σ[(m−i)·log2N + i·log2X] + Σ(m+i)·log2X; require det^(1/w) < (N^beta)^m with ≥100 bits slack, else lower eps to raise m.
- fpylll API on Windows venv: `IntegerMatrix(r, c, int_type='mpz')` (NOT 'gmp'); reduce with `LLL.reduction(M, delta=0.99)` (bare `LLL(...)` raises TypeError). Descale exactly: b[j]//X^j (assert divisible). 15x15 with 2^16000 entries reduces in <1s.
- Roots can be SIGNED; recover factor via g = gcd(N, pA + r) per signed candidate r, verify g|N and both factors prime.

## Pitfalls
1. sympy LIES on LLL polys with ≥~4000-bit coefficients: Poly.eval can return nonzero at an exact root; ZZ-domain gcd can return a common factor NOT containing the true shared linear factor (both contradictions verified). factor_list/real_roots on such polys also hang. NEVER factor/gcd/eval reduced lattice polys with sympy.
2. Root extraction that works: modular common-root + CRT. For ~20-bit primes ℓ: numpy Horner-evaluate the 5 shortest descaled polys at all residues mod ℓ (int64-safe when ℓ<2^31), intersect root sets, prune |r|≤X during CRT, verify survivors over ZZ with raw-Python Horner. ~30 primes cover 590 bits; surviving candidate usually unique.
3. Norm-quality checks must compare ||v||, not ||v||² (bit_length of squared norm is double the exponent — cost a phantom 'LLL failed' diagnosis).
4. Validate the whole port on a SYNTHETIC twin (own primes, same bit geometry, same X, same code path) before real data; LLL stays sub-second even at 2674 bits, so there is no excuse to skip the full-scale twin.
5. GM-style bits without sage kronecker: bit=1 iff pow(c,(p-1)//2,p)==1 (Euler criterion) for c = x^(odd+b)·r^(even) constructions.

## Reference
sagemath `src/sage/rings/polynomial/polynomial_modn_dense_ntl.pyx` small_roots; May, New RSA Vulnerabilities Using Lattice Reduction Methods, PhD 2003. Proven on cryptohack 1337crypt (2674-bit n, X=2^590, δ=2^586 recovered, flag accepted 2026-11-05; AAR: challenge-13396 folder).
