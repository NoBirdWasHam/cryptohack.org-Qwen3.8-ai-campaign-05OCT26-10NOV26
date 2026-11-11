# AAR — do_you_have_good_eyes-breizh (Breizh CTF / CryptoHack archive, port 43607)

## What the challenge is
Interactive MLWE *distinguisher* game. 130 rounds, 128 correct needed for the flag.
Each round the server sends A (8×7 matrix over R_q = F_q[x]/(x^256−1), q = 8380417,
Dilithium-5 parameters) and a vector t (8 polys), base64+gzip-sanitized.
t = A·s + e with s ← [−2,2]^{7×256}, e ← [−2,2]^{8×256} (bit=1) or t uniform (bit=0).
We must answer "MLWE (1) or not (0)?" — i.e. actually distinguish MLWE from random.

## The vulnerability (plain words)
The parameters are "real" Dilithium-5, but the challenge is a *ring with zero-divisors
that splits completely*: q−1 = 2^13·3·11·31, so x^256−1 has all 256 roots in F_q, and
in particular x−1 | x^256−1. Evaluation at x=1 is then a ring homomorphism
φ: R_q → F_q, φ(p) = Σ_k p_k (sum of coefficients). Homomorphisms are supposed to
preserve nothing useful to the attacker — but here the secret and error have
SMALL INTEGER coefficients, and φ turns the ring equation
    t = A·s + e   into  8 scalar equations over F_q:
    T_m := t_m(1) = Σ_j A1_{mj}·σ_j + μ_m (mod q),  A1_{mj} = A_{mj}(1),
where σ_j = s_j(1) = Σ_k s_j[k] and μ_m = e_m(1) are still small INTEGERS
(|σ|,|μ| ≤ 512 — sum of 256 values in [−2,2]). For a uniform t the same equations
exist only if some small box point (σ,μ) satisfies them: with 15 unknowns in a
box of 1025 and 8 equations mod q, expected number of false solutions
≈ 1025^15 / q^8 ≈ e^−24 ≈ 4e−11. So: MLWE ⇒ tiny CVP instance has a solution;
uniform ⇒ essentially never. One shot per round, error ~1e−10 both directions.

## Attack (what we compute per round)
Kannan embedding, dimension 16:
  lattice rows: (e_j | A1_·j | 0) j=0..6; (0 | q·e_m | 0) m=0..7; (0 | T | κ), κ=500.
If MLWE, the lattice contains (σ, −μ, −κ) with ‖(σ,μ)‖ ≤ 512·√15 ≈ 1985 (typ. ≈ 80),
while the lattice's own minimum is ~√(15/2πe)·q^{8/15} ≈ 4.6e3 (det q^8): unique
short vector, gap ≈ 50× — LLL (fpylll) finds it instantly. Decide MLWE iff the LLL
basis has a row with |last| = κ and ‖first 15 coords‖ ≤ 2200.
Cost per round: one 16×16 LLL — microseconds. 130 rounds trivial.

## Key numbers
- q = 8380417; boxes ±512; Kannan dim 16; accept radius 2200; κ = 500.
- Self-test: 3/3 synthetic MLWE + 5/5 synthetic random correct.
- Saved real instances (live_instances.json, 10, labels known from prior-session
  wp/oups feedback): 10/10 correct.
- FP bound uniform→MLWE: ≈ 1025^15/q^8 ≈ 4e−11 per round (ball-packing form:
  vol B_15(2200)/q^8 ≈ 2e−5 worst-case loose bound, still ≈ 0 over 65 random rounds).
- FN MLWE→uniform: solution vector always exists and is unique-short (gap ~50×);
  none observed on 10 real + 3 synthetic.

## Derivation trail / dead ends (honest)
1. First hypothesis "t lies in a small module lattice, per-NTT-coordinate CVP":
   WRONG because I conflated NTT coordinates with complex roots — F_q evaluations
   ζ^i mod q are big residues; NTT values of small polynomials are NOT small
   (measured: ‖ŝ‖ ~ 7.7e6). Caught by fuzzing my own generator (loop-guarded).
2. "Consistency of [Â|t̂] per NTT coordinate": WRONG — ê absorbs the residual,
   8 eqs/7 unknowns+8 error is trivially consistent. Caught before wasting time.
3. Per-coordinate CVP on {(y, Ây+qz)}⊂Z^15: lattice has det q^8 and gap ~50 —
   actually equivalent to what worked but applied to the wrong smallness claim;
   failed empirically (babai dist ≈ 6000 for true MLWE).
4. Working version: projection to x=1 (or any divisor x^d−1 | x^256−1, d≥1;
   d=1 minimal) — the only place integer smallness survives.
5. Host glue bugs found by primitive fuzzing (per brief): NTT bit-reversal
   direction (Horner ground truth caught it), fpylll build lacks Babai (wrote
   nearest-plane with exact Fractions), double-subtracted κ² in Kannan distance
   check (d²=‖v[:-1]‖² directly).

## Verification
- Homomorphism identity T ≡ A1·σ + μ (mod q) verified exactly on synthetic instances.
- Distinguisher: 8/8 synthetic, 10/10 real labeled instances (see above).
- Live game: 128/128 correct, 0 "oups", flag received after 128 rounds
  (game_out.txt, game_log.json): BZHCTF{trop_de_structure_tue_la_structure_...}
  — author's own joke "too much structure kills the structure" confirms the
  structural (homomorphism) attack is the intended solve.
- Flag submitted: ok:true, solved count 296→297 (archive = 0 pts by design).

## Limitations
- The x=1 projection kills all ring structure; on real Dilithium the secret is not
  recoverable this way only because the real e is binomial and s1,s2 ranges are
  larger... (NOT the true reason: for THIS instance type, both s and e have the
  same tiny box, which makes the projected problem massively overdetermined.
  For FIPS-204 Dilithium, η=2/η2=32 boxes make σ,μ up to 512·(16)… projected
  box q-ratio no longer tiny; the break is specific to e being as small as s.)
  Did not test against a hardened variant.
- Single homomorphism (x=1) used; other divisors x^d−1 (d|256) give more
  independent equations (d=2 doubles equations; box halves per coefficient) —
  unused margin.

## Transferable lesson
- A split ring (x^n−1 | everything) is a source of homomorphic leaks: ALWAYS test
  the trivial evaluation map x→1 first when secrets have small integer coefficients;
  coefficient-sum collapse turns ring-LWE into 8 overdetermined linear equations.
- "Smallness" lives in the COEFFICIENT embedding, not in NTT coordinates.
- Banked as skill: cryptohack-ring-eval-distinguisher (references/ ring notes).

## Sources
- HPS textbook (hps2014.txt scratch) not needed beyond cyclotomic-ring basics.
- No writeups/solutions consulted (brief compliance).
