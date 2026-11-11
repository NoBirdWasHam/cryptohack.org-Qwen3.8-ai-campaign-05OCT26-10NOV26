# AAR — quo_vadis (ECSC 2024 Italy, CryptoHack archive, slug quo_vadis-ecsc_2024_italy2024)

## Status
SOLVED and accepted 2026-10-29 (submit ok:true, solved-list +1 via reconcile.py).
Live run: all 5 challenges in 159 s (server timeout 600 s). Flag in
flag_quo_vadis-ecsc_2024_italy2024.txt (self-derived; no external sources consulted).
Earlier: full protocol also passed end-to-end against my own pure-Python replica
(`sim_server.py`) before touching the live listener.

## The vulnerability
Per challenge, the server builds two rings over Z/2^k:
- R1 = tower Z/2^k[b0]/(m0) ... successive quotients by lifted irreducibles (degrees ds),
- R2 = Z/2^k[b]/(g) in ONE step, deg g = prod(ds) = D,
Both are the Galois ring GR(2^k, D), hence CANONICALLY ISOMORPHIC over Z/2^k.
The oracle: server prints f(pt1) for a SECRET random {0,±1}-coeff poly f (1024 coeffs)
and returns f(pt2) for our chosen pt2 — but only after we "prove" we can compute in the
rings. Since f has integer coefficients, f commutes with the isomorphism psi: R1 -> R2:
send pt2 = psi(pt1); the reply is f(psi(pt1)) = psi(f(pt1)); pull back to get f(pt1).
Five challenges give all bytes of K = sha256 key -> AES-CBC flag decrypt.

## Attack construction (per challenge)
1. Parse printed sage GF-tower moduli strings (custom parser, incl. the flat compound
   constant-coefficient quirk, e.g. "b1^3 + b0bar + 1").
2. Find a root r of g mod 2 inside the GF(2^D) tower via Cantor-Zassenhaus with early
   exit (cz_one_root), using structure-constant bitmask arithmetic (byte tables) — the
   earlier 2^D full multiplication table was infeasible for D=30/60.
3. Hensel-lift r to theta in R1 with g(theta)=0 exactly (Newton, unit inverse via
   mod-2 inverse + Newton doubling).
4. M = matrix of theta^i flattened (Z/2^k-basis isomorphism psi^{-1} columns).
   x = M^{-1} pt1 (pivot mod 2 — M invertible since theta generates); send x.
5. Reply v = f(beta) in R2 basis -> f(pt1) = sum v_i * theta^i flattened. Accumulate K.

## Key numbers
D per challenge: 6, 6, 30, 60, 60; k = 2, 8, 8, 32, 64. Timings (local): 0.1/0.1/6.8/35.5/31.1 s.

## Files
quo_core.py (core algebra), solve.py (live client), sim_server.py (pure-Python server
replica + formatter used for verification), harness.py (unit tests, all pass).

## Limitations / failed paths (evidence)
- Tower.ensure_tab original design = 2^D x 2^D table: OOM-huge for D=30/60; replaced by
  structure constants + byte XOR tables (this was the prior session's stall; the earlier
  "Q(sqrt(D)) order/ideal/lattice" direction was NOT needed and was abandoned).
- parse_poly_str originally mis-assigned flat constant-coefficient terms (duplicate-deg
  AssertionError); fixed with zero-term grouping rule.
- No Sage on this host; protocol replica is my own Python server (same math, sage-style
  output strings), so parse-format coverage of the REAL sage prints is verified only
  against the sample lines captured from the live build (e.g. "b1^3 + (b0bar + 1)*b1 + 1").

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
