---
name: ctf-isogenies
category: ctf
description: "CryptoHack isogeny challenges: PARI Vélu isogenies."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, cryptohack, isogenies, velu, pari, j-invariant, sidh, csidh]
    related_skills: [ctf-answer-challenges, ctf-practice-runs, ctf-crypto-attacks]
---

# CryptoHack Isogenies — PARI `ellisogeny` is authoritative, NOT your memorized Vélu formula

## When to Use
Any CryptoHack **Isogenies** challenge (two_isogenies, three_isogenies, comp_isogenies,
special_isogenies, prime_power, whats_my_kernel, csidh_*, sidh_key_exchange, breaking_sidh,
better_than_linear, andré_encoding, ...). Most are *answer-type*: compute a j-invariant
or an isogeny map, submit the bare value (see `ctf-answer-challenges` for the wrapper rule).

## THE core lesson (learned the hard way, 2026-10-12, two_isogenies)
**Do NOT hand-derive a Vélu isogeny's codomain from a memorized formula.** My recalled
formula `a' = a - 4r², b' = b - 8r³` (Vélu 2-isogeny, kernel `(r,0)`) is WRONG — it
gave `a'=5, b'=8i` → `j=273636428973` for y²=x³+x, kernel (i,0), and that answer was
**REJECTED**. PARI's `ellisogeny` is the authoritative implementation and gives the true
codomain (here y²=x³+11x+14i → **j=287496**, accepted). Trust the tool, not the memory.

**Refinement 2 (2026-10-15, csidh_secret_exponents): PARI's `ellisogeny` CODEMAIN is
authoritative, but its returned POINT MAP / point list is BROKEN in the local gp64
build** — measured: a 420-point domain mapped to only 413 distinct images (not a
homomorphism). Never use PARI's isogeny map or the codomain's point list; use only
`ph[1]` coefficients, and do all point-level work with your own verified mapping.
A from-scratch Vélu engine (reconstructable from the Galbraith Thm-25.1.6 recipe below) is
self-contained (x-map, codomain reconstruction, CSIDH walk, Montgomery conversion)
and matched PARI step-by-step on a full 9-step walk — prefer it for multi-step walks.

**Refinement (2026-10-14, prime_power):** a Vélu implementation *derived from the primary
source and validated before use* is a fine independent cross-check. Thm 25.1.6 of
Galbraith et al. ("Mathematics of Public-Key Cryptography", Ch. 25), short-Weierstrass
specialization (a1=a2=a3=0, odd kernel, no G2 part): Fx=3x²+a4, Fy=−2y, u(Q)=4yQ²,
t(Q)=2(3xQ²+a4) summed over ±-pair reps; A4'=a4−5·Σt, A6'=a6−7·Σ(u+xQ·t). Validated
against the book's worked example (two_isogenies data: kernel (i,0) → 11x+14i ✓) and it
then matched PARI `ellisogeny` at all 27 chain steps. Rule: memory alone ≠ safe;
memory + primary-source check + tool cross-check = safe.

## Working PARI recipe — verified end-to-end
Invoke with the PARI/GP binary on PATH (`gp` on Linux/macOS, `gp64.exe` on Windows;
see `windows-crypto-toolchain` for the host-specific path). The minimal Windows build is
**file-based** (no `-c`): `gp -f -q prog.gp`.

For a Vélu isogeny of `y²=x³+a x+b` over a number field with kernel point `(r,0)`:
```gp
K  = bnfinit(t^2+1);        /* field: use var t (higher priority than x,y — else
                               'incorrect priority' error). */
i  = Mod(t, t^2+1);         /* the field element i (K.zk[1] also = t). */
E  = ellinit([0,0,0,1,0],K);  /* y^2 = x^3 + x  (a1..a6 = 0,0,0,1,0) */
ph = ellisogeny(E, [i, 0]);  /* Vélu isogeny. ph is a t_VEC of len 2. */
Cc = ph[1];                 /*   ph[1] = codomain as a 5-vec [a1,a2,a3,a4,a6] (NOT 16-vec) */
Cc = ellinit(Cc);           /* expand to full 16-vec; component [13] is the j-invariant */
print("j(E') = ", Cc[13]);  /* two_isogenies -> Mod(287496, t^2+1) = bare 287496 */
```
Structural gotchas (each cost time):
- `ellinit([a1..a6])` returns a 16-component vec whose **component [13] IS the j-invariant**
  (y²=x³−4x → [13]=1728). Don't call `ellj(vec)` — it errors "incorrect type (t_VEC)";
  read `[13]` instead.
- `ellisogeny(E,P)` returns `ph` where **`ph[1]` is the codomain** (short 5-vec
  `[a1,a2,a3,a4,a6]`). Re-run `ellinit(ph[1])` to expand and read `[13]` for j.
