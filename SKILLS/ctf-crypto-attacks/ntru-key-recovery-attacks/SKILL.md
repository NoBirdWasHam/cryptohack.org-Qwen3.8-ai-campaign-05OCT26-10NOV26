---
name: ntru-key-recovery-attacks
description: Use on NTRU-shaped lattices or secret pairs h=g/f mod q.
version: 1.0.0
author: Hermes (CryptoHack AAR program)
license: MIT
metadata:
  hermes:
    tags: [crypto, ntru, lattice, folding, ctf]
    related_skills: [ctf-lattices, ctf-crypto-attacks]
---

# NTRU key-recovery — attack ladder beyond plain BKZ

## When to Use
Any NTRU-shaped object: h ≡ g/f mod q in a polynomial ring, ideal-lattice challenge with
a planted (f|g)-style short vector, or a 'NTRU'/'folding'/'rotation lattice' tag where
plain BKZ stalls — check for exploitable structure BEFORE throwing bigger block sizes.

Detect the shape first: public h with small f,g and h·f ≡ g (mod q) in R = Z[x]/(φ),
or a challenge lattice whose planted short vector splits as (f | g) with cyclic/rotation
symmetry. If the lattice is a rotation-closed module (x^i·(f,g) all short), plain BKZ is
the WEAK attack — structure attacks below beat it.

## Ladder (cheapest first)
1. Dense-sublattice / overstretched test (Ducas–van Woerden; Pataki–Tural lemma;
   algebraic version eprint 2024/844): if q is large vs σ, the q-ary NTRU lattice
   Λ_h = {(x,y): hx−y=0 mod q} contains the rank-2 dense submodule of rotations of (f,g).
   Test: run moderate BKZ (β ≈ 60–120) and watch the log-GS profile for a STEP — a step
   at position i means a rank-i dense submodule found; from it, key recovery is linear
   algebra. Cheap detector, do it early.
2. May–Silverman / May projection: reduce dim 2n→n by projecting away all but one
   rotation of (f,g) (raises λ1/λ2 gap). Build from the h-rotations directly; then BKZ on
   half the dimension with the SAME budget usually wins.
3. Folding (Atamagorodov–Coster, Crypto'99): for φ = x^n+1 (n even), split f = f0 + x·f1
   etc.; the even/odd sublattice of dimension n recovers (f0,f1,g0,g1) up to a small
   kernel; iterate the 2–4 leftover coset choices. Check φ's automorphism group size
   first — folding strength scales with it (x^n+1, 2-power n: rich; random φ: none).
4. Subfield attack (CJL / Albrecht–Bai–Ducas, eprint 2016/717): push the secret norm into
   a subfield of Q(ζ); needs φ with subfields (2-power cyclotomic: yes). Compute the β
   requirement vs the field index before trying.
5. Howgrave–Graham hybrid (reduction + MITM on middle coefficients): last resort when β
   must stay small; MITM memory 2^m for m guessed coefficients.
6. uSVP framing sanity: gap = gh(Λ_h)/||(f,g)|| with gh ≈ √(d/2πe)·det^{1/d}; price with
   the CN11 simulator (fpylll) BEFORE enumerating. Note λ2 = λ1 in NTRU lattices — uSVP
   heuristics assuming λ2 = gh overstate difficulty; the dense submodule is really there.

## Stall diagnostics (run BEFORE buying more compute)
- To separate construction bug / runner bug / genuine compute wall, build a planted
  real-shape control (same params, dimension, secret weight) and push it through the
  EXACT same pipeline — same builder, same runner scripts, same scan. Toy mirrors real at
  every stage => compute wall: price beta, don't debug. Toy falls where real stalls =>
  bug is in that stage's construction; diff lattice invariants (log2 det, q-row count,
  GS head) to localize.
- Audit candidate-acceptance gates against the planted with exact combinatorics (DP, not
  sampling): a gate that passes the planted only a few percent of the time mimics a
  reduction wall perfectly (typical cause: overlap slots where the planted legitimately
  carries values beyond the gate's bound). Fix gates before crediting bigger beta.
- Folded hierarchies fall bottom-up: the more-folded (smaller-dim) lattices fall at much
  smaller beta — solve those first, bank the recoverable secret components now (verify
  by exact ring identity), and wire the deterministic finisher that consumes the rest so
  the hard stages auto-complete the moment a vector drops.

## Practical notes
- fpylll: basis [qI | H; 0 | I], H = multiplication matrix of h mod φ (columns = x^i·h
  mod φ). CVP variant: target (0, t) via Kannan embedding.
- Symplectic speedups (Gama–Howgrave-Graham–Nguyen) exist but fplll has no native flag;
  irrelevant for correctness.
- Verify found (f,g): h·f ≡ g mod (φ,q) exactly; ||(f,g)|| matches the planted
  distribution. ANY sufficiently small multiple of f suffices to break (CS97) — exact
  f,g not required.
- If the challenge dir has a scan/flag pipeline, route every sub-threshold vector
  through it; read the challenge AAR for the exact norm threshold.
