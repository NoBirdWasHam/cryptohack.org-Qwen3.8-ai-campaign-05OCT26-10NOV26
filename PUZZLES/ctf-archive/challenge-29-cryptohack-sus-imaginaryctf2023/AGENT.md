---
record: agent-aar
puzzle: challenge-13393-cryptohack-sus-imaginaryctf2023
category: CTF Archive
url: https://cryptohack.org/challenges/sus-imaginaryctf2023/
status: solved
date: 2026-11-08
flag_ref: "FLAGS/ctf-archive/challenge-29-cryptohack-sus-imaginaryctf2023/flag.txt"
flag_sha256: a75bd05d8f96186c1ce1facc3b28fa06b43312143abf04fd7e45c52a1b295966
skills: [coppersmith-vanishing-sanity, poly-ring-toolkit]
human_twin: AAR.md
---

# AGENT — sus (ImaginaryCTF 2023), CryptoHack archive #13393
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attacks tried (all failed, each attempted with real computation)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **General factoring of n** — PARI `factor()`/ECM backgrounded in a prior session; the
   small factor p is 512 bits (~1542 digits). ECM records are ~83–90 digits; NFS records
   ~830 digits. Infeasible by orders of magnitude. Documented, not re-grinded.
2. **Pollard p−1** on n (B₁=20000, lcm-exponent, gcd(2^M−1,n)) → gcd = 1. No smooth factor−1.
3. **Fermat with multipliers** k·n, k ≤ 60 (and analysis): the needed gap |k·pq − r| < ~2^768
   never occurs (gaps are ~2^1535); zero hits, consistent with analysis.
4. **Small-factor/structural probes**: trial division < 10^5, perfect-power, gcd(c,n)=1,
   squarefull checks (prior session) → nothing.
5. **Coppersmith univariate (mod unknown divisor)**: root bounds are far short:
   - `x²+x+1 ≡ 0 (mod q)`: q≈n^{1/3} ⇒ X < n^{1/18} = 2^{170}, need 2^{512}.
   - `x³+x²+x ≡ 0 (mod pq)`: pq≈n^{1/2}, δ=3 ⇒ X < n^{1/12} = 2^{255}, need 2^{512}.
6. **Howgrave-Graham bivariate lifting lattice**, two parameterizations:
   - f₁(x,y) = x·y·(x²+x+1) − n, root (p,r), X=2^{512}, Y=2^{1536};
   - f₂(u,v) = (u²+u+1)·v − n, root (p, rp), X=2^{512}, Y=2^{2050}.
   Built HG lattices (rows N^{m−k}x^a y^b f^k, k=1..3, box/triangle monomial regions,
   monomial rows N^m·x^a y^b), LLL via fpylll 0.6.4 (`LLL.reduction`).
   **Validation on a ratio-identical 357-bit toy** (60/120/180-bit p/q/r): across m ∈ {1,2,3}
   and ~50 region shapes, the shortest-vector evaluation bound never dropped below N^m
   (minUB pinned at exactly N^m — the trivial monomial row), and no short vector ever
   vanished at the true root (probe over 40 shortest rows/set). The (X,Y) region is outside
   the solvable region for these constructions — consistent with the Newton-polygon
   volume heuristic (X·Y³ = n^{1.67} vs bound ≈ n^{1.5} for f₁; f₂ marginal on the same scale).
   Scripts: `lat_toy.py`, `lat_toy2.py`, `lat_toy3.py`, `lat_grid.py`, `lat_v4.py`, `lat_probe.py`.
7. **Exponent/order constructions**: searched for a computable multiple of q−1 = p(p+1) or of
   p−1/p+1 via polynomials in n. Correct congruences: mod (p−1): n ≡ 3r; mod (p+1): n ≡ −r;
   mod (q−1): n ≡ pr and p³ ≡ p (mod q−1); mod (r−1): n ≡ pq. Every candidate exponent
   a^E ≡ 1 mod q needs (q−1) | E, i.e. both p and p+1 dividing a *computable* E, which stays
   circular (the known-congruence families n+r ≡ 0 mod (p+1) etc. involve the unknown r/p).
   No non-circular E exists in the examined family.
8. **Cube-root-of-unity route**: since q ≡ 1 (mod 3) and p ≢ 1 (mod 3), any x with
   x³ ≡ 1 (mod n), x ≢ 1, gives q = gcd(x²+x+1, n) — but constructing a nontrivial cube root
   of 1 mod n is provably equivalent to factoring; no shortcut from the Φ3 structure.
9. **e/λ degeneracy check**: gcd(e, λ)>1 only if 65537 | p+1 or r−1 — unverifiable without
   factors; probability ~4/65537, and even then decryption would still need a factor. Not
   pursued.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
