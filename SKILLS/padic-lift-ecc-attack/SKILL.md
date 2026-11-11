---
name: padic-lift-ecc-attack
description: Use when ECC oracle returns x mod p^2. p-adic lift attack.
---

# p-adic lift attack on ECC oracles over Z/p^k

Canonical references (cite in any AAR using this machinery): Silverman, The Arithmetic of Elliptic Curves (GTM 106), Ch. IV formal groups — the p-adic lift rests on the formal group logarithm; Menezes–Okamoto–Vanstone, IEEE TIT 39(5):1639–1646 (1993) for embedding-degree context; Galbraith, Mathematics of Public Key Cryptography 2nd ed. for the anomalous-curve/Smart chapter. Full records: Practice_runs/cryptohack_org/ledger_math.txt.

Trigger: server computes [k]P over Z/p^2 (modulus = p^2) and returns x mod p^2,
prime-order E(F_p), even with prime-order twist (twist primeness is irrelevant).

## Core idea (Smart/anomalous generalization)
1. Response r = x([k]P~) mod p^2 lifts to a FULL point Q~ = (r, sqrt(f(r))) mod p^2:
   f(r) is a QR mod p^2 because r is x of a genuine point mod p. sqrt: a^((p+1)/4)
   mod p (p=3 mod 4), then one Hensel step y = y0 + t*p, t = ((v-y0^2)/p)*inv(2*y0,p).
2. 0 -> E_1 = Z/p -> E(Z/p^2) -> E(F_p) -> 0 splits; [N] (N = #E(F_p)) kills the
   Teichmuller/order-N part and leaves E_1, where the formal group is ADDITIVE
   mod p^2 (a1=a3=0 => no degree-2 term; higher terms >= p^3 = 0).
3. u(R~) := t([N]R~)/p in Z/p with t = -x/y satisfies u(Q~) = +-k*u(P~) => k = ratio.
   The +- equals any min(k, N-k) server ambiguity; submit both candidates.

## Computing u without E_1 arithmetic (the trap)
Naive projective add/double formulas BREAK when the sum enters E_1 (Z3 = Z1*Z2*H
with H = 0 mod p gives an off-curve triple). Instead: [N]R~ = R~ + [N-1]R~ is the
degenerate chord x1 = x0 + p*d', y1 = -y0 mod p. Compute [N-1]R~ AFFINE mod p^2
(never degenerates for 0 < m < N, N prime), then closed form:
    u = d' * (y0 - y1)^{-1} mod p,   d' = (x0 - x1)/p mod p.
(Derivation: lambda = nu/(p d'), p^3*x_S = p*nu^2/d'^2, p^3*y_S = -nu^3/d'^3 mod p^2.)

## Gotchas
- Listener get_flag may need privkey as JSON int, not string (str % int TypeError).
- Clone the server ladder and run the full attack loop on random local k BEFORE
  connecting (10/10 check).
- Why prior analysis stalls: Teichmuller coord of the unknown [k]P~ looks
  uncomputable — but [N] annihilates it automatically; multiply the LIFTED RESPONSE.
- Verified on CryptoHack exceptional_twisted_mind (socket 13417, p=2^256-189).
