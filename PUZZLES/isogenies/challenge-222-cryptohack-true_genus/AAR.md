# true_genus — AAR (parked OPEN, 2026-10-24)

## Status: UNSOLVED after 3 solver deaths + 1 orchestrator session. Parked deliberately.

## What the challenge is (fully understood)
- CSIDH-style class-group action on the F_p-supersingular/CM orbit of E0: y²=x³+1 (j=0),
  p = 2·prod(ls)−1, ls = 29 primes [3..109,139], p ≈ 2^155, p ≡ 1 mod 4, p ≡ 2 mod 3.
- Orbit of E0 under ± l-steps (l ∈ ls; + = quotient by E(F_p)[l], − = twist trick) is a
  torsor for Cl(−4p) ≅ Z/h, h = 36q, q = 14356745447089083514493 prime (verified via bnf,
  bnf.dat cached; cls6.gp/cls6.out have c_i = class of 𝔭_{l_i} mod h, gcdall=1).
- CONFIRMED on small testbed p=1289 (h=36 cyclic, ls=[3,5,43]): BFS orbit = 18 j-invariants
  = 36/2 (j identifies E with its quadratic twist, x ↔ −x). orbit.gp works after fixing
  `ellisogeny` codomain components E2[4],E2[5] (was E2[5],E2[6] — broken, never ran).
- 63 instances (SECRET has top bit 0). bit=1: EC = privA·EB; bit=0: EC = privC·E0 with
  privC resampled until backdoor(privC) != backdoor(privA)·backdoor(privB).
- Flag = AES-256-CBC(SHA256(SECRET)[:32]) — need all 63 bits right (or search flips).

## Backdoor analysis (NEW, this session)
- `b *= e ^ m` is XOR, not exponentiation. backdoor(priv)=0 iff ∃i: priv_i == e_i.
- P(hit) = 1−(6/7)^29 ≈ 0.99 → t = 0 with prob ~0.99 → in bit=0 instances privC almost
  surely AVOIDS e coordinate-wise (c_i ≠ e_i ∀i). Support of x_C in bit=0 ≈ 6^29 ≈ 2^75
  (sparse vs h ≈ 2^78.2); bit=1 support is dense. Bias is real but only exploitable if
  the class of EC is computable — which is the same hard problem.

## Approaches tried and KILLED (with evidence)
1. Quartic/quadratic characters of a4, a6, Δ, j−1728 on the REAL 63 instances:
   residual distributions uniform (tg2.py) — no signal.
2. Small-orbit homomorphism test (p=1289, all 36 classes with known x, tg4/tg5.py):
   NO invariant among {jac,q4,q3 over Fp and Fp2} of {a4, a6, Δ, −48a4, a·+w, D+w, j+w}
   satisfies val(x)=g^x; lq4(a6) vs x mod 4 uncorrelated. Cheap curve-level class
   invariants do not exist for this family.
3. Mod-36 extraction via long isogeny walks: min-degree smooth ideal in a random class
   ≈ 2^65+ (lattice estimate, dim-29 relation lattice det h) — infeasible walk.
4. q-part via Pollard rho in q-subgroup: 2^37 class ops — infeasible.
5. DRAK-style distortion-map/Weil-pairing distance: l-Sylow trivial for l ∤ 36q — the
   local invariants carry no class info here.
6. Brute force / MITM on 7^29 key space: 2^81 — infeasible.

## What would unlock it
- A way to compute x_E mod 4 or mod 9 from (a4,a6) — the small testbed (orbit_small data
  in small3.out, p=1289) can test ANY candidate invariant in seconds. Bring candidates:
  2-isogeny descent invariants (root e of x³+a4x+a6, invariants of the 2-isogenous curve),
  cubic-residue symbols in Z[ω] of 3-division values, Hilbert class field evaluations.
- Or: exploit the backdoor sparsity jointly across instances (63 sparse-set memberships).
- The bit test only needs Δ = x_C−x_B−x_A mod 36 == 0 (bit=1 always passes; bit=0 passes
  w.p. 1/36) → ~1.8 expected wrong bits over 63 → AES-verified flip search (≤2 flips)
  closes the solve. So even a mod-4-only invariant (4/5 accuracy, ~12.6 errors) is NOT
  enough alone; need mod 36 (or mod 4 + mod 9 from separate sources).

## Files
- orbit.gp (FIXED E2[4],E2[5]), small3.gp/small3.out (p=1289 orbit dump, 18 rows x a4 a6)
  in scratch; hunt2.gp (small-prime finder: p=1289 h=36, p=4049 h=72, p=4241 h=108).
- tg2.py (real-instance character test), tg4.py/tg5.py (small-orbit homomorphism tests).
- cls6.gp/cls6.out: class logs of all 29 primes (WORKING, reusable). bnf.dat: bnfinit cache.

---

# SESSION UPDATE 2026-10-26 (leg A + parity breakthrough)

