# AAR — kaitenzushi (HackTM CTF), CryptoHack ctf-archive

**Solved: yes.** Flag recovered and submitted (site ok:true, solves 292→293; score_delta 0 = already credited).

## The setup
n = pq (768-bit primes), 256-bit prime e, and two representations
`x1²+e·y1² = x2²+e·y2² = n` with x_i ≤ 768 bits, y_i ≤ 640 bits.
Hint: both integer vectors x=(x1,x2), y=(y1,y2) rotated by the same unknown angle θ, printed as 1337-bit reals. Flag = RSA decryption of c XOR x1^y1^x2^y2.

## The vuln / attack (self-derived)
Rotation destroys each component but preserves quadratic structure, and the exact-integer relations plus constraint `Sx + e·Sy = 2n` let everything be rebuilt:

1. **Recover e.** |y'|² = y1²+y2² = Sy: printed y-components (~2^640, rel. error 2^-1337) give absolute error ≈ 2^-60 on Sy → Sy exact by rounding. |x'|² = Sx = x1²+x2² known within O(1) (observed 0.27), and exactly `Sx + e·Sy = 2n` ⇒ `e = (2n − Sx)/Sy` with error 2^199/Sy ≈ 2^-1081 ⇒ e exact by rounding. Check: 256-bit prime ✓.
2. **Recover θ.** Unrotating by angle t: E1(t)+E2(t)=2n for all t (identity), but E1(t)−E2(t) = A·cos2t + B·sin2t with A=(x1'²−x2'²)+e(y1'²−y2'²), B=2(x1'x2'+e·y1'y2') (identity x1²−x2² = e(y2²−y1²) kills the constant term). E1(θ)=n ⇒ `tan2θ = −A/B`. Relative error ~2^-1337 → θ good to ~2^-1200 rad.
3. **Undo rotation** with mpmath dps=500: x = R(t)ᵀx', y = R(t)ᵀy', round to integers. Verified exactly: x1²+e·y1² = n and x2²+e·y2² = n. Residual θ mod 90° ambiguity handled by trying the 4 rotations.
4. **Factor n from two representations** (ℤ[√−e] gcd trick): α1=x1+y1√−e, α2=x2+y2√−e both have norm n. α1·conj(α2) = M + N√−e with M=x1x2+e·y1y2, N=x2y1−x1y2, norm n²; the two prime factors land on the two coefficients, so **p = gcd(M, N)** (768-bit prime ✓, q = n/p).
5. **Decrypt**: m = c^d mod n, then flag = m ⊕ x1 ⊕ y1 ⊕ x2 ⊕ y2 (only the all-positive rotation branch XORs to ASCII).

## Key numbers
- e: 256-bit, prime, recovered by rounding — no search.
- θ from a single atan2; p found as gcd(x1x2+e·y1y2, x2y1−x1y2) on first try.
- All checks (E1, E2, isPrime p,q, p·q==n) passed exactly.

## Learning points
- A shared rotation preserves dot/cross products and E1−E2 collapses to a pure cos2θ/sin2θ form whenever the two representations share n — "rotation-hint" challenges leak their own alignment angle.
- Precision budgeting: which aggregates are exactly recoverable depends on component magnitude ÷ value magnitude; Sy exact, Sx within O(1), and e still exact after division by Sy.
- Two representations by x²+ey² = two ideal-factor combinations of n ⇒ rational-integer gcd of the mixed-product coefficients factors n (no number-field library needed here).

## Limitations
- Worst-case error bound on Sx (2^199) exceeded the "round to integer" requirement on paper; empirically the printed values reconstruct Sx within 0.27 (structured rounding). If that had failed, e could still be recovered by searching Sx within ±2^199 for e·Sy ≡ 2n — not needed.
- gcd(M,N) fallback (second gcd variant) coded but unused; first try gave p.
- No live service on this card; nothing fingerprinted. Flag provenance: entirely self-derived from chall.sage + output.txt; no solutions/writeups consulted.

## Files
- solve.py (runnable: `venv python solve.py` in this folder)
- statement.txt, chall.sage, output.txt, flag_kaitenzushi-hacktm_ctf2023.txt

## Vulnerability (plain words)
The challenge rotates the secret vectors (x1,x2) and (y1,y2) by one shared unknown angle θ and prints them as 1337-bit reals. A rotation scrambles individual coordinates but preserves all dot/cross structure, and the printed precision is so high that the key aggregate quantities recover exactly after rounding. The secret alignment angle — and e — leak themselves.

## How the answer follows
1. Sy = y1²+y2² exact by rounding (abs. error ≈ 2^-60); Sx within O(1) (0.27 observed); the public identity Sx + e·Sy = 2n then gives e = (2n − Sx)/Sy with error 2^-1081 ⇒ e exact (256-bit prime ✓).
2. Unrotating by trial t, E1(t)−E2(t) = A·cos2t + B·sin2t (identity x1²−x2² = e(y2²−y1²) kills the constant term), and E1(θ) = n forces tan2θ = −A/B ⇒ θ to ~2^-1200 rad via one atan2.
3. Undo the rotation (mpmath dps=500), round to integers; both exact relations x1²+e·y1² = x2²+e·y2² = n verify; θ mod 90° ambiguity covered by the 4 rotation branches.
4. Two representations of n by x²+e·y² = two ideal-factor splits in Z[√−e]: α1·conj(α2) = M + N√−e of norm n² ⇒ p = gcd(M, N) (768-bit prime ✓), q = n/p.
5. flag = (c^d mod n) ⊕ x1 ⊕ y1 ⊕ x2 ⊕ y2; only the all-positive branch XORs to ASCII ⇒ submitted, ok:true (solves 292→293).

## Limitations / attempts that failed
- Paper worst-case bound on Sx (2^199) exceeded the round-to-integer requirement in theory; it worked empirically (0.27 error). Fallback (search Sx in ±2^199 for e·Sy ≡ 2n) designed but never needed.
- Second gcd variant coded but unused (first try gave p). No live service on the card; nothing further failed — no other attempts recorded in run logs.

## Sources
Provided files only: `chall.sage`, `output.txt`. Flag fully self-derived; no solutions/writeups consulted. No textbook cited in run logs (rotation invariance and the imaginary-quadratic gcd trick self-derived).
