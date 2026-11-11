# AAR — verilicious-cyber_apocalypse (CryptoHack archive, HTB Cyber Apocalypse 2025, author r4sti)

## Status
SOLVED & submitted (live solved-list confirms; archive worth 0 pts, score_delta 0).

## The vulnerability
`verify()` turns PyCryptodome's `PKCS1_v1_5.decrypt(ct, sentinel)` into a
binary "PKCS#1 v1.5 padding is VALID" oracle (sentinel is returned iff decode
fails). The `assert all(ver.verify(r^e * enc_flag) for r in R)` line then
publishes 78 multipliers r for which the oracle said VALID. Decoding of
r*m mod n (m = padded flag) is valid iff its top bytes are 00 02 (plus a 00
separator later) — i.e. r*m mod n ∈ [2^1009, 3·2^1008), an interval of width
2^1008 ≈ n / 2^15.4. Each multiplier leaks ~15.4 bits of m; 78 of them give
~1200 bits > 1024-bit m ⇒ m uniquely pinned (offline, non-adaptive RSA
scaling / HNP-style interval information).

## Attack
L = {(v_i) : v ≡ T·(R_j·R_0^{-1}) mod n} written as an honest basis:
row0 = (1, R_1 R_0^{-1}, …, R_{N−1} R_0^{-1}), rows n·e_i (i≥1). Closest
vector to (c,…,c), c = 2.5·2^1008: true per-coord error ≤ 2^1007, and the
box volume / det(L) = 2^{−185} ⇒ unique solution far under λ1/2.
`fpylllLLL.reduction` + `CVP.closest_vector` (radius-bounded enumeration)
solves it in ~0.7 s. Recover m = v_0·R_0^{-1} mod n, verify m^e ≡ enc_flag
and all 78 box constraints, strip PKCS1 padding (PS len 31) → flag.
Final script: solve3.py (solve.py/solve2.py = BKZ-Kannan detours, see below).

## Key numbers
- n: 1024-bit RSA, e = 65537, |R| = 78; interval [2^1009, 3·2^1008).
- Kannan embedding (dim 79, κ = 2^1007) + BKZ-40 stalled >25 min under CPU
  contention; `CVP.closest_vector` after plain LLL (40 s) finished in 0.7 s.
- Ground-truth sims sim6/sim8/sim9 (512/256-bit, N=78) reproduce the exact
  pipeline; sim9 match=True.

## Learning points
- A PKCS1v15 "decrypt with sentinel" oracle leaks ~15 bits per scaling
  multiplier (00 02 prefix = 8+7 bits of the residue), not 3 — always
  recompute interval widths from the *em* byte layout, not from
  "which byte differs".
- Build fpylll inputs as a true basis: the generator set {R-row} ∪ n·I is
  redundant (rank-deficient → LLL leaves a zero row → BKZ on non-basis =
  garbage). The (1, R_i/R_0) row0 form fixes both basis and redundancy.
- A box symmetric about the target center admits a mirror point; always
  discriminate candidates with the RSA relation m^e == enc_flag.
- For BDD with huge gap, fplll's `CVP.closest_vector` (Babai-radius
  enumeration) on an LLL basis is drastically faster than Kannan+BKZ.
- Checked first: is R a raw MT19937(randbytes) stream (twist/untwist test
  over all alignments — negative; seed(s) was a red herring).

## Limitations
- BKZ-40 Kannan embedding never completed on the real instance during this
  session (host saturated by 3 other agents' jobs; ~1100 s CPU spent in
  BKZ-25 stage too); the enumeration route succeeded instead, so BKZ-40
  feasibility here is untested rather than disproven.
- MT19937 angle ruled out by evidence (twist test over 1900 alignments,
  best match 0/300), not by proof; R is simply author-filtered multipliers.
- Flag's eprint reference was NOT consulted (flag text self-referential).

## Source (section added by 2026-11-09 corpus audit — AAR body text unchanged)
- Platform: CryptoHack, ctf-archive card 'Verilicious (Cyber Apocalypse 2025)' (challenge file per site.md).
- Statement provenance: statement.txt in folder (begins: "# Verilicious (Cyber Apocalypse 2025), contributed by r4sti # # A sacred ward, o...")
- Provided material as stored in folder: flag_verilicious-cyber_apocalypse.txt, mt_test.py, output.txt, sim.py, sim2.py, sim3.py, sim4.py, sim5.py
- Not consulted: /solutions/ pages, third-party writeups (campaign no-cheat rule).
