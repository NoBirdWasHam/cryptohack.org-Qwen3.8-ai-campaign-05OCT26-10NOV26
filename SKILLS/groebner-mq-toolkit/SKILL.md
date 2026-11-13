---
name: groebner-mq-toolkit
description: Use for GF(2) polynomial-system CTFs via msolve, M4GB, SAT.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, groebner, mq, ctf]
    related_skills: [ctf-crypto-attacks, ring-eval-lwe-distinguisher]
---

# Groebner / MQ solving toolkit (measured on this host)

## When to Use
A challenge reduces to solving polynomial equations over GF(2) (or small fields): cipher ANFs, hash preimage
systems, 'multivariate' schemes, membership systems.

## Tool ladder (2026-11-02 host measurements, ~/tools/arsenal/MQ_ARSENAL.md)
1. msolve (github.com/msolve/msolve) — F4-style GF(2) Groebner; on this box dies at ~512 vars for dense
   quad systems (measured wall).
2. M4GB (Makarim–Stevens ISSAC 2017; github.com/cr-marcstevens/m4gb) — F4 on bit-sliced matrices.
   The public build has NO m4ri/m4rie dependency (bitslicing internal; see build recipe below) — and
   that internal backend is the RAM-hemorrhaging one at 300+ vars.
3. SAT route for dense-quadratic GF(2): Tseitin/xor-chain CNF -> pycryptosat (native XOR clauses; the
   winning class here — plain CDCL like kissat stalls on xor chains, measured ~2-4k conflicts/s UNKNOWN).
   ALWAYS encode-verify: known-solution instance must satisfy 100% of clauses before solving for real.
4. Macaulay linearization at degree 2 is memory-honest but saturates (rank <= n on random quads); measured
   512v/1024eq = 8.03 GB, 1024v = 64 GB -> pre-abort with a cap-enforced estimator before allocation.
5. GPU F4 (F4MG) needs NVIDIA CUDA — this host is AMD: NOT possible (finding, not failure).

## Hygiene (hard-won)
- Negative results must be config-validated: prove the solver CAN solve a same-shape toy instance first
  (empty-coset fiasco pattern — gp-kannan-msp-cvp has the sibling lesson).
- Test the witness BEFORE timing the engine, and gate the FULL loop, not just the input: plant a root,
  encode-verify the system, solve a SMALL same-shape planted instance, decode the output, semantically
  re-verify the recovered root. Input-only encode-verify hides broken OUTPUT parsers (measured: msolve
  0.11.0 GF(2) parametrization parsed into a non-root H for runs of blind engine-bound timing).
- A witness bit-convention relabel (e.g. bit-reversal) never changes system shape or engine cost; if
  an engine wall was measured on a verified system, re-timing under a relabeled witness cannot move it.
- Before escalating a RAM ladder (bigger caps, engine flags, owner RAM requests), spend ~30 min on
  REFORMULATION probes: linearizing substitutions (especially when the unknown is a FIELD element —
  see inversion-linearization below), eliminating existential aux variables over the coefficient
  ring, and constraint-density vs degree-of-regularity at higher density. Engines fail on SHAPE,
  not on RAM: a 40-GB-dead wide formulation is often a sub-second [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] under the
  right substitution (measured 5+ orders of magnitude).
- M4GB GF(2) at 320 dense quad vars is MEMORY-bound before time-bound: lcm-degree-3 selection grows
  past 3 GB within ~6 s (16-core build); msolve 512-var planted dense quads hits ~1.8 GB in <10 s.
- msolve 0.11.0 zero-dim GF(2) output: [0,[2,n,1,names,mults,[nreal,[uni,den,[coord...]]]]]; main var
  = names[n-1], uni term [c,[k,1]] gives its root w0=k; coord_i value = 1 XOR eval(coord_i, w0) where a
  term [c,[d...]] is c·theta^(sum d). ALWAYS re-verify by evaluating the input polynomials at the root.
- pycryptosat wheel quirks: get() budget exhaustion returns (None,None) = UNKNOWN not UNSAT; no 'mem' option;
  get_conflict() may return [] legitimately.

## Canonical references
[R26] msolve. https://github.com/msolve/msolve
[R27] Makarim–Stevens, M4GB, ISSAC 2017. https://marc-stevens.nl/research/papers/ISSAC17-MS-M4GB.pdf
[R28] M4GB source. https://github.com/cr-marcstevens/m4gb
Build fact (repo, 2026-11-02): M4GB compiles a SPECIALIZED solver per problem shape —
bin/solver_BACKEND_MAXVARS_FIELDSIZE with BACKEND in {m4gb, openf4, fgb}; set MAXVARS to your system's
variable count at compile time (GPL-3.0, C++11). Paper benchmark context: broke MQ-Challenge Type V up to
n=27/m=18 (10.9 days, 2 nodes) — calibrate expectations for dense quadratics accordingly.

Windows/msys64 build recipe (verified 2026-11-05, ~/tools/m4gb-src):
- autoreconf --install && ./configure; then make MAXVARS=<n> FIELDSIZE=2
  CXXFLAGS="-O3 -Wall -march=native -pthread -std=gnu++11" bin/solver_m4gb.exe
  (upstream bin/solver_m4gb rule fails under Windows — EXEEXT; gnu++17 default breaks
  contrib/runtime_stats.cpp on mingw byte vs std::byte).
