---
name: ring-eval-lwe-distinguisher
description: Use when ring-LWE secrets are small over split rings.
version: 1.0.0
author: Hermes campaign solver
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, lwe, lattices]
    related_skills: [ctf-crypto-attacks, ctf-lattices]
---

# Ring-LWE via trivial evaluation homomorphism (x→1 collapse)

## When to Use
Ring-LWE/MLWE (e.g. Dilithium params, R_q=F_q[x]/(x^256−1), q=8380417) where BOTH
secret and error have small integer coefficients AND the game/protocol leaks
(A, t=A·s+e). A distinguishing instance or a real key with small e/s2.

## Core idea
1. x−1 | x^n−1 always (1^n−1=0), so φ(p)=p(1)=Σ p_k is a ring
   hom R_q→F_q. It preserves INTEGER smallness: σ_j=Σ_k s_j[k] stays small
   (|σ| ≤ bound·n), and t(1)=A(1)·σ+μ (mod q) is a linear system with 15 box-
   constrained unknowns vs 8 equations mod q. MLWE ⇒ box solution exists;
   uniform t ⇒ expected count = box^{15}/q^8 (tiny).
2. Solve as Kannan CVP dim 15+1: rows (e_j|A1_·j|0),(0|q·e_m|0),(0|T|κ=500).
   LLL finds (σ,−μ,±κ) (norm ≤ bound·√15) vs lattice minimum √(15/2πe)q^{8/15}:
   gap ~50× at q=8.4e6 → plain LLL suffices. Decide: ∃row |last|=κ, ‖head‖<R.
3. Generalize: reduce mod (x^d−1), d | n: coefficients become class sums, box
   bound·n/d, 8d equations, 15d unknowns — margin (n/d)^{15d}/q^{8d} stays
   negative for d up to ~n/4; pick d trading dim vs FP margin.

## Pitfalls (all cost a real run)
- NTT values are NOT small integers: Σ s_k ζ^{ik} mod q has ζ^{ik} as big F_q
  residues; smallness lives in the COEFFICIENT embedding only. Never do
  per-NTT-coordinate box/CVP.
- Consistency of [Â|t̂] proves nothing: ê absorbs the residual.
- Lattice {(y,Ây+qz)} without the unit-row block y in coordinates has det q^d →
  dense garbage; put unknowns as real coordinates (unit rows) so det=q^{8d}.
- Kannan distance = ‖v_head‖ directly, κ already excluded by slicing.
- Windows fpylll build may lack Babai; nearest-plane with Fraction GS is 20 lines.
- Socket loops: carry unconsumed buffer across reads or you desync.

## Verify on own ground truth first
Generate synthetic (A,s,e,t); assert homomorphism identity T≡A1σ+μ; then FP/FN
on 5+5 before touching a live service.
