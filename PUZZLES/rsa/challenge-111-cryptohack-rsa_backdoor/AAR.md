# AAR — 111-cryptohack-rsa_backdoor: RSA Backdoor Viability (CryptoHack)

**Result:** SOLVED (account NoBirdWasHam; 2026-10-23) — score_delta +175, verified `ok:true`
**Flag:** `[flag — recorded in FLAGS/rsa/challenge-111-cryptohack-rsa_backdoor/flag.txt]`

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "RSA Backdoor Viability" (175 pts, slug `rsa_backdoor`), contributed by joachim
- **NOT consulted:** `/challenges/rsa_backdoor/solutions/`, third-party writeups (no-cheat rule)
- Theory reference: Cox, *Primes of the form x²+ny²* (class field / genus theory facts); Atkin–Morain style CM factoring.

## The vulnerability
`p = (427·s²+1)/4` ⇒ **4p−1 = 427·s² is 427 times a square** (the flag pun confirms this is
the intended backdoor). Equivalently p is represented by the **principal form** x²+xy+107y²
of discriminant −427 (h(−427)=2), so p **splits completely in the ring class field** of
Q(√−427). Consequences used:
1. The Hilbert class polynomial H₋₄₂₇(x) = x² + HB·x + HC splits mod p; its roots j are
   CM j-invariants of curves with **#E(F_p) = p+1−t, t = ±1** (Frobenius π = (1+s√−427)/2,
   π+π̄ = 1; both class-group components share the same t since the two CM curves are
   3-isogenous over F_p — 3 is the inert prime carrying the nontrivial class).
2. When t = +1, #E(F_p) = p divides n = pq, so **[n]P = O mod p** for every P ∈ E(F_p) —
   an Atkin–Morain factoring oracle.

## The attack (solve script: `cm_formal.py`)
Work in **R = (Z/n)[δ]/(δ² − DD)**, DD = HB²−4HC = disc(H), with x := (δ−HB)/2 (a root of H).
- R/pR ≅ F_p×F_p (H splits mod p); R/qR ≅ F_{q²} (H is irreducible mod q here because
  (−7/q) = −1 — see below), so R ≅ F_p×F_p×F_{q²}: gcd(N_{R/Z/n}(u), n) splits n whenever
  u vanishes on a p-component only.
- Curve over R: E: y² = x³ + Ax + B with A = 3x/(1728−x), B = 2x/(1728−x) (j = x).
- **No square roots needed:** pick x0 ∈ R and adjoin y formally: S = R[Y]/(Y²−g(x0)).
  P = (x0, Y) ∈ E(S) is automatically on the curve. (Square roots mod composite n are the
  whole problem — a formal-Y étale algebra sidesteps them entirely.)
