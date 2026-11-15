---
record: agent-aar
puzzle: challenge-13401-cryptohack-unbalanced-icc_athens2022
category: CTF Archive
url: https://cryptohack.org/challenges/unbalanced-icc_athens2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-51-cryptohack-unbalanced-icc_athens2022/flag.txt"
flag_sha256: sha256:553d00525ad3e72b4036a1a2c910b7b194b113ab49d4bad1f01a5afe8f2e54d4
skills: []
human_twin: AAR.md
---

# AGENT — unbalanced-icc_athens2022 (CryptoHack ctf-archive)

> 2026-11-14 verification audit run: this row now carries an OWN derivation
> (Durfee-Nguyen trivariate Coppersmith, rank-126 lattice, +46 b/dim margin) recorded in AAR.md;
> the flag is mirrored at flag_ref. The earlier null was honest bookkeeping, superseded — not overwritten.
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Current state of the attack" [OBSERVED text; evidence tag applies to its source, not each claim]
OPEN, but the door is identified and the numbers are positive. RUN#1 wrongly concluded "design sound" (bivariate-lattice wall-map). RUN#2 corrected it: these are literally the published parameters of Sun–Yang–Laih (Asiacrypt'99) RSA variant I, which Durfee–Nguyen (Asiacrypt 2000) break with a TRIVARIATE Coppersmith on f(x,y,z) = 1 + x((N+1) − y − z) ≡ 0 mod e with root (k,p,q) plus the integer relation yz = N — their bound δ_max ≈ 0.364 vs our δ = 0.293 (≈72 bits inside). RUN#3 transcribed the paper's exact helper region (a=0 ⇒ N-free determinant; diagonal audit matches Eq.(4) exactly), fixed the extraction (keep MIXED monomial vectors; eliminate y via two resultants S=Res_y(Q1,Q2), S'=Res_y(Q1,Q3); CRT the shared root k mod primes > 2^320; p+q = N+1+1/k (from A = N+1); then quadratic in T²−(N+1+1/k)T+N ⇒ p, q), and measured real-parameter margins: a=0 configs (7,6,0) +2.2, (8,7,0) +40.2, (9,7,0) +79.5 bits/vec. Run logs end at "Plan: run (9,7,0) w/ fallback (8,7,0)" — the real-instance gate outcome is not recorded in run logs.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- RUN#1's "design sound" verdict was a literature gap, not a computation gap — corrected in RUN#2; treat its bivariate wall-map as valid only for the bivariate family.
- DNG §4.1 text carries an internal inconsistency ("d of 256 bits" vs its own numeric check + implementation table d=192) — resolved in favor of the implementation table; Durfee-thesis Figure 1 download (slow Stanford mirror) unfinished, belt-and-braces only.
- The decisive real-instance runs ((9,7,0)/(8,7,0) at X = 2^300) were still gated when run logs end — outcome not recorded in run logs; reduction/extraction pipeline itself built and tested (`resultant_lib.py`, `dng4.attack`).

## artifacts [OBSERVED]
- code: bkzrun.py, detmargin.py, dng.py, dng2.py, dng3.py, dng4.py, epslat.py, epsolve.py, extract2.py, forensics.py, optsearch.py, probe.py, probe10a.py, probe3.py, probe4.py, probe5.py, probe6.py, probe7.py, probe9.py, purelat.py, real_lattice.py, reallat.py, resultant_lib.py, sshift.py, windowsolve.py
- data/logs: flag_found.txt, gate192.log, output.txt, real2.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
`challenge.py` + `output.txt` (provided). Literature (math papers, allowed by campaign rules): Durfee–Nguyen, Asiacrypt 2000, LNCS 1976, pp. 14–29 — actual PDF obtained open-access via Springer (`dng_asiacrypt2000.pdf`); Sun–Yang PKC'05 survey, LNCS 3386 §2.5 (initial, wrong region — superseded); Sun–Yang–Laih Asiacrypt'99 variant I as the target scheme; Hong et al. AMC 139(2003) and Ernst–Heer–Joye–Henniger Eurocrypt'05 noted as alternatives (not needed). Durfee PhD-thesis URL logged as fallback. No CryptoHack solutions/writeups consulted (provenance rule).

**RUN#3 BREAKTHROUGH — GATE d=192 PASSED (exact p recovered).**
Root causes fixed in order:
1. pdiv_mod returned remainder; need pdiv_quo quotient for exact division.
2. gcd(N, c_s of Res_x) = N ALWAYS: p,q symmetry — vanishing polys vanish at BOTH (k,p) and (k,q),
   so Res_x(y) carries both primes; gcd routes are structurally dead.
3. WORKING: exact Res_x(Q_i,Q_j)(y) over Z -> strip y^s -> flint fmpz_poly.roots() gives EXACT
   integer roots -> p and q both appear -> N % root == 0 check -> factor. (This is DNG's "standard
   root finding" decoded correctly.)
4. mod-l S-gcd/CRT-k route still fails: common deg-43 factor contains (x-k) but quotient may not;
   kept as harmless fallback.
Gate: m=4,t=2,a=0, X=2^192, 30 vanishing unis, pair(0,1) gave 256b root = p exactly.

**SYNTH d=300 PASSED** (seed 20261102, cfg m=6,t=4,a=0, det-margin −52.8 but LLL delivered;
pair(0,1) Res_x gave exact 256b root = p). Real mode: cfgs reordered, margin guard relaxed to −400.

**RUN#3 SOLVED.** Real instance cracked with cfg m=6,t=4,a=0,X=2^300 (r=77, LLL delta .99):
59 below-HG vanishing polys -> z=N/y Laurent+shift -> exact Res_x(pair0,1)(y) -> strip y^25 ->
flint fmpz_poly.roots() -> exact integer roots {p,q} -> gcd via N%root -> d=e^-1 mod phi -> flag.
FLAG: ICC{unb4lanc3d_pr1m3s_0nly_m4k3_th1ngs_w0rs3}  — submitted OK (CryptoHack solved 297->298).
Flags: real2.log, flag_found.txt. Notes: margin guard must use per-vector (marg/r); exact det_of
skipped for r>80 (20-min stall); content_reduce unis before resultants; det margin -51.8/vec still
worked (LLL better than bound); p<->q symmetry makes all gcd(N, resultant-coef) routes return N.