- libtool emits a 30 KB stub + real binary in bin/.libs and drops -static: relink manually
  g++ -O3 -march=native -std=gnu++11 -static -o bin/solver_m4gb_n<n>_gf2.exe \
  src/bin_solver_m4gb-m4gb.o contrib/bin_solver_m4gb-runtime_stats.o -pthread.
- Public repo has NO m4ri/m4rie dependency (bitslicing internal) — pacman m4ri/m4rie unneeded.
- FIELDSIZE=2 auto-adds field equations x^2+x for ALL MAXVARS vars: solver requires
  nvars == MAXVARS exactly (extra phantom vars silently pollute the GB). Input: default format
  ($fieldsize 2 / $vars names / one poly per line, '*' or '^' fine); output = reduced GB, NOT roots.
- Measured GF(2) planted-MQ scaling (16 cores, -O3): first-update 3.4 s @320 vars, 11.8 s @416,
  30.1 s @512 (dense deg<=2 monomial index ~131k); run then enters lcm-degree-3 phase and had not
  closed at 90 s (320/416) / 180 s (512). Sub-ms only at 12 vars. A seconds-scale solve budget
  (e.g. per-connection alarm) is incompatible with GF(2) MQ at hundreds of vars on this engine.
  (2026-11-06 re-check: numbers reproduce within 2% on freshly regenerated planted systems; the
  320-var lcm-3 phase crosses 3.2 GB RSS at ~6 s — under a <2 GB host cap the 320-var run dies on
  MEMORY long before the alarm window closes.)
- `--nrthreads` (M4GB, default 16) and msolve `-t` are MEMORY knobs that move the WRONG way for
  conservation: threads PARTITION the matrices — fewer threads conserve cores, never RAM.
- M4GB Windows build (internal bitslicing, no m4rie): the lcm-3 dense phase is a MEMORY STEP
  FUNCTION, not a growth curve: measured 320-var GF(2), 0.9 GB through sparse U/M phases, then
  6.7 -> 14.6 -> 40+ GB within 36 s with NO plateau — exceeds a 64 GB home box regardless of
  thread count. Any smaller "it died at X GB" number is just a self-kill truncation; never price
  dense phases from guard-truncated samples. This build is NOT VIABLE >= 320 vars on workstation
  RAM; prefer msolve for 300+ var GF(2), and probe RAM headroom from the machine's free memory,
  not prior kill values.
- msolve option ladder for a memory-bound GF(2) system (measured 320-var planted): `-l 44/42`
  (probabilistic linearization) is DECLINED — "characteristic is too low" warning, silently falls
  back to -l 2. The memory-bounded block-Lanczos variants exist ONLY for large characteristic; on
  GF(2) there is NO bounded-RAM linear algebra in this engine. `-m <pairs>` (chunk pairs per
  matrix) DELAYS the memory step (37 GB @ 33 min vs 46 GB @ 10 min) but never bounds it — chunks
  accumulate across passes. `-q 1` (signature-based) is available; try it once before conceding a
  wall. Sanity math first: deg-3 rows x monomials at 0.01% density is still a tens-of-GB bitmap if
  lazy-dense ever wins — no flag rescues the wrong shape.

Existential aux vars in bilinear pencil systems -> KILL THEM FIRST, never carry into F4
(measured 2026-11-06, challenge-263 GCM membership): a system sum_p h_p * (known matrix) * f_j = Z
(bilinear in target h, existential aux f in a fixed subspace) looks like F4 territory (512 vars,
deg-3, 40-65 GB measured). Elimination over GF(2)[h] gives Fitting/minor conditions (degree-96 polys -
still dead), BUT if the pencil comes from FIELD MULTIPLICATION, the substitution y = h^{-1} is a
GF(2)-birational change of variables under which every membership condition Z in h^k*V becomes LINEAR
in y for k=1 (bits of Z*y), and linear via Frobenius for k=2 (y^2 = sum_j y_j * e_j^2, cross terms
die in char 2). Whole solve = [flag — recorded in FLAGS/post-quantum/challenge-168-cryptohack-lwe-intro/flag.txt] on 32N rows x 128 cols + one field inversion:
KB RAM, ms. Structural theorem: rank(T(h)|_V) = 96 for ALL h != 0 (field injectivity), so the
per-block 32 conditions are independent until the kernel saturates; kdim(N) = 96,64,32,1..3 and 4-6
random blocks isolate the planted root (24/24 seeds by N=6). Caveat-verified: near rank saturation
the stacked rows CAN be dependent (sum_c Z_c*mu_c = 0 with mu_c in the 32-bit complement), leaving
2^kdim-1 legitimate candidates - collect more pairs until kernel dim == 1, never trust a fixed N.
Lesson: before feeding any bilinear/pencil system to F4, ask whether the unknown is a FIELD element -
inversion-linearization beats F4 by 5+ orders of magnitude there. Also: enumerate kernels with the
pivot-BITS-only nullspace vector (v = e_jf XOR sum of (1<<pivot_col) where piv[i]_jf=1); XORing whole
RREF rows yields non-kernel garbage unless rows are self-orthogonal (silent 50%-per-node corruption).

Algorithm-family note (D10 residual): F5 (Faugere 2002) is the signature-based successor of F4 — available
via Magma/Sage (_groebner with F5) but NOT ported to this host; MSXL/XL linearization = the Macaulay-degree
case this skill already PRICED (rank-saturated on random quads). Before reaching for F5: measure the
linearization rank first — if it saturates, no Groebner refinement helps; go SAT (pycryptosat) instead.
