---
record: agent-aar
puzzle: challenge-303-cryptohack-u-turn-breizh_ctf2025
category: ctf-archive
url: https://cryptohack.org/challenges/u-turn-breizh_ctf2025/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-303-cryptohack-u-turn-breizh_ctf2025/flag.txt"
flag_sha256: 54278009ebfdbb9f7985d1a812502f02ccdf579a893c4763a3e5b524d3cff862
skills: []
human_twin: AAR.md
---

# AGENT — u-turn-breizh_ctf2025 (Breizh CTF 2025 "U-turn")
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The "hash" is linear over Z/256 on balanced-quinary digits: h = A*x mod 256 with
x_i ∈ {-2,-1,0,1,2} (l=50), A public (48x50). Finding a second preimage = finding
the unique small-coordinate point in a coset of the lattice
L = {(x,y) ∈ Z^98 : second block = A*x + 256y} near target (0, h).
Lattice params: det = 256^48 = 2^384, n=98 → GH ≈ 36; true distance ‖x‖ ≤ √(50·4) ≈ 14.1
→ unique-CVP regime.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- fpylll 0.6.4 API churn: LLL.lll / M.lll gone; use fpylll.algorithms.bkz2.BKZReduction
  (.lll_obj(), __call__(BKZ.Param(block_size=..., max_time=...))); CVP.closest_vector has
  no max_nodes kwarg. Plain LLL+Babai insufficient in the 98-dim projection formulation
  (run2.log: babai ok: False); BKZ-40 ~200s; CVP enumeration there did not finish <30min.
- This host's gp64 (PARI 2.17.4 minimal build) LACKS matinv, vecconcat, vecabs, mathide,
  calle (use matadjoint/matdet, matid...). GP matrix literals need ';' row sep WITHOUT
  inner brackets; Mat(list-of-vectors) treats vectors as COLUMNS.
- sympy: Matrix.rows()/rows are property vs row(i) method confusion; hermite_normal_form
  rejects rank-deficient input; sequential .rank() loops explode (coefficient blowup).
- Hensel bit-lifting to get a particular solution xp mod 256 works (rank(A mod 2)=47,
  3 free vars/level; only ~33k partials at level 6, first consistent lift gives xp).
- Reformulation used (plan E): R = rowspace([A;256I]) ⊂ Z^50; since 256Z^50 ⊆ R,
  L = {x : Ax≡0 mod256} = rowspace(256·R^{-1}) EXACTLY (integral basis).
  det L = |im(A mod 256)| ≈ 2^384 → det^(1/50) ≈ 205, GH ≈ 350 vs true ‖x‖≈10-14:
  unique-CVP with huge margin → Babai on LLL-reduced 50-dim basis expected to hit.
- x digits then recover out = Σ x_i 5^i + c·5^50 (c < 2^128/5^50), undo known-plaintext
  PKCS7 XOR-fold of BZHCTF{...} 24-char flag; verify hash(flag)==h.

## artifacts [OBSERVED]
- code: Arows.gp, diag1.py, glue_test.py, hvec.gp, ker.gp, ker2.gp, ker3.gp, ker4.gp, ker5.gp, ker6.gp, ker7.gp, solve.py, solve_c.py, solve_e.py, solve_f.py, solve_g.py, solve_h.py, solve_i.py, solve_j.py, solve_xp.py, xpvec.gp
- data/logs: flag_u-turn-breizh_ctf2025.txt, run2.log, run3.log, runJ.log, xp.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only; AAR records an in-campaign earlier-session prerequisite. Disclosure wording preserved verbatim:
> Hensel particular-solution xp (xp.json) was a prerequisite from an earlier session, not re-derived here.
