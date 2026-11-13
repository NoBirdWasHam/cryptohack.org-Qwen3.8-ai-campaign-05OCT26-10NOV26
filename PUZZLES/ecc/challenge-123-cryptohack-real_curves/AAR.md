# AAR — 123-cryptohack-real_curves: Real Curve Crypto (CryptoHack, 200 pts)

**Result:** SOLVED. Flag: `[flag — recorded in FLAGS/ecc/challenge-123-cryptohack-real_curves/flag.txt]` (API: ok:true, score_delta +200, solves 211→212).
**Date:** 2026-10-22

## Source
- **Platform:** CryptoHack (https://cryptohack.org/), ECC category, slug `real_curves`, contributed by jschnei
- **NOT consulted:** `/challenges/real_curves/solutions/`, /solves/, third-party writeups (no-cheat rule)

## The vulnerability
The "elliptic curve" is over **ℝ** (mpmath, dps=200), not a finite field: `y² = x³ − x`,
`P = N·G` with `N` = 128-bit AES key. The identity component of E(ℝ) is a **circle**
ℝ/ωℤ via the Weierstrass uniformization `x = ℘(u), y = −℘′(u)/2`, so the "DLP" is

    N·u_G − k·ω = u_P   (integers N < 2^128, k ≈ 0.4·N)

with ω the real period (= π/agm(1,√2) = 2.6220575542921198…; square period lattice, CM by i).
u_G and ω are computable to arbitrary precision (gx is an exact dyadic float); u_P is
recoverable from (px,py) to ~155–160 digits (the source's dps=200 double-and-add adds
error ≈ 2^127·10^-200 ≈ 10^-157 in u — measured empirically on a synthetic instance).
That precision surplus (≈155 digits ≫ 39 digits of secret) is the leak: the relation is
a **CVP with a huge gap**, not a hard DLP.

## The attack
1. Elliptic logarithms by quadrature: `u(x) = ∫_x^∞ dt/(2√(t³−t))` (substitution t=x+s²),
   **with sign fix from y**: `u = ω − u(x)` when y < 0 (branch bug that initially broke
   validation — cost the most time).
   u_G = 1.03919168245815745979…, u_P = 0.030828584465435926068… (both y>0 here).
2. Scale to integers at 2^700: U, W, V; Kannan-embedding lattice (rows)
   `[1,0,U,0], [0,1,−W,0], [0,0,V,c]`, c = 2^190. Plain exact-fraction LLL suffices
   (true vector ≈2^190 vs Gaussian-heuristic ≈2^233; expected spurious ≈2^-367).
3. Short vector with |4th coord| = c gives N = 106141468078803597872809305192151622442.
4. AES-128-CBC decrypt with key = N.to_bytes(16,'big') → `[flag — recorded in FLAGS/ecc/challenge-123-cryptohack-real_curves/flag.txt]`.

Pipeline was validated end-to-end on a synthetic instance (known 127-bit N, same
dps=200 source code) before touching the real data.

## Key numbers
- ω = π/agm(1,√2) ≈ 2.6220575542921198104648395898911194136827549514316
- α = u_G/ω ≈ 0.3963268009724177663150383880632120813174547237050967671250236380487735761802783571056616859153459869
- β = u_P/ω ≈ 0.0117574018979757894566902048177906496039076949865784925329100524690538743339452424070300277976229623
- N = 106141468078803597872809305192151622442 (127 bits)

## Learning points
- "DLP over ℝ" on an elliptic curve = inhomogeneous Diophantine approximation
  ‖N·α − β‖ < ε on the circle. It is hard only when ε ≲ 1/N; when the data precision
  ε⁻¹ exceeds ~N², Kannan embedding solves it. (My initial 2D-CVP hardness analysis was
  wrong because I fixed the wrong target window; correct scaling makes the true vector
  the unique closest one.)
- Always recover the **sign of y** when inverting ℘: u and ω−u are the two points sharing
  an x; a wrong branch silently destroys the lattice relation.
- Measure numerical error empirically (dps=200 vs dps=500 rerun) before trusting a
  precision-budget argument.
- PARI `elllog(E,[x,y])` errored ("too few arguments") on this build; quadrature +
  `pi/agm(1,sqrt(2))` for the period worked fine.

## Limitations
- Significant early effort went into a wrong hardness proof (concluding the instance was
  generic-hard); small-N brute force (N < 2·10^6) and the CF of α (no huge partial
  quotients) ruled out shortcuts before the lattice framing was fixed.
- The attack's success margin depends on the source's rounding error (~10^-157); with
  dps ≈ 120 instead of 200 the same lattice would fail (ε·2^P would exceed det^⅓).

## Files
- `solve.py` — full solve (elliptic log + LLL + AES decrypt), runnable.
- `flag_real_curves.txt` — the flag.
- `elog.py`, `prep.gp`, `ab.txt` — exploratory artifacts.

## Configuration (environment for this run)
- Windows 11, git-bash; python3 (mpmath, PyCryptodome); PARI/GP gp64.exe 2.17.4
- Submitted via `python3 submit_flag.py real_curves "<flag>"` from workspace root;
  correctness from API score delta (+200), not the submission HTML.

## Vulnerability (plain words)
The "elliptic curve" y² = x³ − x is evaluated over the **real numbers** (mpmath, dps=200), not a finite field. The identity component of E(ℝ) is topologically a circle: the map u ↦ (℘(u), −℘′(u)/2) wraps the real line around it with real period ω. Recovering the 128-bit AES key N from P = N·G is therefore the circle relation N·u_G − k·ω = u_P for unknown integers N and k — and because the server's printed coordinates retain ≈155–160 digits of precision while the secret is only ≈39 digits, this is an inhomogeneous Diophantine approximation with a huge gap, i.e. a lattice closest-vector problem, not a hard DLP.

## How the answer follows
1. Real period ω = π/agm(1,√2) ≈ 2.6220575542921198… (square period lattice, CM by i). Elliptic logarithm by quadrature u(x) = ∫_x^∞ dt/(2√(t³−t)), **with the y-sign branch fix** u → ω−u(x) when y < 0 (that branch bug cost the most time). Here u_G ≈ 1.0391916824…, u_P ≈ 0.0308285844… (both y > 0); ratios α = u_G/ω, β = u_P/ω recorded in "Key numbers".
2. Precision budget: the source's dps=200 double-and-add injects ≈2^127·10⁻²⁰⁰ ≈ 10⁻¹⁵⁷ of error into u_P (measured empirically, dps=200 vs 500 rerun on a synthetic instance) — 155+ clean digits ≫ the ~39 digits of secret, which is the leak.
3. Scale u-values by 2^700 to integers U, W, V and build the Kannan-embedding lattice rows [1,0,U,0], [0,1,−W,0], [0,0,V,c], c = 2^190. Plain exact-fraction LLL suffices: true vector ≈2^190 vs Gaussian-heuristic competitor ≈2^233, spurious ≈2⁻³⁶⁷.
4. The short vector with |4th coordinate| = c yields N = 106141468078803597872809305192151622442 (127 bits).
5. AES-128-CBC decrypt with key = N.to_bytes(16,'big') → `[flag — recorded in FLAGS/ecc/challenge-123-cryptohack-real_curves/flag.txt]` (API ok:true, +200). Pipeline was validated end-to-end on a synthetic instance (known 127-bit N, same dps=200 source) before touching real data.

## Limitations / attempts that failed
Carried from "Limitations" above: significant early effort went into a wrong hardness analysis (initial 2D-CVP argument concluded the instance was generic-hard — it fixed the wrong target window); small-N brute force (N < 2·10^6) and continued-fraction scan of α (no huge partial quotients) were run and ruled out shortcuts before the lattice framing was corrected. Success margin depends on the source's rounding error (~10⁻¹⁵⁷): at dps ≈ 120 the same lattice fails (ε·2^P exceeds det^⅓). Tooling: PARI `elllog(E,[x,y])` errored ("too few arguments") on this build — quadrature + `pi/agm` used instead.

## Sources
Provided challenge source; textbook theory (allowed class): Washington, *Elliptic Curves: Number Theory and Cryptography*, Ch. III (uniformization of E(ℝ), elliptic logarithm) and HPS *An Introduction to Mathematical Cryptography* §6.4–6.5 (lattices/CVP, Kannan embedding) — both cited in the original AAR. No `/solutions/`, `/solves/`, or third-party writeups consulted.

## References (allowed: textbook theory only)
- Washington, *Elliptic Curves: Number Theory and Cryptography*, Ch. III (uniformization
  of E(ℝ), elliptic logarithm); HPS *An Introduction to Mathematical Cryptography*
  §6.4–6.5 (lattices/CVP, Kannan embedding).
- No CryptoHack solutions/solves pages or third-party writeups consulted.