- Field var must be **higher priority than x and y** (use `t`) or
  `"incorrect priority in ellisogeny: variable x >= y"`.
- `bnfinit(Mod(t^2+1, p))` can fail `nfmaxord [not in Z[X]]`. **Usually you don't need the
  prime field**: if the codomain coeffs are in `Q(i)`, compute over `Q(i)`
  (`bnfinit(t^2+1)`, char 0) — the j lands in the **base field** (a plain integer).

## Answer-type j / Montgomery / image-point challenges (2026-10-12, all bare-value)
These are the low-point isogeny/lattice-adjacent answer challenges — no PARI isogeny
needed, just exact modular arithmetic:
- **j_invariant (20)**: y²=x³+145x+49 mod 163 → j = c4³/D via invariants (b4=2a, b6=4b,
  b8=−a²b; c4=−24b4, D=−8b4³−27b6²) = **127**.
- **c_group_homomorphism / Image Point Arithmetic (30)**: given P, Q on y²=x³+ax+b (p=63079),
  recover a,b from the two points (a = (y1²−y2²)/(x1−x2) − (x1³−x2³)/(x1−x2) mod p; verify both
  points on-curve), then plain EC addition → x(P+Q) = **43636**. An isogeny that preserves the
  group structure and has trivial image = just do the addition.
