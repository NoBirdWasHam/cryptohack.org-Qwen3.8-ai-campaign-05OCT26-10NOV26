---
record: agent-aar
puzzle: challenge-210-cryptohack-prime_power
category: isogenies
url: https://cryptohack.org/challenges/prime_power/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/isogenies/challenge-210-cryptohack-prime_power/flag.txt"
flag_sha256: 932ab0a0e4191d32c0af7b3f565b7b180dbe9869378abc5816f9add54b806e7f
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 210: Prime Power Isogenies (50 pts, isogenies)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Solution" [OBSERVED text; evidence tag applies to its source, not each claim]
**Model.** At each step take the *pointwise-rational* l-isogeny: kernel E(F_p)[l].
Since l ∈ {5,7} divides 420 = #E but l² ∤ 420, E(F_p)[l] is cyclic of order l → unique
pointwise kernel → Vélu codomain is deterministic. (Isogenous curves keep #E = 420, so the
property holds at every step.) Vélu formula (Galbraith et al. Thm 25.1.6, short-Weierstrass,
odd kernel): with u(Q)=4yQ², t(Q)=2(3xQ²+a4) summed over ±-pair reps:
A4' = a4 − 5·Σt, A6' = a6 − 7·Σ(u + xQ·t).

**Implementation 1 (Python, `solve.py`).** From-scratch EC arithmetic + Vélu. Formula
validated against the book's worked example (two_isogenies: y²=x³+x / Q(i), kernel (i,0)
→ y²=x³+11x+14i, j=287496 — reproduced exactly).

**Implementation 2 (PARI/GP 2.17.4, `pp_verify27.gp`).** `ellisogeny(E, S[1])` with
S = all pointwise order-l points (brute-force enumeration). Built-in Vélu, independent of
implementation 1.

**Results (both implementations, step-by-step identical):**
- 5-walk j-sequence: 52 → 13 → 98 → 62 → 407 → 407 → 62 → 98 → 13 → **52** (d=9).
  Model at d=9: y² = x³ + 321x; 321 = 66⁴ = 353⁴ mod 419 → **isomorphic to E0**.
  → "what do you see": the degree 5^9 isogeny lands back on the starting curve (9-cycle).
- 7-walk: first return to E0's isomorphism class at **d = 27** (model y² = x³ + 215x;
  215 = 113⁴ = 306⁴ mod 419). No earlier step is isomorphic to E0. j-sequence is palindromic
  around the middle (…407 | 396 396 | 407…).

**Submission:** `submit_flag.py prime_power "27"` → HTTP 200 "Flag submitted"; API user
endpoint confirms score 7145 → 7195 (+50), solved 154 → 155.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
1. **j(E0) = 1728 mod 419 (52).** E0 is the mod-419 reduction of the j=1728 curve.
   j-invariants here should be read mod p: "52" *is* 1728. (Nearly caused a wrong
   special-case analysis.)
2. **Two rational l-isogenies per curve, not one.** Over F_{p²}, l-torsion is full
   ((Z/l)² since l² | #E(F_{p²}) = p²+1+2p): each curve has a second, Galois-conjugate,
   non-pointwise rational l-isogeny. The CSIDH walk (and this challenge) uses the
   *pointwise* kernel E(F_p)[l]. Any "unique rational l-isogeny" assumption is only valid
   when l² ∤ #E(F_{p²}).
3. **j-level walks are NOT well-defined.** Two F_p-twins (twists) with the same j can have
   different pointwise l-isogeny codomain j's (observed for j=98: models (239,292)→62 vs
   (67,113)→13). The walk must be followed on actual (a4,a6) models (the Vélu codomain),
   never by reconstructing curves from j. My first PARI attempt did exactly that
   (curve_from_j each step) and produced a wrong 2-cycle; the Python model-level walk is
   the correct one.
4. **Isomorphism test to E0:** (a4',a6') ~ (1,0) ⟺ a6'=0 and a4' a 4th power; for p=419
   the 4th powers are exactly the QRs (gcd(4,418)=2), so a QR test suffices.
5. **PARI 2.17.4 (gp64.exe) parser quirks (confirmed again this session):**
   - `for (i, n, { ... })` brace blocks: "embedded braces (in parser) is not yet implemented".
   - Top-level multi-statement `for` bodies: syntax error; works inside a function body.
   - Multi-line `print(...)` inside a for body: parser breaks; keep each statement on one line.
   - `Str(x) + Str(y)` string concatenation: "forbidden addition t_STR + t_STR" — use
     multi-arg `print`.
   - Working pattern: functions with semicolon-separated single-line for-body statements
     (see `pp_graph.gp`, `pp_verify27.gp`).

## artifacts [OBSERVED]
- code: pp_verify27.gp, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Galbraith et al., Thm 25.1.6 (Vélu short-Weierstrass formulas), pre-validated
  against the two_isogenies worked example.
- PARI/GP ellisogeny as the second implementation.
- No third-party writeups or solution pages consulted (AAR: self-solve).
