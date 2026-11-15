---
record: agent-aar
puzzle: challenge-257-cryptohack-eclcg-hitcon_ctf2024
category: ctf-archive
url: https://cryptohack.org/challenges/eclcg-hitcon_ctf2024/
status: solved
date: 2026-11-08
flag_ref: "FLAGS/ctf-archive/challenge-8-cryptohack-eclcg-hitcon_ctf2024/flag.txt"
flag_sha256: e8e89ba52193a84f561eb82a33eacc02ed46bb52a80d8bcab3179751ca9f2306
skills: []
human_twin: AAR.md
---

# AGENT — ECLCG (HITCON CTF 2024), challenge-257-cryptohack-eclcg-hitcon_ctf2024
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attacks tried (all fail, with reasons)" [OBSERVED text; evidence tag applies to its source, not each claim]
- **FHKLS / truncated-LCG lattices:** need known `a` (or linear recurrences in the
  outputs). Here `a` unknown and p-sized; the only `a,b`-free identities are the
  quadratic minors (fact 2). Dead at step one.
- **Linearized monomial CVP over (d, m):** monomials `{d, m, dm, mm, d², e_i·p}`,
  120–136 exact equations `V_ij − e_ij p = 0` over Z (p unknown ⇒ no congruence lattice
  exists). Volume-vs-determinant: log₂(box) ≈ 1.09·10^5 vs log₂(det) ≈ 8.7·10^4 ⇒
  ~2^22000 spurious lattice points in the box; lattice sees only linear structure and
  cannot enforce the rank-1 (`mm`) consistency that pins the true point. Same verdict for
  every variant tried (unknowns (k_i,d), (K_i,n_i), known-d restriction, 2-stage gcd plans).
- **Resultant / elimination to one variable:** every elimination path regenerates the
  unknown modulus (no F_p available to compute in); mod-q images regress to fact 4.
- **Degeneracy scan of the instance:** 17 distinct r,s (no repeated nonce ⇒ no k-leak),
  no small-k event (prob 2^-55·17), `a≠0/1` not detectable/needed — nothing degenerate.

## reusable-rules
- "Truncation bits" and "LCG quotients" are dual information stores (fact 4): always ask
  where the size budget went before designing the lattice.
- gcd-of-minors is a beautiful *given-d* primitive for unknown-modulus LCG — worth
  keeping, but here the hard part is exactly recovering that one parameter.

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: check_wall_evidence.py, solve.py, solve_port.py, synth_control_ec.py
- data/logs: audit_g1_run.log, audit_g1b_run.log, audit_g2_run.log, data.json, output.txt, progress.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
chall.py, output.txt, data.json (parsed z,t,u per signature), own check_wall_evidence.py (reproducible evidence suite). No third-party writeups/solutions consulted; no external reference named in run logs -- all facts self-derived and machine-verified.