## LEG A (backdoor cross-instance leak) — CLOSED, no leak
- backdoor(priv) = ∏_i (secret_marks_i XOR priv_i); = 0 iff any coordinate equals the mark.
- max_exp = 3 (verified), so marks/hits live in [-3,3]; t = bd(A)·bd(B) = 0 w.p. ~0.9998.
- bit=0 ⇒ privC resampled until bd(privC) ≠ 0 ⇒ privC coordinate-avoids the fixed marks.
  Image of that sparse set under Σ v_i c_i mod 36 is still all of Z/36 (6^29 ≫ 36·7^29/h),
  so even mod-36 has NO bias for bit=0; j-level is uniform both ways. No observable signal
  without class computation. Confirms AAR; nothing else in transcripts deleg_53daaaa2/6e2c606a.

## PARITY EXTRACTOR FOUND: q4(Delta) = quartic character of the discriminant
- Testbed p=1289 (tg6/tg8): value q4(Delta) ∈ {479, 810} = ±i exactly, and
  q4(Delta)(x) = q4(Delta)(0)·(−1)^x over ALL 18 labeled rows. Perfect x mod 2 detector.
- jac(Delta) ≡ −1 for every orbit curve (both testbed and real E0), so q4(Delta) = ±q4(Delta_E0).
- Real p ≡ 1 mod 8 (verified) => quartic character exists in F_p. Real instances (tg10/tg11):
  r = q4(D_C)/(q4(D_A)·q4(D_B)) ∈ {+v0, −v0}, v0 = q4(Delta_E0), v0^2 = −1.
  r = +v0 ⇔ Δ odd ⇒ bit=0 CERTAIN (bit=1 ⇒ Δ ≡ 0 mod 36).
  r = −v0 ⇔ Δ even ⇒ candidate (36 forced zeros, 27 even positions, all 1-bits ⊆ those 27).
- SECRET space: 2^63 → 2^27; AES-first-block brute force over subsets (tg11) ~6 min, 8 procs.

## DEAD (new, with proofs/evidence)
- Mod-9 / mod-3 via cubic symbols: IMPOSSIBLE for this family. Evidence + argument:
  1) tg8 testbed: q3_{Fp2}(yS) ≡ 1 identically. Proof: Frob yS = −yS forces
     c3(yS) = c3(yS)^p = conj ⇒ c3 ∈ μ3 ∩ Fp = {1}.
  2) Structural kill: class action commutes with End(E) ⊃ O = Z[√−p] ∋ Frob = ±√−p.
     All O-linear level data E[l^k] (any l≠p) has Frob action = (±√−p mod l^k),
     class-independent up to the global sign, and ±M are GL2(Z/l^k)-conjugate
     (e.g. diag(4,5) ~ diag(5,4) mod 9). So E[l^k]/psi_l factorization/9-torsion
     eigenstructure over F_p carry ZERO mod-3/9 class info. (tg9 empirics consistent:
     scalar Frob eigenvalue u does not exist; Frob is the O-element s, not a scalar.)
  3) The apparent "order-9 x-coords in F_p" (2 per row) is an artifact of a broken
     psi-recurrence eval (psi_odd is y-free; my recurrence was wrong) — retracted.
- q8(Delta) carries NO mod-4 info (testbed: 2 values within each x mod 4 class).
- p′≡1 mod 3 testbed (hunt3.gp) unnecessary: the kill in (2) is p-independent.

## STATUS: parity-only bit test gives 2^27 SECRET candidates → tg11 brute force.
## Files (new): tg8.py (char battery incl 9-div), tg9.py (Frob-on-E[9] via Fp6), tg10.py,
## tg11.py (parallel AES search over 27 candidate positions).

---

# SESSION UPDATE 2026-10-26 (tg11 found=0 diagnosed: tg11 had an AES-CBC bug)

## ROOT CAUSE of found=0: tg11 scan() omitted the IV XOR on the prefix filter
- CBC: first plaintext block P0 = AES_ECB_Dec(C0) XOR IV. tg11 compared raw ECB_Dec(C0)[:7]
  to b"crypto{' — never true for the real secret (P0^IV vs P0 mismatch) → whole 2^27
  search blind. Key derivation itself (SHA256(int.to_bytes(secret,8)) full 32B, AES-256-CBC)
  was verified CORRECT against source.sage line by line:
  key = SHA256.new(int.to_bytes(secret,8)).digest()[:128] → full digest (32 B). iv/ct from output.
- Bit layout verified: ZZ(SECRET).bits() is LSB-first, output.txt has exactly 63 instances
  → bit_length(SECRET)=63 → bit 62 = 1 FORCED. tg11's index j = bit j mapping was correct.

## tg12.py: fixed scan (ECB_Dec(C0) XOR IV prefix test), bit-62=1 constraint → 2^26 space,
  built-in synthetic self-test (3/3 planted secrets recovered through the identical
  key-derivation + CBC + padding pipeline) — PASSED before touching real data.

