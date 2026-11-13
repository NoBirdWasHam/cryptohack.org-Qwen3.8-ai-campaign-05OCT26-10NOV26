---
record: agent-aar
puzzle: challenge-13402-cryptohack-kaitenzushi-hacktm_ctf2023
category: misc
url: https://cryptohack.org/challenges/kaitenzushi-hacktm_ctf2023/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/ctf-archive/challenge-13402-cryptohack-kaitenzushi-hacktm_ctf2023/flag.txt"
flag_sha256: 6b417ce5f896ec9d3225e1594884e04dc1751d534a0c902bf0d7463e495c30b3
skills: []
human_twin: AAR.md
---

# AGENT — kaitenzushi (HackTM CTF), CryptoHack ctf-archive
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vuln / attack (self-derived)" [OBSERVED text; evidence tag applies to its source, not each claim]
Rotation destroys each component but preserves quadratic structure, and the exact-integer relations plus constraint `Sx + e·Sy = 2n` let everything be rebuilt:

1. **Recover e.** |y'|² = y1²+y2² = Sy: printed y-components (~2^640, rel. error 2^-1337) give absolute error ≈ 2^-60 on Sy → Sy exact by rounding. |x'|² = Sx = x1²+x2² known within O(1) (observed 0.27), and exactly `Sx + e·Sy = 2n` ⇒ `e = (2n − Sx)/Sy` with error 2^199/Sy ≈ 2^-1081 ⇒ e exact by rounding. Check: 256-bit prime ✓.
2. **Recover θ.** Unrotating by angle t: E1(t)+E2(t)=2n for all t (identity), but E1(t)−E2(t) = A·cos2t + B·sin2t with A=(x1'²−x2'²)+e(y1'²−y2'²), B=2(x1'x2'+e·y1'y2') (identity x1²−x2² = e(y2²−y1²) kills the constant term). E1(θ)=n ⇒ `tan2θ = −A/B`. Relative error ~2^-1337 → θ good to ~2^-1200 rad.
3. **Undo rotation** with mpmath dps=500: x = R(t)ᵀx', y = R(t)ᵀy', round to integers. Verified exactly: x1²+e·y1² = n and x2²+e·y2² = n. Residual θ mod 90° ambiguity handled by trying the 4 rotations.
4. **Factor n from two representations** (ℤ[√−e] gcd trick): α1=x1+y1√−e, α2=x2+y2√−e both have norm n. α1·conj(α2) = M + N√−e with M=x1x2+e·y1y2, N=x2y1−x1y2, norm n²; the two prime factors land on the two coefficients, so **p = gcd(M, N)** (768-bit prime ✓, q = n/p).
5. **Decrypt**: m = c^d mod n, then flag = m ⊕ x1 ⊕ y1 ⊕ x2 ⊕ y2 (only the all-positive rotation branch XORs to ASCII).

## reusable-rules
- A shared rotation preserves dot/cross products and E1−E2 collapses to a pure cos2θ/sin2θ form whenever the two representations share n — "rotation-hint" challenges leak their own alignment angle.
- Precision budgeting: which aggregates are exactly recoverable depends on component magnitude ÷ value magnitude; Sy exact, Sx within O(1), and e still exact after division by Sy.
- Two representations by x²+ey² = two ideal-factor combinations of n ⇒ rational-integer gcd of the mixed-product coefficients factors n (no number-field library needed here).

## anti-patterns / limits
- Worst-case error bound on Sx (2^199) exceeded the "round to integer" requirement on paper; empirically the printed values reconstruct Sx within 0.27 (structured rounding). If that had failed, e could still be recovered by searching Sx within ±2^199 for e·Sy ≡ 2n — not needed.
- gcd(M,N) fallback (second gcd variant) coded but unused; first try gave p.
- No live service on this card; nothing fingerprinted. Flag provenance: entirely self-derived from chall.sage + output.txt; no solutions/writeups consulted.

## artifacts [OBSERVED]
- code: chall.sage, solve.py
- data/logs: flag_kaitenzushi-hacktm_ctf2023.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided files only: `chall.sage`, `output.txt`. Flag fully self-derived; no solutions/writeups consulted. No textbook cited in run logs (rotation invariance and the imaginary-quadratic gcd trick self-derived).