- **b_compute_montgomery / Montgomery Curves (30)**: E: y²=x³+ax+b (a=312589632, b=654443578,
  p=1912812599) → find A of the isomorphic y²=x³+Ax²+x.
  - j(E) = 915617603 (invariant method above).
  - **Montgomery j(A) = −64·(A²−3)³** — derive b2=4A, b4=**2** (a3²=1 — the off-by-one that
    broke the first attempt), b6=1, b8=0. Sanity: A=0 → 1728.
  - Solve (A²−3)³ = −j/64 mod p: cube root w (PARI `polrootsmod(Pol([1,0,0,−w_target],x),p)`),
    t = A² = 3+w, A = ±√t (p≡3 mod 4 → pow(t,(p+1)//4,p)). TWO roots share the j: **[flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt]**
    and 1385156202 ([flag — recorded in FLAGS/isogenies/challenge-205-cryptohack-b_compute_montgomery/flag.txt] accepted). Verify each with j_mont(A)==j(E) before submitting.
  - PARI trap: `polrootsmod([c0,c1,...], p)` errors `incorrect type in factormod (t_VEC)` —
    it needs `polrootsmod(Pol([c0,c1,...], x), p)`.
- **a_spot_super (25)**: find the supersingular curve in a list (Montgomery A, p=2^127−1).
  Supersingular ⟺ #E(F_p) = p+1 (Frobenius trace 0) — PARI `ellcard` (Schoof). Do NOT test
  j∈{0,1728} (only the two *rational* supersingular j's; there are ~p/12 mod p) and do NOT
  use j^((p−1)/2) (vacuous — Euler's criterion, true for every nonzero j).
- **iso_introduction_chall (10)**: conceptual (isogeny = degree-preserving morphism); bare answer.

## j-invariant cross-check in Python (independent of PARI)
For short Weierstrass `y²=x³+A x + B` with A,B in the base field (A,B may be imaginary but
A³,B² real): `j = 6912·A³ / (4·A³ + 27·B²)`. In F_p2 with `i²=-1`, `(u·i)² = -u²`.
```python
p=2**18*3**13-1
a=11; b2=-196          # (14i)^2 = -196
j = (6912*a**3) // (4*a**3 + 27*b2)   # = 287496
```
Two independent methods agreeing = confidence to submit.

## F_p2 field arithmetic in Python (implementing the map yourself)
Represent F_p2 as tuples `(a,b)`=a+bi, `i²=-1`, `p ≡ 3 (mod 4)` (F_p sqrt via
`pow(x,(p+1)//4,p)`). `mul=(a*c-b*d, a*d+b*c)`; `inv=(a/(a²+b²), -b/(a²+b²))`. To verify
a map WITHOUT square roots, work with **y²** directly (compare `y'²` to the codomain RHS).

## Converting the codomain to another model (special_isogenies, 2026-10-12)
Some challenges ask for the codomain in a **different model** (Montgomery y²=x³+Ax²+x),
not as a j-invariant. PARI's `ellisogeny` still gives the short-Weierstrass codomain;
convert it:

For y² = x³ + a x + b with a rational 2-torsion x-root v (find v: x³+a x+b=0):
1. Shift x = X + v  →  y² = X³ + 3v X² + (3v²+a) X.
2. Scale X = u² X′, Y = u³ Y′ with u⁴ = (3v²+a)  →  y² = X′³ + (3v/u²) X′² + X′.
3. **A = 3v / u²** where u² = √(3v²+a) (F_p sqrt: p≡3 mod 4 → pow(c,(p+1)//4,p)).

**A vs −A (corrected 2026-10-15 — replaces the old "twist lands ~0%" claim):** for
p ≡ 3 (mod 4), y²=X³+AX²+X and y²=X³−AX²+X are the **same F_p-isomorphism class**
(X→−X is an isomorphism because −1 is a nonsquare), so the explicit point-mapping
test passes for BOTH signs — it cannot disambiguate. The challenge convention is the
**principal square root**: A = 3v/√(3v²+a) with the principal √ (pow(c,(p+1)//4,p)).
Verified: special_isogenies → 199 (accepted) and csidh_secret_exponents → 404
(accepted), both principal-root values; −199=220 and −404=15 are the same class.
j_mont for the sanity check: j(y²=X³+AX²+X) = 256(A²−3)³/(A²−4) (the −256(A²−3)³/(A⁴+4)
variant in old scratch files is WRONG except at A=0).

## Identifying a SUPERSINGULAR curve in a list (a_spot_super, 2026-10-12)
Given a list of curves, find the supersingular one. Flag = its parameter (here the
Montgomery A of y²=x³+Ax²+x over p=2^127−1). **Do NOT test j by hand — two traps:**
1. `j ∈ {0, 1728}` is NOT the supersingularity test over F_p. For p≡3 mod 4 there are
   ~p/12 distinct supersingular j-values mod p, not two. (0 and 1728 are just the two
   *rational* ones.) Testing j∈{0,1728} finds nothing except the A=0 (j=1728) distractor.
2. `j^((p-1)/2) ∈ {1,−1}` is VACUOUSLY TRUE for every nonzero j (Euler's criterion) —
   it flags ALL curves. That is not a supersingularity test.
The correct, robust test is the point count: **supersingular ⟺ #E(F_p) = p+1** (Frobenius
trace a = p+1−#E = 0). Use PARI Schoof:
```gp
default(parisizemax, 1<<30);        /* ellcard overflows the default 8 MB stack */
p = 2^127-1;
E = ellinit(Mod([0, A, 0, 1, 0], p));   /* Montgomery y2=x3+A x2+x -> [0,A,0,1,0] */
if (ellcard(E) == p+1, print("SUPER A=", A), 0);
```
~400 ms/curve at 2^127, so 100 curves ≈ 40 s in a loop. The unique hit here was
A=[flag — recorded in FLAGS/isogenies/challenge-203-cryptohack-a_spot_super/flag.txt] (idx 60), card = p+1 exactly.
**PARI `if` is `if(cond, then, else)`** — a 3-arg function, NOT a block statement
(`if (c) stmt;` is a syntax error). Put `print(...)` in the then-slot.

## #E′(F_p) is NOT forced to be #E(F_p)/deg
For an ℓ-isogeny with a fully-rational kernel, #E′(F_p) can equal #E(F_p) (the dual
isogeny's kernel is also fully rational). Do NOT "reject" PARI's codomain because its
point count ≠ #E/deg — that reasoning is wrong for F_p-point counts. (special_isogenies:
deg 5, #E=#E′=420, perfectly consistent.)

## Flag format (per `ctf-answer-challenges`)
- "The flag is the j-invariant j(E')" → submit the **bare integer** (`287496`), no wrapper.
- **j ∈ F_{p²}\F_p → Sage field-element string: `<imag>*i + <real>`** (highest-degree term
  first, explicit `*`, spaces around `+`). comp_isogenies: `[flag — recorded in FLAGS/isogenies/challenge-211-cryptohack-comp_isogenies/flag.txt]`
  accepted after 6 wrong serializations (`imag*i + real` without `*`, `a+bi`, space/comma
  pairs, real-first). See ctf-answer-challenges for the general rule.
- Confirm non-singularity first: discriminant `-16(4A³+27B²) ≠ 0`.

## Composite-degree isogenies over F_{p²} (comp_isogenies, 2026-10-15, 60 pts, SOLVED)
3^13-isogeny of y²=x³+x over F_{p²}=F_p[i] (p=2^18·3^13−1), kernel K∈E(F_{p²}) of order
3^13. (Then-believed: PARI cannot do F_{p²} — DISPROVED 2026-10-21, see SIDH section:
`ellisogeny` works over ffgen t_FR fields.) Used a pure-Python Vélu engine (F_{p²} field, EC law,
Vélu-3, chain solver, f2_sqrt). Recipe:
- Q_0 = [3^12]K (order 3); φ_0 = Vélu 3-isogeny, kernel {O, Q_0, −Q_0} (odd degree: 2
  nonzero points; same Galbraith Thm-25.1.6 formulas as over F_p — only the field changes).
- Iterate k=0..11: K_{k+1} = φ_k(K_k) (order 3^{12−k}), Q_{k+1} = [3^{11−k}]K_{k+1}
  (order 3), φ_{k+1} = Vélu 3-isogeny. 13 steps → E_13. j(E_13) = 292990704480+249510360818i.
- F_{p²} field pitfalls (both cost a hang):
  1. **x^((q+1)/4) sqrt is INVALID in F_{p²}** — needs q ≡ 3 mod 4, but q = p² ≡ 1 mod 4
     always. Use Tonelli–Shanks (generic, field-agnostic).
  2. **TS non-residue search over F_p never terminates**: z^(p−1)=1 ⇒ z^((q−1)/2)=1 for
     EVERY z ∈ F_p. Search z in F_{p²} (start with i; half of F_{p²} are non-residues).
- End-to-end verification WITHOUT PARI (the triple, all cheap):
  (V1) total map kills K: φ_12∘…∘φ_0(K) = O;
  (V2) Frobenius: chain with conjugate kernel gives conj(j) exactly;
  (V3) total map is a homomorphism: total(P+R) = total(P)+total(R) on random F_{p²} points.
- Anchor: the FIRST step's codomain should land on a known curve — here E_1 was the F_p-
  twist of the server-verified three_isogenies codomain (same j=[flag — recorded in FLAGS/isogenies/challenge-208-cryptohack-three_isogenies/flag.txt], a6 = −a6 mod p).
  If step 1 doesn't land where PARI says it should, the engine is broken before you
  waste hours on 13 steps.

## Multi-prime CSIDH secret walk (csidh_secret_exponents, 2026-10-15, answer 404)
Secret vector [2,3,4] over primes [3,5,7] from E₀: y²=x³+x mod 419 → walk
[3,3,5,5,5,7,7,7,7] (pointwise ℓ-steps, degree 3²·5³·7⁴). Final codomain
y²=x³+196x+398 (j=48, #E=420); only 2-torsion root with 3v²+a a square is v=410
→ A = 3v/√(3v²+a) = **404** (principal-root convention). Verified 4 ways: 206
ground truth, prime_power AAR model-exact cross-check (5-walk & 7-walk), PARI
ellisogeny chain identical at all 9 steps, 419/419 Montgomery point-mapping.
Gotcha: the Vélu x-map image of a degree-ℓ isogeny sits on the challenge-convention
codomain (which has #E′ = #E, NOT #E/ℓ) as an ℓ-coprime subgroup — do not "fix"
the codomain to satisfy a naive point-count expectation.

## SIDH public key → kernel via ECDLP (whats_my_kernel, 2026-10-16, 70 pts, SOLVED)
Public key = images of a 2^e-torsion basis under the secret isogeny: E_A, P_B = φ(P_a),
Q_B = φ(Q_a), ker φ = ⟨P_a + n·Q_a⟩, n = secret. **First test: are the images collinear?**
If Q_B ∈ ⟨P_B⟩ (here it was — the two public points generate one cyclic subgroup):
1. ECDLP: Q_B = m·P_B, m mod 2^e. ℓ-adic LSB-first bit extraction (2-division chain):
   ~e doublings + e subtractions; pure Python over F_{p²} (434-bit p) ran in ~10 s.
   Verify by direct double-and-add (m·P_B == Q_B) before trusting any bit.
2. Kernel relation: φ(P_a + nQ_a) = P_B + nQ_B = (1 + n·m)·P_B = O; with
   ord(P_B) = 2^e (check: smallest s with 2^s·P_B = O) → **n ≡ −m⁻¹ (mod 2^e)**.
3. n IS the flag payload: read the FLAG placeholder length in the source BEFORE
   assuming hex. `bytes_to_long(FLAG[7:-1])` on a **27-?** slot = 216-bit int that was
   raw ASCII: −m⁻¹ mod 2^216 = 0x77686f6f…67 = b"whoops_this_was_just_a_dlog" →
   flag `[flag — recorded in FLAGS/isogenies/challenge-214-cryptohack-whats_my_kernel/flag.txt]` (accepted). The 215-bit ASCII "weirdness"
   was the author's planted answer, not broken data — two wrong submits first
   (19-hex-digit assumption: A mod 2^76; then the last-19-chars tail) both rejected
   with score_delta 0.
No isogeny computation needed at all when images are collinear. (If NOT collinear,
the kernel is a 2-dim relation and you need the full isogeny machinery.)

## Dual-isogeny attack when only ONE image point is public (dual_masters, 2026-10-22, 90 pts, SOLVED)
SIDH keygen, ker φ = ⟨P_a + n·Q_a⟩ over F_{p²}, p=2²¹⁶·3¹³⁷−1, public (E_A, φ(Q_a)) only.
Even one image point breaks it: φ(P_a) = −n·φ(Q_a) ⇒ φ(E[2^e]) = ⟨Q'⟩ = **ker φ̂** (dual
kernel = φ(E[deg]), always). So: build φ̂ as an e-step Vélu-2 chain from E_A with kernel
kernel ⟨Q'⟩, dualize step-by-step to get φ = φ̂̂, then φ(P_a) = k·Q' (2-adic DLP), n = −k mod 2^e.
Hard-won implementation facts (pure Python):
- **Vélu 2-isogeny, kernel (e,0), t=3e²+a: x' = x + t/(x−e), y' = y·(1 − t/(x−e)²)**,
  codomain a'=a−5t, b'=b−7et. (The tempting −y(1+t/(x−e)²) is WRONG; verify homomorphism
  numerically on a small curve before trusting any hand-written map.)
- **Each dual Vélu step lands on a TWIST of the intended old curve**: rescale by
  (X,Y)→(u²X,u³Y) with u² = (b·ad)/(bd·a) from the twist relation (ad,bd = dual-step
  codomain); sign of u³ (and μ₃-choice of u² when a=0) pinned by testing
  dual∘step = [2] on a generic tracked point. Without this the composed map doesn't land
  on E_A at all.
- **Final curve E_e ≅ E is only a 6-way twist** (j=0 here): need u2³=b_e (cube root via
  AMM lifting — no exponent works since 3 | q−1) and u3²=b_e; pick the scaling whose
  dual image of Q_a equals the public Q' (exactly one of 6 matches).
- **F_{p²} searches**: every element of F_p AND every diagonal a+ai is both a square and
  a cube in F_{p²} (p+1 even, 3∤p−1) — TS non-residue / AMM non-cube searches must scan
  (x,y) with non-residue norm x²+y² (e.g. (x,1) with x²+1 non-residue in F_p). Infinite
  loops otherwise, no error.
- Toy-probe fields must satisfy p≡3 mod 4 (p=1009 ≡1 mod 4 makes F_p[i]/(i²+1) a
  non-field and every sanity check meaningless).
- Flag was exactly 27 chars = 216 bits, so n mod 2²¹⁶ recovers it whole; check the '?'-
  count in the source's FLAG placeholder first.

## Repeated ℓ-isogeny walks (CSIDH-style; prime_power, 2026-10-14, answer 27)
Walk = repeatedly take the **pointwise** ℓ-isogeny: kernel E(F_p)[ℓ]. For ℓ | #E with
ℓ² ∤ #E it is cyclic of order ℓ → deterministic Vélu codomain. Pitfalls that cost hours:
1. **Carry the actual (a4,a6) Vélu codomain forward — never reconstruct curves from j.**
   Two F_p-twins (twists) with the same j have different pointwise ℓ-codomain j's
   (observed: j=98 models (239,292)→62 vs (67,113)→13). A j-level walk (curve_from_j
   each step) silently computes the wrong thing.
2. **"Unique rational ℓ-isogeny" is false when ℓ | p+1.** Then ℓ² | #E(F_{p²})
   (= p²+1−a²+2p) → ℓ-torsion is full (Z/ℓ)² over F_{p²} → TWO Galois-stable kernels:
   the pointwise E(F_p)[ℓ] and its conjugate. The CSIDH walk uses the pointwise one;
   the conjugate edge is a different curve.
3. **Read j-invariants mod p.** E0: y²=x³+x has j=1728 ≡ 52 (mod 419) — "52" IS 1728;
   the extra-automorphism (j=1728) special cases apply to E0 itself.
4. **Isomorphism to y²=x³+x:** (a4',a6') ~ (1,0) ⟺ a6'=0 and a4' a 4th power; for
   p=419, 4th powers = QRs (gcd(4,418)=2) → Euler test suffices.
5. All curves in the walk have #E = 420 (isogenous ⇒ same cardinality) → ℓ² ∤ #E at
every step → walk well-defined. Sanity: 4 (ℓ=5) / 6 (ℓ=7) pointwise order-ℓ points
   at each step.
prime_power facts: 5-walk j-seq 52→13→98→62→407→407→62→98→13→52 (9-cycle; 5^9 part:
"you see" it returns to E0, model 321x, 321=66⁴); 7-walk first return at **27**
(model 215x, 215=113⁴); j-seq palindromic. Both Python-from-scratch and PARI agree
step-by-step.

## PARI 2.17.4 (gp64.exe) parser quirks (2026-10-14, confirmed)
- **Python-written .gp files must use LF**: Windows `open(w)` writes CRLF and gp fails
  with misleading errors (`fopen` → "not a function", `for(i=1,#v` → "unexpected end of
  file"). Always `open(path, "w", newline="\n")`.
- `for (i, n, { ... })` brace blocks: **"embedded braces (in parser) is not yet implemented"**.
- **Top-level** multi-statement `for` bodies: syntax error; wrap in a function body.
- Multi-line `print(...)` inside a for body: parser breaks; keep each statement one line.
- `Str(a) + Str(b)`: "forbidden addition t_STR + t_STR" — use multi-arg `print`.
- Working pattern: functions with semicolon-separated, single-line for-body statements.
- Also: `if` is `if(cond, then)` / `if(cond, then, else)` (3-arg function form).

## Full SIDH key exchange in PARI over F_{p²} (sidh_key_exchange, 2026-10-21, 80 pts, SOLVED)
**gp64 `ellisogeny`/`ellisogenyapply` DO work over `t_FR` ffgen fields** — full 4-chain
SIDH (p = 2^110·3^67−1, 110+67 steps each way) ran in minutes where sympy was hopeless.
Recipe (Python generator emitting a .gp script):
- `f2 = ffinit(p,2,'x); w = ffgen(f2,'w)`; curve `ellinit([Mod(1,p)+0*w, Mod(0,p)+0*w])`.
- Recover the challenge's i-basis: D=a1²−4a0, β=lift(sqrt(Mod(-4,p)/Mod(D,p))),
  α=(a1·β·((p+1)\2))%p, `i_gp = Mod(α,p)+Mod(β,p)*w` (verify i_gp²=p−1).
- chain(E,R,ell,e,extras): `for(i=1,e, if(1, Q=ellmul(E,R,ell^(e-i)); iso=ellisogeny(E,Q);
  R=ellisogenyapply(iso[2],R); for(j=1,n, extras[j]=ellisogenyapply(iso[2],extras[j]));
  E=ellinit(iso[1])))` — the `if(1, ...)` idiom makes a multi-statement body parse.
- Return `[E, R, extras]` (NOT concat — concat splices the 16-vec curve). Index `res[3][1]`.
- **`ellj()` rejects t_FR curves** (and raw 5-vecs): compute j = 6912·a4³/(4a4³+27a6²).
- **t_FFELT has no polcoeff / no lift-to-int** (lift(lift(x)) stays t_FFELT): print the
  element (gp prints `A*w + B`) and parse in Python; convert basis there.
- Verify jAB == jBA before decrypting; key = sha256 of sage str `"<imag>*i + <real>"`.
- Python generator must use **rf-strings** (single-quoted `\` comments break gp; `{}` double).

## Running Sage without local Sage: SageCell HTTP+WebSocket protocol (breaking_sidh, 2026-10-22)
When Sage is not installed locally, `sagecell.sagemath.org` accepts programmatic code:
1. `POST /sockjs/kernel/info` body `{"language":"sage"}` → `{"session","secret"}`.
2. `wss://sagemath.org/sockjs/kernel/<session>/<server>/websocket` (ssl ctx, no verify),
   send `["execute", secret, {"code": ..., "options": {"print_mode":"plain"}}]`.
3. Messages `["stream",...]` (stdout), `["execute_result",...]`, `["output_status","idle"]` = done.
Limits/pitfalls: ~40 s CPU per cell (kernel dies mid-run → `kernel_dead`, RETRY: chunk work
so each cell ≤ ~6 oracle calls); state does NOT persist between cells → prepend a SETUP
block (field/curve/basis defs, ~2.5 s) to every cell; `interrupt` message does NOT stop a
CPU-bound kernel; `sage -python` ≠ plain python (use plain python3 + websocket-client).

## Castryck–Decru SIDH key recovery (breaking_sidh, p=2^117·3^75·5−1, f=45)
Port of jack4818/Castryck-Decru-SageMath to SageCell. Hard-won pitfalls:
- Original code shadows `i` (=√−1) with loop var `i` → NameError after first loop; rename.
- Original K search `2^a·3^(b−max_length)·R` until order 3 works ONLY for f=1 (exponent
  kills the 2-part because ord(P)=p+1 exactly). f=45: use K = ((p+1)/3)·R (order 3, 8/9).
- Off-by-one: original `i` is the 1-BASED digit number. 0-based digit di uses
  expdata[di], kernel 3^(b−di−1)·(P3+s·Q3), AuxiliaryIsogeny length di+1. Prolongation
  digits = even di≥2 (runs of one zero); di=2 is the special 3-way-test digit; all-split
  result = bad prolongation K → switch to alternativeK (Weil pairing ≠ 1).
- Gluing-curve discriminant test WITHOUT sqrt (Mumford): deg-8 h = ν²+ν·h1+h0 with
  h0=f1·h2', h1=f2·h2'−2f1·f1'; ν=x²+ν1x+ν0, ν1=−h1', ν0=(−h1·ν1−h0)/2; curve
  y²+ν1xy+ν0y = x³+Ax²+Bx+C, A=ν1²−4ν0, B=ν1ν0−4ν0, C=ν0². Disc(h)==0 ⟺ resultant(h,f2)==0
  (factor 4·disc(f2) is a nonzero square) — no square roots, no curve construction.
- Oracle cost ≈ 2^ai·0.02 s (ai = expdata value; shrinks as digits are found). ~134
  oracles total ≈ 10 min wall incl. per-cell overhead. State file + resume-on-death works.
- K→alternativeK swap is PERMANENT: after digit di=2 needs alt, EVERY later prolongation
  digit must use the alt chain (original reassigns EBprolong). Persist the alt flag in
  your resume state — a fresh cell defaulting to the K chain silently yields all-False
  prolongation digits that default to 2 (looks fine in logs; last-3 j-match then fails).
- Last-3 disambiguation: cand = key + t·3^(b−3), t ∈ 0..26 (27 values, not 25); test
  j(E0/⟨P3+cand·Q3⟩) == j(EB); chunk ≤13 chains per SageCell cell (CPU cap).
- PARI `ellisogeny` works over ffgen t_FR fields (2.17.4) — useful for small cross-checks
  of the gluing test on toy parameters.

## CSIDH key exchange from private vectors (csidh_key_exchange, 2026-10-22, SOLVED)
Given a_priv/b_priv exponent vectors over ells (CSIDH-512), shared = walk(E0, a+b),
secret = Montgomery A of final curve, key = sha256(str(A)).
- `E0 = EllipticCurve(F,[1,0])` in Sage = **y² = x³ + x** (a=1,b=0), NOT Montgomery A=1.
  Wrong E0 = not supersingular = every kernel search silently garbage (roundtrip tests
  catch it).
- Walk in SW form over F_p with Galbraith Thm 25.1.6 Vélu (validated challenge-214).
  Forward e>0: kernel E[ℓ](F_p): Q=((p+1)/ℓ)·R, R random F_p point. Backward e<0:
  anti-rational line: Q=((p+1)/ℓ)·(R−π(R)) over F_p², satisfies π(Q)=−Q; sums are
  π-invariant so codomain stays in F_p.
- Vélu reps = one point per ± pair: a'=a−5Σt, b'=b−7Σ(u+x·t), t=2(3x²+a), u=4y².
  The x-MAP sums over the SAME reps with coefficient 1 — summing over all ± points
  (doubling) gives a NON-homomorphic map while the codomain stays right (codomain
  roundtrips pass, homomorphism test fails — test BOTH).
- Validate against PARI at p=419: ellisogeny codomain j + ellisogenyapply images;
  fit x'=x+A/(x−xq)²+B/(x−xq) to PARI outputs to pin coefficients (A=u, B=t per rep).
- Final Montgomery A = 3v/√(3v²+a) where v = x-coord of the tracked image of 2-torsion
  (0,0) through every xmap (invariant under model rescaling; try ±A if decrypt fails).
- Python pow(0, P-2, P) returns 0 silently — kernel-point poles don't raise; don't rely
  on ZeroDivisionError as an oracle.

## BDGLS/VeluSqrt large-prime-degree isogeny (better_than_linear, 2026-10-24, 85 pts, SOLVED)
q=2.3e10-isogeny of y²=x³+x over F_{p²}, p=92935740571; answer j' = 48495725269*i + 91493879515 (accepted).
Recipe (paper: BDLS eprint 2020/341 Algorithm 2; PDF at velusqrt.isogeny.org, eprint direct is CF-walled):
- y²=x³+x IS Montgomery A=0,B=1 → Edwards codomain formula needs ONLY h(±1):
  d=((A−2)/(A+2))^ℓ·(h(1)/h(−1))⁸ = −(h(1)/h(−1))⁸; A′=2(1+d)/(1−d); j′=256(A′²−3)³/(A′²−4).
- h_S(α)=∏_{s∈S}(α−x([s]K)), S=odd 1..ℓ−2; index system (Ex. 4.7): b=⌊√((ℓ−1)/2)⌋, b′=⌊(ℓ−1)/4b⌋,
  I={2b(2i+1)}, J=odd<2b, K=S\(I±J); h(α)=h_K(α)·∏_i∏_j Q_α(β_i,x_j)/∏_i∏_j(β_i−x_j)².
- Biquadratics (A=0,B=1): Q_α=F0α²+F1α+F2, F0=(Z−x)², F1=−2(xZ+1)(Z+x), F2=(xZ−1)².
  Closed forms: Q₊=(x−1)²(Z²+1)−2(x+1)²Z; Q₋=(x+1)²(Z²+1)+2(x−1)²Z — (x±1)² SWAP, derive carefully.
- Resultants as Θ(#I·#J) double product are fine at 35-bit ℓ when numpy-vectorized: exact int64
  mulmod for p<2^37 via ((a>>19·b %p)<<19 + (a&(2^19−1))·b)%p (all intermediates <2^57); 5.8e9
  terms ≈ 24 min single-thread. True Õ(√ℓ) needs NTT poly arithmetic — not needed for the flag.
- Final vector→field product must multiply COMPLEX entries, not componentwise (silent wrong answer).
- Trace-0 supersingular E: EXPONENT of E(F_{p²}) is p+1 (π²=−p ⇒ [p+1]=0), not (p+1)²; toy generic
  K: R=[(p+1)/ℓ]T, K⁻=R−π(R) anti-rational, K=K⁺+K⁻; negate FULL field element (both parts) for −y.
- Validate on 4 toys (ℓ≈1e3–5e3) vs naive Vélu j BEFORE real run; toy caught both the Q₋ swap bug
  and a doubling +a typo. φ_x(α)=α^ℓ h(1/α)²/h(α)² lands on CH's B′-model — don't square-test vs B=1.

## SIDH with the auxiliary images MISSING (meet_me_claw shape)
Some SIDH instances ship Alice's (E_A, j(E_A)) but `phiA_P3 = phiA_Q3 = None` — the
auxiliary point images are deliberately withheld. Consequences, before wasting time:
- **Castryck–Decru and GPST/adaptive attacks are INAPPLICABLE** — both consume the aux
  images (Kani gluing needs φ(P3),φ(Q3); GPST needs the peer to evaluate your malicious
  points). No oracle exists in a static key-exchange-with-encryption setup.
- What remains is plain **ECDLP in the 2-isogeny volcano**: meet-in-the-middle claw,
  ~2^(e_a/2) work — forward table of 2^(e_a/2) leaf j-invariants from E0, backward walk
  from E_A, match on j. Feasible for e_a ≈ 35–46 in pure Python (p ≈ 80 bits, table
  ~8M entries, hours).
- If Bob's secret is also given (as in the challenge), the shared j = walk E_A by Bob's
  3-path once Alice's 2-path is recovered; key = sha256(str(j)) per the statement.
- Implementation facts for the walk (pure Python F_{p²}): trace-0 supersingular E ⇒
  EXPONENT of E(F_{p²}) is p+1 (toy-basis multipliers 3^e_b / 2^e_a, not (p+1)²/2^e_a);
  off-walk curves have only ONE rational 2-torsion point — a "3 roots" assumption hangs;
  PARI-cross-check every hand-rolled Vélu closed form (the x(P+Q)+x(P−Q) recollection is
  wrong; Galbraith Thm 25.1.6 form is right).
- **CONFIRMED SOLVED 2026-10-25 (meet_me_claw, 120 pts, p=2^35·3^29−1):** split 23+12
  worked exactly as above. Forward 2^23 leaves ≈ 3.6h pure Python (672µs/node — one
  modular inverse per point op dominates; budget for this BEFORE launching, and chain
  fwd→bwd→final in ONE background runner script, polling cheaply). Backward 3^12 tree
  ≈ 27min, EXACTLY 1 j-match (no twist false positives). Recovered a, re-ran full
  35-step walk tracking P3,Q3, H = φ(P3)+sB·φ(Q3), 29-step Vélu-3 chain, j(E_AB),
  key = sha256 of `"<im>*i + <re>"` → flag accepted first try.
- Progress-monitoring on Windows: WorkingSet64 is trimmed by the OS and lies; use
  PrivateMemorySize64 (or Get-Counter '\Process(python*)\Private Bytes') to watch a
  long-growing dict.

## Pitfalls
- **Unvalidated memorized Vélu formula = WRONG** (a'−4r², b'−8r³). Use PARI
  `ellisogeny`, or a primary-source implementation validated + cross-checked.
- `ellj(t_VEC)` errors; read component `[13]`.
- `ph[1]` (codomain) is a 5-vec, not the 16-vec; `ellinit(ph[1])` to expand.
- Field var `x`/`y` collides with curve vars → use `t`.
- If the j is rational, skip F_p2 in PARI; compute over `Q(i)` and read the base-field part.
- Vélu j-invariants here are always **base-field integers** (imag part cancels). PARI's
  `Mod(J, t²+1)` with a `0*t` part → `J` is the answer.