---

# SOLVED 2026-10-26

- Flag: [flag — recorded in FLAGS/isogenies/challenge-222-cryptohack-true_genus/flag.txt]  (submitted, score_delta +175, ok:true)
- SECRET = 6058240009948404437 (0x54133130ed089ad5); its 27 one-bits are EXACTLY the 27
  q4(Δ)-candidate positions — the parity extractor fired on all 63 bits with zero errors,
  and every even-Δ instance was a real 1-bit (no bit-0 false positives this instance set).
- Lesson for AAR future lives: when an exhaustive-key search returns found=0, audit the
  cipher filter end-to-end on synthetic planted data FIRST; here one missing IV XOR
  invalidated a 2^27 run. CBC first-block filter MUST be ECB_Dec(C0) XOR IV.
- Files: tg12.py (final solver, self-testable via --selftest), tg12.out, flag_true_genus.txt.

## Vulnerability (plain words)

A CSIDH-style class-group action on the j=0 orbit over F_p (p ≈ 2^155,
Cl(−4p) ≅ Z/36q), carrying a planted backdoor: backdoor(priv) XORs the signer's
exponent marks against a private vector, and with probability ~0.99 tells the
verifier that a "bit 0" instance used a resampled key avoiding those marks. The
run did NOT crack the class-group DLP (that route was killed with evidence, listed
below). The actual break is a genus-theoretic parity invariant: the quartic
residue character of the curve discriminant is a cheap, explicit character of the
class-group action that reads the parity of the action exponent — Gauss genus
theory (discriminant characters detect the 2-part of a class group), which the
flag name spells out. Combined with the source's own bit semantics, parity pins
each of the 63 SECRET bits down to a 2^26 candidate set, brute-forceable directly
through the AES check.

## How the answer follows

- Invariant: Jac(Delta) ≡ −1 on every orbit curve, so q4(Delta) ∈ {+v0, −v0} with
  v0 = q4(Delta_E0), v0² = −1; on the fully-labeled p = 1289 testbed (orbit.gp:
  18 j-rows with known class exponents x) q4(Delta)(x) = q4(Delta)(0)·(−1)^x holds
  for ALL rows — an exact x-mod-2 detector. Real p ≡ 1 mod 8, so the quartic
  character exists in F_p.
- Per instance compute r = q4(Delta_C) / (q4(Delta_A)·q4(Delta_B)):
  r = +v0 ⇒ Delta odd ⇒ bit = 0 certain (bit = 1 forces Delta ≡ 0 mod 36);
  r = −v0 ⇒ Delta even ⇒ candidate 1-bit position. Output has 63 instances ⇒
  bit 62 = 1 forced ⇒ SECRET space 2^63 → 2^26.
- AES filter: key = SHA256(int.to_bytes(secret,8)) (full digest), AES-256-CBC,
  test prefix ECB_Dec(C0) XOR IV == "crypto{" (the IV XOR is mandatory — the
  earlier blind run proved it). tg12.py self-tested 3/3 on planted secrets, then
  real run: the 27 candidate positions were exactly the SECRET's 1-bits
  (SECRET = 6058240009948404437) →
  [flag — recorded in FLAGS/isogenies/challenge-222-cryptohack-true_genus/flag.txt], server +175.

## Limitations / attempts that failed

- Character batteries (jac/quadratic/quartic/cubic of a4, a6, Delta, j−1728 over
  F_p and F_{p²}): uniform on the real instances; on the labeled testbed NO cheap
  invariant satisfied val(x) = g^x except the parity-level q4(Delta).
- Mod-3/9 extraction was proved structurally impossible for this family: the
  class action commutes with End(E) ⊇ Z[sqrt(−p)] ∋ Frob = ±sqrt(−p), so Frob on
  E[ℓ^k] (ℓ ≠ p) is class-independent up to GL2-conjugacy — cubic symbols and
  9-torsion eigenstructure carry no class info (testbed evidence + argument; one
  apparent positive was a broken psi-recurrence and was retracted).
- Mod-36 via smooth-ideal walks: minimum smooth ideal degree ≈ 2^65 (lattice
  determinant estimate) — infeasible; Pollard rho in the q-part: 2^37 class ops —
  infeasible; MITM on the 7^29 key space: 2^81 — infeasible.
- tg11's 2^27 search returned found=0 from a missing IV XOR in the CBC filter —
  a glue bug, not the math.
- An earlier session parked this as UNSOLVED after 3 solver deaths; a later
  session re-opened and solved it — the AAR's earlier status lines are historical
  record, the final section is the outcome.

## Sources

- PARI/GP bnfinit (bnf.dat cache; cls6.gp class logs of all 29 primes) for class
  group structure.
- Quartic residue symbols / genus theory: textbook-level number theory
  (knowledge retrieval stated plainly); the specific invariant was searched for
  and verified in-run on the labeled p = 1289 testbed.
- No third-party writeups or solution pages consulted (run log).
