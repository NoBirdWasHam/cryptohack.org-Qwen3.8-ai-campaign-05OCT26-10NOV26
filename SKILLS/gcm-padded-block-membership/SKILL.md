---
name: gcm-padded-block-membership
description: Use for GCM tag oracles using 12-byte blocks.
---

# GCM 12-byte-block (V-subspace) tag-oracle attacks

Verified model (pycryptodome, bit-exact):
- GHASH blocks are 16-byte-ALIGNED over raw entry bytes; 12-byte chunks only give V-membership
  (last-4-bytes-zero subspace) for block 0 of a ≤12-byte entry and the final partial block.
  len>12 entries straddle chunks — do NOT model per-chunk V per block.
- Block i exponent = s−i (i 0-based incl. final len block at exponent 1; 96m‖96n bits).
  Min DATA-block exponent = 2 ⇒ membership cuts Z∈H²V (s1-side u1-pair XOR) or H³V (s0-side);
  Z∈H·V is impossible. E=AES_K(J0)=empty-digest=win value; T = GHASH ⊕ E; keystream block j
  = AES_K(J0+1+j); ciphertext bytes are as free as plaintext (model per-byte 8-bit unknowns).
- Field: int=block BE, int bit b = coeff x^(127−b); mul_x(a)=(a>>1)^(0xE1<<120 if a&1);
  gmul=Horner; identity = 1<<127 (int 1 is x^127 — a classic trap).

Structure (CryptoHack greatest_common_multiple, archive 2762):
1. Win = predict E = new().digest(); oracle tag/u1(replace 12B)/u2(append 12B), coins hidden.
2. Given H=AES_K(0)+coins, ALL tags are GF(2)-LINEAR in (E, per-byte block unknowns) → RREF;
   E-bit identified iff PURE pivot row (particular solution with mixed free vars is WRONG — trap).
3. Given H, u1 coins via Z∈H²V vs H³V membership; u2 coins via 3-tag combos where (H^k⊕1)E cancels.
4. H WITHOUT msolve: u1-pair tag-xors D_i satisfy the truncated-LCG-class lattice relation
   (m4gb/structural_elim.dfs_solve, ks_allowed=(2,3), survivors==1 semantics, det ~1/16 fail;
   gf_inv_model converts survivor -> H; self-check H^2 = x^2-reduction zero). Live-verified.
5. u2 coin-path DFS with per-tag consistency pruning over u2 tail (+1 adaptive u1 at end,
   rank-neutral-to-positive): unique leaf = true transcript; E determined iff rank(E-rows)==128
   (~12% at tail>=20, ~19% with adaptive u1). Buy misses with CONNECTION RETRIES (fail-closed,
   answer only at 128), not transcript length (rank plateaus at ~20 u2 coins).
6. SERVICE budgets: archive 2762 session alarm ~30 s wall from PoW-success (hard; probe:
   prompt alive 28.9 s, aborted 34.7 s). Collect ~8 s + solve must fit ~20 s.
7. DFS COST: recomputed powH/gmul dominates (90%). Memoize powH per-H power-table + gmul
   pair-cache (pure memoization): 50.8 s -> 2.9 s. Tree-split multiprocessing is USELESS here:
   pruning collapses the frontier to one live path (Amdahl-serial); fix node cost instead.

Tooling: msolve `-t 2` works (`[-1]`=UNSAT, `[0,[p,...]]`=parametrization); `-g 2`=GB dump; no `-L`;
path args must be Windows-style. Run ⟨x+1⟩ / ⟨1⟩ control before trusting any result (broken builds
exist that print [-1] always). Working reference: Practice_runs/cryptohack_org/challenge-317-*greatest*/
model.py (gmul, ghash, membership_pols f→g1→g2 chains, run_h_solve, solve_E byte tokens + pure-row test).
SOLVED 2026-11-06 via route 1-7 above; live runner = challenge-317-*greatest*/live_run.py (fail-closed
 gates; flag format trap: service prints `tag: codegate2024{...}`, platform slug greatest_common_multiple-code).

## Canonical references (owner list 2026-11-02)

[R25] NIST SP 800-38D (GCM): the authoritative J0/GHASH/tag construction this skill's algebra must match when specs differ from a challenge's reimplementation. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf | [R24] FIPS 197 (AES). https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf (see block-cipher-standards skill).
