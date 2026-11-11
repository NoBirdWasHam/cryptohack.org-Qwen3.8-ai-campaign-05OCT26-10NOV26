---
name: poly-ring-toolkit
description: Use for CTF polynomial roots, CRT, resultants and gcds.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, algebra, ctf]
    related_skills: [windows-crypto-toolchain, ctf-crypto-attacks, coppersmith-vanishing-sanity]
---

# Polynomial / ring arithmetic toolkit (CTF recipes)

## When to Use
Challenge reduces to polynomial algebra: shared primes as poly gcd, root-finding mod p, CRT recombination
(Hastad-style), resultants killing a variable, or lifting factorizations mod p^k.

## Recipes (Sage if available, else PARI gp64 — host paths in windows-crypto-toolchain)
- **Shared-secret-as-gcd**: two moduli/ciphertexts sharing structure -> gcd over Z first, then try
  Z[x]/F_p[x] gcd when only polynomial form exposes the shared factor (PARI: polgcdext / gcd).
- **Roots mod p**: PARI polrootsmod(f,p) (or factormod — roots = linear factors); Sage GF(p)['x'].roots().
  Non-monic? invert leading coeff mod p first. p=2 special case common in GF(2) challenges: use
  polcompositum-free direct scan for tiny deg.
- **CRT for polynomials** (Hastad multi-message): Z[x] via polcrt / Sage crt(list_polys, list_mods) —
  then d-th root COEFFICIENT-WISE when moduli are pairwise coprime integers (integer CRT on coeffs).
- **Resultants to eliminate**: Res_x(f,g) kills x; watch coefficient blowup (deg bound); Sage/PARI resultant.
  Fallback when huge: subcompute mod many small primes + integer CRT of the resultant values.
- **Hensel lifting factorizations/roots mod p^k**: simple root (f'(r) !≡ 0) lifts uniquely —
  Newton doubling for large k (see padic-lift-ecc-attack for the ECC instance; wiki [R35] for statement).
- **Irreducibility / cyclotomic**: polissquarefree before assuming distinct roots; Phi_n via polcyclo;
  power-of-two 2^m-th roots of unity need q ≡ 1 mod 2^m (NTT setup) — [R36].

## Verify
Every reconstruction gets a same-shape control (known roots / known CRT sum) BEFORE touching live data —
same control-probe discipline as msolve (windows-crypto-toolchain).

## Canonical references
[R09] SageMath manual https://doc.sagemath.org/ · [R10] PARI/GP manual https://pari.math.u-bordeaux.fr/
[R35] Hensel's lemma (wiki) · [R36] Cyclotomic polynomial (wiki).