- Binary ladder for [n]P over S. When the p-components of the running point hit O, some
  denominator has norm ≡ 0 mod p (and ≠ 0 mod q, since #E(F_{q²}) = q²+1−t″ ∤ n), and
  gcd(norm, n) = **p**.
- If t = −1 (#E(F_p) = p+2 ∤ n): twist E^d: y² = x³ + d²Ax + d³B for random d ∈ R; the
  trace flips on a p-component iff d's component is a nonsquare ⇒ P(both flip) = 1/4 per
  trial; loop trials until the ladder throws a bad denominator.
- Then q = n/p, d = e⁻¹ mod (p−1)(q−1), m = c^d mod n.

Key numbers: n 4096 bits; p 2049 bits (verified prime, 4p−1 = 427·s², s 1021 bits);
q 2048 bits. Real-instance run: 573 s (trial with the right twist hit early).
Self-test (`python3 cm_formal.py self`): 4/4 small instances (p of the same shape, q 160-bit).
Trace check on a small instance via PARI `ellap`: t = −1 at both H-roots mod p, and +1 after
twisting by a nonsquare — confirming the twist loop is load-bearing.

## Learning points
- p=(D·s²+1)/4 ⇒ p principal of disc −D ⇒ CM curve with trace ±1 ⇒ factor via [n]P over
  an étale algebra when #E(F_p) | n. The "recursion limit" hint is a red herring for this
  route.
- **Formal-Y trick:** to get a point on a curve over Z/n without sqrt mod n, adjoin Y with
  Y² := g(x0) as a formal quadratic extension; the group law never needs Y to exist in Z/n.
- Jacobi bookkeeping pins the splitting behavior: (−7/n) = −1 with (−7/p) = +1 forced
  (−7/q) = −1 ⇒ H irreducible mod q ⇒ no integer-j curve over Z/n exists — the rank-2
  algebra R is mandatory. (−427/q) = +1 ⇒ #E(F_{q²}) ∤ n, keeping the q-component alive.
- Trace t = ±1 is a coin flip; random R-twists (1/4 hit) cover t = −1.
- Composite-n exponent traps cost hours: a QR mod p AND mod q does NOT satisfy
  a^((n−1)/2) ≡ 1 mod n, and a^((n+1)/4) is not a sqrt mod composite n even for
  guaranteed squares a = k² (verified empirically, 0/20).

## Limitations / failed attempts (evidence)
- `gcd(α^((n−1)/2)−1, n)` battery for α ∈ {−7, 61, −427} (probe2.py/solve.py): gcd = 1.
  Reason: w_p^q ≠ w_p; α^((n−1)/2) mod p = (α/p)·α^((q−1)/2), not 1.
- Integer-root-of-H curve over Z/n (solve2.py): disc(H) is not a QR mod n because
  (−7/q) = −1 ⇒ H irreducible mod q. Dead end for this instance.
- Square root in R via y = g·x/N(g) (old solve.py/cm_attack.py): y² = g²/N ≠ g — broken;
  also sqrt in R ≡ factoring. cm_attack.py additionally used j = δ instead of j = (δ−HB)/2.
- Plain Coppersmith on 427qs²+q = 4n and univariate 427s²+1 mod p (bound N^{β²/δ} = N^{1/8}
  ≪ s ~ N^{0.25}): no slack (pre-established, not re-derived).
- Fermat/p−1/ECM, naive Frobenius gcd batteries (probe1.py): hopeless at these sizes
  (pre-established).

## Artifacts
- `cm_formal.py` — the solve (modes: `self`, `real`); `flag_rsa_backdoor.txt` — flag.
- Dead ends kept for the record: `solve.py`, `solve2.py`, `solve_cm.py`, `cm_attack.py`,
  `cm_fast.py`, `cm_R.py`, `probe1.py`, `probe2.py`, `selftest.py`.

## Configuration (environment for this run)
- **Host OS:** Windows 11 (11), shell = git-bash/MSYS
- **User:** OWNER
- **Interpreter:** plain `python3` (sympy, gmpy2, PyCryptodome); PARI/GP `~\tools\gp64.exe` (2.17.4) used only for trace verification
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-111-cryptohack-rsa_backdoor`
- **Agent:** Hermes Agent (desktop); submission via `submit_flag.py <slug> <flag>` (cookie + requests, reports score delta)

## Vulnerability (plain words)
The prime was generated as `p = (427·s²+1)/4`, so `4p−1 = 427·s²` — 427 times a square. That special shape makes p a prime represented by the principal form x²+xy+107y² of discriminant −427, which forces p to split completely in the ring class field of Q(√−427). Concretely: the CM curves whose j-invariants are the roots of the Hilbert class polynomial H₋₄₂₇ have #E(F_p) ∈ {p, p+2} (trace ±1). When the trace is +1, #E(F_p) = p divides n = pq, so one scalar multiplication [n]P degenerates modulo p but not modulo q — an elliptic-curve factoring oracle for n (Atkin–Morain style). Factoring n ⇒ plain RSA decrypt ⇒ flag.

## How the answer follows
1. Set up R = (Z/n)[δ]/(δ² − DD) with DD = HB²−4HC = disc of H₋₄₂₇(x) = x²+HB·x+HC, and let x := (δ−HB)/2 be a formal root of H. R ≅ F_p×F_p×F_{q²}: H splits mod p (p splits completely) and is irreducible mod q (forced by (−7/q) = −1).
2. Curve over R: E: y² = x³+Ax+B with A = 3x/(1728−x), B = 2x/(1728−x) (j = x). Point without square roots mod n: adjoin Y formally, S = R[Y]/(Y²−g(x0)), P = (x0, Y) — the group law never needs Y in Z/n.
3. Binary ladder [n]P over S. When the p-components hit O (case #E(F_p) = p | n), some denominator has norm ≡ 0 mod p and ≠ 0 mod q (since #E(F_{q²}) = q²+1−t″ ∤ n), so gcd(norm, n) = p.
4. If trace came out −1, twist E^d: y² = x³+d²Ax+d³B with random d ∈ R; each p-component flips iff d's component is a nonsquare ⇒ P(hit) = 1/4 per trial; loop until the ladder throws a bad denominator. (Trace check on a small instance via PARI `ellap` confirmed t = −1 at both roots, +1 after nonsquare twist — the twist loop is load-bearing.)
5. q = n/p, d = e⁻¹ mod (p−1)(q−1), m = c^d mod n → flag `[flag — recorded in FLAGS/rsa/challenge-111-cryptohack-rsa_backdoor/flag.txt]`.
Key numbers: n 4096 bits; p 2049 bits, verified prime with 4p−1 = 427·s², s 1021 bits; q 2048 bits; real run 573 s; self-test 4/4 on same-shape small instances.

## Limitations / attempts that failed
All previously logged dead ends remain in "Limitations / failed attempts (evidence)" above; summary of what failed: gcd(α^((n−1)/2)−1, n) battery for α ∈ {−7, 61, −427} returned gcd = 1 (wrong exponent identity for mixed Legendre symbols); integer-j curve over Z/n impossible (disc(H) non-QR mod n since H irreducible mod q); explicit sqrt in R was algebraically broken (y² = g²/N ≠ g) and sqrt in R ≡ factoring anyway; plain Coppersmith on 427qs²+q = 4n has no slack (bound N^{1/8} ≪ s ~ N^{0.25}); Fermat/p−1/ECM hopeless at these sizes. Composite-n exponent traps verified empirically (0/20 for a^((n+1)/4) as sqrt of k²).

## Sources
Provided challenge files; theory references named in the original AAR: Cox, *Primes of the form x²+ny²* (class-field/genus-theory facts), Atkin–Morain-style CM factoring. PARI/GP `ellap` used only for trace verification. `/challenges/rsa_backdoor/solutions/` and third-party writeups NOT consulted (no-cheat rule).
