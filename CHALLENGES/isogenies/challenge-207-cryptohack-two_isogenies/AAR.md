# AAR — two_isogenies (CryptoHack Isogenies, 30 pts)

Date: 2026-10-12 · Worker: Hermes · Status: SOLVED (+30, verified by server)

## Result
- Flag `287496` submitted bare → server delta **+30**, score 6295→6325, solved 132→133.
- Computed answer: j(E′) = 287496 for the Vélu 2-isogeny φ₂: E → E′ of
  E: y² = x³ + x over F_p² (p = 2^18·3^13−1), kernel (i, 0).

## Method that worked
1. **PARI/GP `ellisogeny`** (gp64 2.17.4, file-based `-f -q`):
   `bnfinit(t^2+1); i=Mod(t,t^2+1); E=ellinit([0,0,0,1,0],K); ph=ellisogeny(E,[i,0]);`
   → codomain **y² = x³ + 11x + 14i** (over Q(i)); j(E′) read from `ellinit(ph[1])[13]`
   = `Mod(287496, t²+1)` (base-field, 0·i part).
2. **Independent Python cross-check** (rational j formula for y²=x³+Ax+B):
   j = 6912·A³/(4A³+27B²), A=11, B=14i ⇒ B²=−196 ⇒ j = 9199872/32 = **287496**. Both methods
   agree exactly.
3. Non-singularity: discriminant −16(4·11³+27·(−196)) = −512 ≠ 0.

## What went wrong (and the root cause)
- First answer **273636428973** (both bare and `crypto{…}`-wrapped) → rejected (delta 0).
- That value came from the **memorized Vélu codomain formula** a′ = a−4r², b′ = b−8r³, which
  for r=i gives a′=5, b′=8i. PARI's authoritative `ellisogeny` contradicts it
  (a₄=11, a₆=14i). **Conclusion: the memorized formula was wrong**, not the arithmetic.
- Side effect: I spent many turns trying to make a hand-rolled Vélu *map* (x′,y′ formulas)
  "land" on my hand-derived codomain; it never did — a correct map can't land on a wrong
  codomain. That mismatch was the tell that the codomain, not the map code, was at fault.
- PARI usage friction (each a real cost, now documented in skill `ctf-isogenies`):
  - gp64 takes GP files, not `-c`.
  - `ellj(<16-vec>)` errors "incorrect type (t_VEC)" — read component `[13]` instead.
  - `ellisogeny` returns `ph` with **`ph[1]` = 5-vec codomain** [a1..a4,a6]; must re-`ellinit`
    to read j at `[13]`.
  - Field variable must outrank x,y (use `t`) or "incorrect priority" error.
  - `bnfinit(Mod(t^2+1,p))` fails `nfmaxord [not in Z[X]]` — but unneeded: computing over
    Q(i) suffices because the j-invariant is a base-field integer.

## Evidence inventory
- Server: `submit_flag.py two_isogenies 287496` → `{"score_delta": 30, "after": {"score": 6325, "solved": 133}}`.
- PARI: codomain a4=Mod(11,t²+1), a6=Mod(14t,t²+1); j=Mod(287496,t²+1).
- Python: 6912·11³/(4·11³+27·(−196)) = 287496 exactly.

## Lessons (→ skill `ctf-isogenies`)
1. **Never hand-derive isogeny codomains from memorized Vélu formulas — use PARI
   `ellisogeny`**, then cross-check the j with the rational formula. Two independent
   methods agreeing = submit.
2. A map that refuses to land on your derived codomain is evidence the **codomain** is wrong.
3. Flag format: "the j-invariant j(E′)" → bare integer.

## Open items
- ~10 more isogeny challenges (three_isogenies 35, special_isogenies 30, prime_power 50,
  comp_isogenies 60, whats_my_kernel 70, csidh_* 60–90, sidh_key_exchange 80,
  breaking_sidh 250, …). Same PARI workflow applies; CSIDH/SIDH ones likely need
  F_p² point arithmetic (no fpylll dependency observed for the answer-type ones).
- GMP/fpylll build still unresolved (lattice/isogeny-graph heavy challenges only).

## Vulnerability (plain words)

No exploit here — it is a computation problem. The challenge fixes E: y² = x³ + x
over F_{p²} (p = 2^18·3^13−1) and a rational 2-torsion point (i,0), and asks for
j(E/⟨(i,0)⟩). The only skill tested is computing a 2-isogeny's quotient curve
correctly; there is nothing adversarial to break.

## How the answer follows

- Vélu's formulas for a 2-isogeny with kernel generator (e,0) in short
  Weierstrass form: t = 3e²+a, a′ = a−5t, b′ = b−7et. With e = i (i²=−1), a = 1:
  t = −2, a′ = 11, b′ = 14i — exactly the codomain y² = x³ + 11x + 14i that PARI's
  ellisogeny returned.
- j = 6912·a′³/(4a′³+27b′²): 4·11³ + 27·(14i)² = 5324 − 5292 = 32, so
  j = 6912·1331/32 = 287496 — a base-field integer (zero i-part), which is the flag.
- Two independent engines (PARI ellisogeny; closed-form j) agree, and the server
  accepted the bare integer.

## Limitations / attempts that failed

- First submission 273636428973 (rejected): came from a mis-memorized codomain
  formula a′ = a−4r², b′ = b−8r³ (the x-only/Montgomery-style 2-isogeny, not this
  short-Weierstrass Vélu codomain). Wrong formula, not wrong arithmetic.
- Several turns burned hand-rolling a Vélu *point map* that "never landed": a
  correct map cannot land on a wrong codomain.

## Sources

- PARI/GP 2.17.4 ellisogeny (ground truth for the codomain).
- Standard Vélu formulas (textbook math; the mis-memorized variant was corrected
  against PARI).
- No CryptoHack solutions page or third-party writeup consulted for this challenge
  (run log).
