---
record: agent-aar
puzzle: challenge-70-cryptohack-unevaluated-tetctf2021
category: ctf-archive
url: https://cryptohack.org/challenges/unevaluated-tetctf2021/
status: solved
date: 2026-11-04
flag_ref: "FLAGS/ctf-archive/challenge-70-cryptohack-unevaluated-tetctf2021/flag.txt"
flag_sha256: 883833d8b7ce0b551914f58e2c34342c60f94c572cf13cdd4532a5433f5f83e4
skills: []
human_twin: AAR.md
---

# AGENT — unevaluated-tetctf2021 (TETCTF 2021, CryptoHack ctf-archive)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (derived from source, first principles)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. n is a perfect square → p = isqrt(n). Verified p*q*r == order, p≡11 mod 12 branch.
2. Group structure: (Z/p^2)[i]* ≅ μ_{p^2-1} × (1 + p·F_{p^2}). The p-Sylow
   {1+p·u} is additive F_{p^2}: (1+pu)(1+pv)=1+p(u+v), so the p-part DLP is a LINEAR
   equation: X = pk^(order/p) = 1+p·k·u_g  ⇒  k0 = k mod p = u_X·u_g^{-1} in F_p[i].
   DONE, verified (check True in solve1.py output).
3. T = pk·g^{-k0} = g^{p·c1}, c1 = (k-k0)/p < 2^256/p ≈ 2^128.6.
4. T^r = (g^{p r})^{c1}: both sides are Teichmüller lifts of F_p elements (im≡0 mod p),
   so the DLP reduces to F_p^*: base a = (g^{p r} mod p) real, target = T^r mod p real.
   This gives c1 mod q. One 128-bit prime-field DLP (safe prime p-1=2q) — subexponential
   NFS territory, generic (rho/BSGS ≈ 2^63.5) is infeasible.
5. After c1 mod q: c1 = (c1 mod q) + q·t with t ∈ {0..5} (c1max/q ≈ 5.45). Enumerate,
   k = k0 + p·c1, AES-ECB decrypt, keep plaintext matching flag/padding (solve_final.py).
   (The r-subgroup DLP is NOT needed — the 256-bit bound on k + q-part pins k.)

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: dlp_run2.sh, run_dlp.sh, solve1.py, solve_final.py, source.py, test_e2e.py
- data/logs: output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
1. n is a perfect square → p = isqrt(n). Verified p*q*r == order, p≡11 mod 12 branch.
2. Group structure: (Z/p^2)[i]* ≅ μ_{p^2-1} × (1 + p·F_{p^2}). The p-Sylow
   {1+p·u} is additive F_{p^2}: (1+pu)(1+pv)=1+p(u+v), so the p-part DLP is a LINEAR
   equation: X = pk^(order/p) = 1+p·k·u_g  ⇒  k0 = k mod p = u_X·u_g^{-1} in F_p[i].
   DONE, verified (check True in solve1.py output).
3. T = pk·g^{-k0} = g^{p·c1}, c1 = (k-k0)/p < 2^256/p ≈ 2^128.6.
4. T^r = (g^{p r})^{c1}: both sides are Teichmüller lifts of F_p elements (im≡0 mod p),
   so the DLP reduces to F_p^*: base a = (g^{p r} mod p) real, target = T^r mod p real.
   This gives c1 mod q. One 128-bit prime-field DLP (safe prime p-1=2q) — subexponential
   NFS territory, generic (rho/BSGS ≈ 2^63.5) is infeasible.
5. After c1 mod q: c1 = (c1 mod q) + q·t with t ∈ {0..5} (c1max/q ≈ 5.45). Enumerate,
   k = k0 + p·c1, AES-ECB decrypt, keep plaintext matching flag/padding (solve_final.py).
   (The r-subgroup DLP is NOT needed — the 256-bit bound on k + q-part pins k.)
