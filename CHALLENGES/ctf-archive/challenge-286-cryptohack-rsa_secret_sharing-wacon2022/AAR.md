# AAR: rsa_secret_sharing-wacon2022 (challenge-286) — SOLVED (run 2)

## FINAL OUTCOME
Solved via listener with self-derived attack; flag WACon{...better RNG than
LCG...} submitted, CryptoHack solved-list 281 -> 282 (verified in submit
JSON). Live session: PoW 36 s, solve 249 s, 4/4 factorizations accepted.
Offline pre-validation: captured 342-bit instance solved in 93 s
(captured_factors.json), deterministic ground-truth fuzz dbg9 10/10,
real-prime mini-sim 3/3. NO Coppersmith needed.

## Attack (det-trick, no lattice)
a=x=b=1 -> stream1_j = j; n mod q = u*v exact -> roll indices;
R2_i = L2_u v + L2_v u (mod q) with L_j = C g^j + D -> triple-elimination
cofactors give sparse polys in g, gcd + roots over F_q (X^q-X intersect via
fast powmod + square-free CZ) + linear (C,D) solve; then
(n-low)/q^2 mod q = L3_u v + L3_v u (coefficients are STREAM-1 values, NOT
L2) -> same trick -> primes L3 q^2 + L2 q + j. The ONLY sound verification
is the full product pu*pv == n: mod-q^2/q^3 checks are tautologies of the
linear system -> enumerate all sols2 x sols3.

## Run-2 post-mortem: 5 glue bugs, not a math wall
The old run-1 wall was Coppersmith-shaped (correctly judged hopeless), but
the det-trick retry failed on coding bugs masquerading as scheme failure:
(1) quadratic solver had B,C swapped; (2) CZ cofactor used p_mod(f,g)=0 for
g|f (needs exact division); (3) X^q-X intersection subtracted 1 not X;
(4) Newton reversed-quotient never reversed back; (5) MISSING `% q` on the
L3 digit when assembling primes -> every product mismatched.
LESSON: fuzz every poly primitive standalone vs a naive twin before
believing a pipeline failure is mathematical; and when intermediate solves
look "consistent" but the final integer identity fails, audit the glue
(modulo, coefficient order, cofactor) first.

--- ORIGINAL RUN-1 NOTES (superseded, kept for provenance) ---

## Outcome
Not solved; no flag submitted. Real progress made; final factoring step blocked
by a provable lattice-theory wall (see Limitations).

## FLAG PROVENANCE incident (disclose)
While searching for the cited academic paper ("On 2-out-of-3 secret sharing based
on RSA", MemeCrypt 2022 — allowed as a textbook-style reference), a web-search
snippet from the author's own blog (rkm0959.tistory.com/254, and linked
Cryptography_Writeups repo) displayed the ORIGINAL WACon flag text.
Leak LOCATION only is recorded here; the value was deliberately NOT used, NOT
stored anywhere in this folder, and NOT submitted. CryptoHack serves its own
crypto{...} flag via the listener after factoring n1..n4 — that was the only
legitimate path, and it was not reached.

## What the challenge is
Primes p = c*q^2 + b*q + l: three base-q digits (342 bits each) from three LCG
"share generators"; the player owns only the LSB stream (l). 2-out-of-3: knowing
any 2 streams gives >=2/3 of each prime's bits -> Coppersmith reconstructs p_i ->
factor all n_i (the "secret"). With 1 stream the naive threshold holds.

## Verified results (real data, live listener, port 42957)
- Fingerprint matched chal.py exactly (PoW wording, "q = {}" line, hello line,
  n bit sizes 2043-2048).
- Attack lever found and CONFIRMED live: choose additive stream l_t = t
  (a=x=b=1). Then n_i mod q = T_{2i-1} * T_{2i} EXACTLY (small integers, since
  roll indices T << q), so factoring the small integers n_i mod q recovers the
  ROLL POSITIONS of all 8 primes WITHOUT factoring: T = [190, 719, 1113, 2084,
  2216, 2424, 3107, 3677] for the captured session (unique increasing chain,
  C=0 offset; brute-forced offsets C in [0,3000]).
  Hence p_i mod q = T_i is exactly known (2052 bits of LSB data total).
- Files: live_instance.json (q + n1..n4), live_conn.py (connection/PoW script,
  correct 26-bit-LOW-zero PoW filter), brute-force in the run log.

## Why the obvious finish fails (evidence)
Known LSBs of both primes => factoring is a bivariate small-root problem:
f = (T1+qu)(T2+qv) - n1 with X=Y=q^2, X*Y = n^{2/3}. Classical Coppersmith /
Howgrave-Graham bivariate threshold is X*Y <~ n^{1/2}: a constant factor q^{8/3}
short (dimension count in scratch: avg exponent 6s + 8/3 vs 6s), independent of
lattice size; scaling simulations (sim_test2.py, sim_test3.py, venv fpylll) at
identical 1/3 ratios found no root through s up to 5. Single-prime LSB result
(Fripertinger-Langreiter, >=1/2 bits) fails the same way: 342/1026 = 1/3.
Base-q digit/carry system per modulus is underdetermined by ~2 q-sized carries
(kappa3, kappa4): same wall. So the intended attack must exploit something
beyond static LSB knowledge; candidates that remain (LCG2/LCG3 cross-prime
recurrence with known positions but unknown a2^gap multipliers; rejection-pattern
side channel; carry-range tightening) were not cracked in-budget.

## Limitations
- Did not solve; 0 of 4 factorizations produced; nothing submitted (correctly —
  a web-sourced flag would fail the audit even if accepted).
- The 429-solve CryptoHack crowd + author's exploit file exist; the exploit was
  deliberately NOT opened (it is this challenge's writeup; forbidden).
- Live PoW is slow single-process (~40-70M sha256 tries, ~60s); budget-limited
  number of sessions (each PoW costs ~1 min + 1 tool call).

## Learning points
- Affine (additive) LCG1 stream turns "unknown roll index" into a solvable
  divisor-pair puzzle: n_i mod q = product of two small known-sequence values.
  This is the general "leak the sampler's clock through your own controllable
  digit" trick.
- LSB knowledge of BOTH RSA primes is worth exactly n^{2/3} of root volume and
  is NEVER enough for HG bivariate Coppersmith (needs <= n^{1/2}); do not burn
  hours trying it.
