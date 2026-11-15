---
record: agent-aar
puzzle: challenge-130-cryptohack-matrix_revolutions
category: Diffie-Hellman
url: https://cryptohack.org/challenges/matrix_revolutions/
status: solved
date: 2026-10-20
flag_ref: "FLAGS/diffie-hellman/challenge-130-cryptohack-matrix_revolutions/flag.txt"
flag_sha256: 0f08918fe24a33001989b290916f7979e0b1de1e4ff54280d9bcad5628577d58
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 130: The Matrix Revolutions
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved (reproducible)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Structure** (`getpols.py` + gp64): charpoly(G) = f1·f2, irreducible deg 61 & 89, exps 1.
   ⇒ algebra F2[x]/charpoly ≅ GF(2^61)×GF(2^89); ord(G) = (2^61−1)(2^89−1), both Mersenne primes.
2. **Targets** (`step1.py`): Krylov solve A_pub = h_A(G) over the basis {G^k}; rA1 = h_A mod f1,
   rA2 = h_A mod f2 (same for B) → `targets.json`. (Krylov correctness is implied by step 5's gates.)
3. **DLOG by index calculus** (`ic6.c`, C, u128 bitmasks):
   - Factor base = monic irreducibles deg ≤ D (buildfb, ascending).
   - Relation search: walk a = x^i (mulx-reduced), accept iff squarefree + all irreducible
     factors deg ≤ D (exact `ddf` + exact division; NO norm heuristic in ic6).
   - 89-bit block: D=14 (nfb=2537), P(smooth)≈2.9e-6; 7 parallel searchers, offsets 1e9…7e9,
     5200 general relations. 3 factor-base elements never appeared → **targeted search** (mode T:
     walk x^i·p, relation gets coefficient −1 for p; ~2e6 iterations each).
   - Linear algebra over Z/(2^m−1) (Φ prime for m=61,89): Gauss-Jordan with modinv.
     Final rank 2536/2537 (89-bit) and 745/746 (61-bit): solved anyway — target log is
     determined iff target vector ⊥ kernel: slope = [free col in factors] − Σ_piv e_j·A_RREF[j][free];
     print only when slope==0.
   - **Self-verification built into Z mode:** x^lg == h (poly modexp) must hold before printing
     (`VERIFY … OK` on stderr). This gate is what caught the muln bug below.
4. **61-bit block:** D=8 was 5000× too slow (P≈1.9e-8 empirically); D=12 (nfb=746, P≈9e-5) →
   1800 relations in ~50 s.
5. **Assembly** (`step3.py`): CRT(l61 mod 2^61−1, l89 mod 2^89−1) → A, B; gates; key =
   SHA256(''.join(bits of shared rows))[:32]; AES-CBC decrypt → flag.

## reusable-rules
- Matrix DH over GF(2) with split charpoly = direct product of extension fields; DLOG reduces
  to per-factor index calculus; CRT the exponents; ord(G) = lcm of the field group orders.
- Function-field smoothness at q=2 deviates strongly from ρ(u) at small D (61/8 measured 1.9e-8
  vs ρ≈1e-6): MEASURE P(smooth) on ~5e5 iterations before committing to a search budget.
- 2^61−1 and 2^89−1 are both prime (Mersenne exponents) → Z/Φ is a field, Gauss-Jordan with
  Fermat modinv is valid; composite Φ would have needed per-prime-factor CRT Gauss.
- Parallel relation search: disjoint i0 windows, merge files, ONE Gauss pass; ~1.5e5 tests/s/core.

## anti-patterns / limits
- Worked only from the provided zip + my own code. No solutions page, no writeups, no shared flags.
- Did NOT modify the Krylov step (its output is validated end-to-end by G^A==A_pub).
- Submissions: exactly one flag submission for this challenge (score_delta +125).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: flag_matrix_revolutions.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement page: https://cryptohack.org/challenges/diffie-hellman/ (card "The Matrix Revolutions", 125 pts).
- Provided file: https://cryptohack.org/static/challenges/matrix_revolutions_2d9c03dde281a05e89519d9cd356d19c.zip
  → unzipped/ (matrix_revolutions.sage, generator.txt, alice.pub, bob.pub, flag.enc).
- NOT consulted: /challenges/matrix_revolutions/solutions/, any writeup, any third-party flag.
