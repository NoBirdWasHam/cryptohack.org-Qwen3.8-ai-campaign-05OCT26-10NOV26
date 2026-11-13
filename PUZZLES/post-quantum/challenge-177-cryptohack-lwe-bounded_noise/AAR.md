# AAR — Bounded Noise (challenge-177-cryptohack-lwe-bounded_noise)

LWE with **binary** noise (n=25, m=625, q=65537); the 25 base-q digits of S ARE the flag (49-byte template `crypto{...}`).

## Attack
CVP lattice `[A^T|0; 0 q]` is WRONG for mod-q LWE (the signal A*s mod q is not a lattice point). Algebraic route instead:
1. Pick 25 pivot rows forming an invertible 25x25 subset; parameterize s = s0 + N*e where e is the 25-dim binary error (e_j in {0,1}) and N spans the error space of the remaining rows.
2. One extra row prunes 2^25 candidates to ~1026 (incremental Gray-code evaluation keeps it fast in pure Python).
3. Full verification of all 625 equations; unique candidate -> flag digits.

## Result
**SOLVED** — `[flag — recorded in FLAGS/post-quantum/challenge-177-cryptohack-lwe-bounded_noise/flag.txt]}` (submitted 2026-10-13, live-verified). Files: `_pq/bounded_noise_output.txt`, `_pq/solve_bn_enum.py` (working), `_pq/_bn_parsed.json`.

_Backfill note (2026-10-14): this doc folder was created after the fact; all scripts/data referenced above live in `_pq/` and the flag was verified live on 2026-10-13._


## Vulnerability (plain words)
The noise is *binary*: each of the 25 error coordinates is in {0,1} instead of drawn from a spread-out distribution. Noise is the one thing standing between LWE samples and plain linear algebra; a 25-bit discrete error set is small enough to enumerate and structured enough to linearize. The flag name literally states the fix: linearised polynomials for bounded errors.

## How the answer follows
1. First instinct — CVP embedding lattice [[A | 0],[0 qI]] — is recorded in the run log as a **failed** approach: with mod-q LWE the true signal A·s (mod q) is a residue class, not a fixed lattice point the target can be measured against, so nearest-plane/Babai drifts without a well-defined error vector to chase.
2. Algebraic route instead: pick 25 of the 625 rows that form an invertible 25×25 matrix over GF(65537). Solving those rows expresses the secret *affinely in the error*: s = s₀ + N·e, where e ∈ {0,1}²⁵ is the unknown binary error and N is the kernel-style lift matrix — this is the "linearisation": guessing the 25-bit noise determines s completely.
3. Prune with the remaining rows: each extra equation a candidate s₀+N·e must satisfy kills ~half the space; one well-chosen extra row cut 2²⁵ candidates to ≈1026 (Gray-code enumeration — flip one e-bit at a time and update N·e incrementally — kept 33M evaluations cheap in pure Python).
4. Verify survivors against **all 625** equations; exactly one candidate survived → its base-q digits are the flag.
Result `[flag — recorded in FLAGS/post-quantum/challenge-177-cryptohack-lwe-bounded_noise/flag.txt]}`, submitted 2026-10-13, live-verified.

## Limitations / attempts that failed
- Failed attempt kept deliberately: the wrong CVP embedding (step 1) — this is the documented dead end.
- Run logs do not record whether additional pruning rows or BKZ-style fixes were tried beyond the single extra row + exhaustive verification.

## Sources
- Server-provided instance `_pq/bounded_noise_output.txt`; working solver `_pq/solve_bn_enum.py` (+ `_pq/_bn_parsed.json`). Theory background: bounded-noise-LWE is standard (Regev-style learning with errors where e is sparse/binary), but no external writeup was consulted.
