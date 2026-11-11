---
name: bivariate-coppersmith-hint-factoring
description: Use when factoring RSA from p+q or sqrt-sum hints.
---

# Bivariate Coppersmith from approximate p+q / sqrt-sum hints

Use when a challenge leaks S = p+q or hint = D(√p+√q) approximately and n=pq must be factored.

## Rule 0 (learned the hard way on 1337crypt, DUCTF 2020 — bivariate detour produced a FALSE
'artifact corrupt' verdict there): a sqrt-sum hint hint = D(√p+√q) makes the UNIVARIATE
quadratic z² − hint·z + D²·isqrt(n) have roots ≈ D√p, D√q. Take the small root r and use
p_approx = floor(r²/D²) (tighter than (floor(r/D))²: keeps the cross term), then plain
UNIVARIATE Coppersmith on f(x) = x + p_approx mod n (1337crypt: |δ|=2^586 with X=2^590,
beta=0.4/0.5, m=6 t=9). Solve it that way — the bivariate f(u,v)=uv+q0u+p0v+c0 lattice never
uses the sqrt-sum structure. Only fall back to the bivariate machinery for p+q-style linear hints.

## Core setup
- hint = floor(D(√p+√q)): S = (hint±E)²/D² − 2√n (E = hint error, 0 if exact floor).
- t0 = interval center; d0 = isqrt(t0²−4n) (ALWAYS positive: S²−4n = (p−q)² > 0); p0=(t0+d0)/2, q0=n//p0, c0=p0q0−n.
- Root bounds: |u0| ≤ (ΔS)(1+S/d)/2 (amplification (1+σ)/2, σ=(p+q)/|p−q| can be ~4 when q≈0.55p — compute from data, never assume 2).
- Lattice: rows n^{m−j}·f^j·u^i v^k, X^aY^b column scaling, HG threshold n^m/(√w+1); reconstruct h = Σ r_ab·u^a v^b / X^{a+b} (division is correct WITH this scaling; test on synthetic twin first).
- Eliminate via f linear in v: R(u) = numer(h(u, −(q0u+c0)/(u+p0))·(u+p0)^{deg_v+2}).

## Pitfalls (each cost hours)
1. VERIFY on a synthetic full-scale twin FIRST (same bit sizes, same σ regime, same code path) — include a noisy-hint variant (E=2^16) before trusting real-data negatives. Vanishing holds even for noisy hints; pairwise gcd(R0,Ri) stays rooted.
2. Extraction: use PER-PRIME root-set INTERSECTION across all resultants, then CRT — NOT a k-way gcd over Z (extraneous content makes 6-way gcd deg 0 even when the root is present; pairwise gcds are the rooted ones).
3. Dump polys to Pari with readvec (read() executes + returns last expr — silent garbage; pollred/sqfree don't exist).
4. Inconsistency oracle (cheap, decisive): if passing rows vanish at any integer root, ALL resultants share u0 mod p for EVERY prime. `polrootsmod` per resultant, intersect per prime; ZERO common primes ⇒ output data inconsistent with the claimed generator — stop scanning, write evidenced negative.
5. HG mixed-row window for (m=8,K=6, 1337-bit) is empirically X∈(2^594, 2^616]; beyond it only f-multiples pass (Rs=0) — scans above the window are meaningless.
6. isqrt silently abs()s negatives in some paths — assert disc>0 explicitly; S²<4n means the centering interval is wrong (true S always has S²−4n=(p−q)²≥0).
7. Before heavy compute: cheap model discriminators — v2(hint) (float-quantized hint ⇒ huge v2), hint/D vs 2n^{1/4} log-scan for wrong D exponent, gcd(c_i,n), iroot(n,k), tiny-scale replica.

## Canonical references (owner list 2026-11-02)

[R39] Howgrave-Graham, 'Finding Small Roots of Bivariate Integer Polynomial Equations: The Vanishing Case', EUROCRYPT 1999, LNCS 1593. https://link.springer.com/book/10.1007/3-540-48910-X | [R40] Coron, 'Finding Small Roots of Bivariate Integer Polynomial Equations: A Direct Approach', CRYPTO 2007, LNCS 4622. https://iacr.org/archive/crypto2007/46220372/46220372.pdf | [R41] Blomer-May, 'A Tool Kit for Finding Small Roots of Bivariate Polynomials over the Integers', EUROCRYPT 2005, LNCS 3494. https://dlnext.acm.org/doi/10.1007/11426639_15
