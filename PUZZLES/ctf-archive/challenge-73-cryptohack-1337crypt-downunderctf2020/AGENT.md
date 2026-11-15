---
record: agent-aar
puzzle: challenge-13396-cryptohack-1337crypt-downunderctf2020
category: CTF Archive
url: https://cryptohack.org/challenges/1337crypt-downunderctf2020/
status: solved
date: 2026-11-05
flag_ref: "FLAGS/ctf-archive/challenge-73-cryptohack-1337crypt-downunderctf2020/flag.txt"
flag_sha256: d5c08794aab776ca3b72faef8ccbe9cb9201c6c6c84cfab7b9e36ac51f874f47
skills: [bivariate-coppersmith-hint-factoring]
human_twin: AAR.md
---

# AGENT — 1337crypt (DownUnderCTF) — CryptoHack archive challenge-13396
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (derived here, first principles)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. hint gives s = sqrt(p)+sqrt(q) to within 1/D. Then
   S = p+q = (hint+delta)^2/D^2 - 2*sqrt(n), delta in [0,1)  =>  |S - S0| <= ~2^587.
2. Root separation amplification: dp = dS * (1 + S/|p-q|)/2. With |p-q| read off from
   d0 = isqrt(S0^2-4n), |p - p0| = |q - q0| =: bound B ~ 2^59x (computed exactly in solve.py).
3. Write p = p0+u, q = q0+v. Then
   f(u,v) = u*v + q0*u + p0*v + c0, c0 = p0*q0 - n,  vanishes EXACTLY at (u0,v0), hence mod n^m
   for any m. Bivariate Coppersmith (Howgrave–Graham): lattice = { n^{m-j} f^j * mono(deg<=D-2j) },
   rows scaled by X^a Y^b; every lattice polynomial h satisfies h(u0,v0) = 0 mod n^m, so the HG
   test ||h(Xu,Xv)||_2 < n^m/sqrt(w) forces h(u0,v0) = 0 over Z.
4. h(u0,v0)=0 + f(u0,v0)=0: resultant in v (f is linear in v) -> R(u) in Z[u] with root u0;
   gcd(R1,R2) factors to a linear factor giving u0; p = p0+u0 verified by p | n.
5. Decrypt: bit = 1 iff Legendre(c_i, p) = +1 (c_1 class = square; c_0 = x*square is non-residue
   mod p since x is). Reassemble bits -> bytes -> flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
(append runtime evidence below)

## artifacts [OBSERVED]
- code: 1337crypt.sage, dbg.py, dbg2.py, dbg3.py, dbg4.py, dbg5.py, dbg_mini.py, dbg_port.py, diag.gp, diag2.gp, red.gp, red2.gp, redB.gp, redK2.gp, redU.gp, scanC.py, scanE.py, scanX.py, scanX2.py, scanX3.py, selfcheck.py, selfcheck4.py, solve.py, solve2.py, solve3.py, solve4.py, solve4_part1.py, solve_coppersmith_port.py, solve_v1_old.py, test_mini.py, test_mini2.py, tiny.gp, tiny2.py, tiny3.py, xcheck.py
- data/logs: output.txt, real_port.log, run1.log, run2.log, selftest_full.log, solve_run.log, st_small.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Derived from challenge-provided materials (1337crypt.sage + output.txt) only; no author/organizer solution consulted — AAR states verbatim: "No author/organizer solution consulted; math derived from the provided .sage + output.txt only."