1. **General factoring of n** — PARI `factor()`/ECM backgrounded in a prior session; the
   small factor p is 512 bits (~1542 digits). ECM records are ~83–90 digits; NFS records
   ~830 digits. Infeasible by orders of magnitude. Documented, not re-grinded.
2. **Pollard p−1** on n (B₁=20000, lcm-exponent, gcd(2^M−1,n)) → gcd = 1. No smooth factor−1.
3. **Fermat with multipliers** k·n, k ≤ 60 (and analysis): the needed gap |k·pq − r| < ~2^768
   never occurs (gaps are ~2^1535); zero hits, consistent with analysis.
4. **Small-factor/structural probes**: trial division < 10^5, perfect-power, gcd(c,n)=1,
   squarefull checks (prior session) → nothing.
5. **Coppersmith univariate (mod unknown divisor)**: root bounds are far short:
   - `x²+x+1 ≡ 0 (mod q)`: q≈n^{1/3} ⇒ X < n^{1/18} = 2^{170}, need 2^{512}.
   - `x³+x²+x ≡ 0 (mod pq)`: pq≈n^{1/2}, δ=3 ⇒ X < n^{1/12} = 2^{255}, need 2^{512}.
6. **Howgrave-Graham bivariate lifting lattice**, two parameterizations:
   - f₁(x,y) = x·y·(x²+x+1) − n, root (p,r), X=2^{512}, Y=2^{1536};
   - f₂(u,v) = (u²+u+1)·v − n, root (p, rp), X=2^{512}, Y=2^{2050}.
   Built HG lattices (rows N^{m−k}x^a y^b f^k, k=1..3, box/triangle monomial regions,
   monomial rows N^m·x^a y^b), LLL via fpylll 0.6.4 (`LLL.reduction`).
   **Validation on a ratio-identical 357-bit toy** (60/120/180-bit p/q/r): across m ∈ {1,2,3}
   and ~50 region shapes, the shortest-vector evaluation bound never dropped below N^m
   (minUB pinned at exactly N^m — the trivial monomial row), and no short vector ever
   vanished at the true root (probe over 40 shortest rows/set). The (X,Y) region is outside
   the solvable region for these constructions — consistent with the Newton-polygon
   volume heuristic (X·Y³ = n^{1.67} vs bound ≈ n^{1.5} for f₁; f₂ marginal on the same scale).
   Scripts: `lat_toy.py`, `lat_toy2.py`, `lat_toy3.py`, `lat_grid.py`, `lat_v4.py`, `lat_probe.py`.
7. **Exponent/order constructions**: searched for a computable multiple of q−1 = p(p+1) or of
   p−1/p+1 via polynomials in n. Correct congruences: mod (p−1): n ≡ 3r; mod (p+1): n ≡ −r;
   mod (q−1): n ≡ pr and p³ ≡ p (mod q−1); mod (r−1): n ≡ pq. Every candidate exponent
   a^E ≡ 1 mod q needs (q−1) | E, i.e. both p and p+1 dividing a *computable* E, which stays
   circular (the known-congruence families n+r ≡ 0 mod (p+1) etc. involve the unknown r/p).
   No non-circular E exists in the examined family.
8. **Cube-root-of-unity route**: since q ≡ 1 (mod 3) and p ≢ 1 (mod 3), any x with
   x³ ≡ 1 (mod n), x ≢ 1, gives q = gcd(x²+x+1, n) — but constructing a nontrivial cube root
   of 1 mod n is provably equivalent to factoring; no shortcut from the Φ3 structure.
9. **e/λ degeneracy check**: gcd(e, λ)>1 only if 65537 | p+1 or r−1 — unverifiable without
   factors; probability ~4/65537, and even then decryption would still need a factor. Not
   pursued.

## artifacts [OBSERVED]
- code: batt.gp, batt2.gp, diag_toy.py, gcd_check.py, jm_integer_port.py, js_small_roots.py, lat_grid.py, lat_probe.py, lat_toy.py, lat_toy2.py, lat_toy3.py, lat_v4.py, nval.gp, pfac.gp, probe1.py, probe2.py, run5_artifact_sweep.py, run5_pin_battery.py, scratch_run.py, solve_cyc.py, solve_toy.py, solve_toy2.py, solve_toy3.py, solve_toy4.py, solve_toy5.py
- data/logs: jm_margins.log, jm_real.log, jm_run2.log, output.txt, solve_cyc_rerun.log, toy4.log, toy5.log, toys_run4.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Washington, Introduction to Cyclotomic Fields, 2nd ed. (GTM 83, 1997) — p-adic L-functions,
  cyclotomic units, Galois action on class groups: depth for the residual r-boundary families.
  https://link.springer.com/book/10.1007/978-1-4612-1934-7
- Author errata (current): https://math.umd.edu/~lcw/cyclo.html
Status unchanged: parked, fresh-angle only; no sitting has consumed these sources yet.
