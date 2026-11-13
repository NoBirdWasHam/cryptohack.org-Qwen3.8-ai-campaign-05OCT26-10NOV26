---
record: agent-aar
puzzle: challenge-206-cryptohack-special_isogenies
category: isogenies
url: https://cryptohack.org/challenges/special_isogenies/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/challenge-206-cryptohack-special_isogenies/challenge-206-cryptohack-special_isogenies/flag.txt"
flag_sha256: 29ef5f0b7fc0c2facd22af7e616542825331312745dfc31f37423ab0b5e005ee
skills: [ctf-isogenies]
human_twin: AAR.md
---

# AGENT — special_isogenies (CryptoHack Isogenies, 30 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Method" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **PARI `ellisogeny`** (per `ctf-isogenies` skill): codomain **y² = x³ + 269x + 82**,
   j = 13, #E′ = 420. (Consistent with the isogeny theorems: #E′/#E = 5 is not required
   for F_p-point counts — the dual isogeny's kernel is fully rational, so #E′ can equal #E;
   the initial "must be 84" intuition was WRONG for F_p-point counts.)
2. **Montgomery conversion** (short-Weierstrass → y²=x³+Ax²+x):
   - rational 2-torsion root v = 23
   - x = X + 23 → y² = X³ + 69X² + 180X
   - scale u⁴ = 180 → u² = √180 = 173
   - **A = 69/173 mod 419 = 199**
3. **Twist disambiguation**: j(A)=13 has two F_419 solutions {199, 220} (twists).
   Applied the explicit isomorphism (X=x−23, X′=X/u², Y′=Y/u³) to all 210 F_419 codomain
   points: **210/210 land on A=199, 1/210 on A=220** → A=199.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Hand-rolled Vele x'/y' maps and memorized codomain-coefficient formulas repeatedly failed point-consistency checks — lesson banked in the `ctf-isogenies` skill: use PARI `ellisogeny`, never hand-derive Velu data; the only real work is the model conversion.
- Several rounds lost to the #E' = 420 != 84 misconception above.
- PARI syntax friction cost time (file-based gp64, `subst` vs call syntax, `poldegree` not `degree`) — recorded in `ctf-isogenies`.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
PARI/GP `ellisogeny` (manual); `ctf-isogenies` skill; evidence quoted in the original AAR (server JSON `score_delta:30`, PARI codomain output, 210-point Python check); `solve.py` in this folder. No solutions/writeups consulted.
