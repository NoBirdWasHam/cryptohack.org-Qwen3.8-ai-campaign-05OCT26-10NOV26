# AAR — one_round_crypto (ECSC 2024 Italy), CryptoHack archive 13390

## Status: SOLVED. Flag captured live and submitted (solved-list 259 -> 260).
Flag: ECSC{d035_7h15_d357r0y35_ASA?!_c25976c15c535a3d}
(self-derived attack only; official writeup NOT consulted, per flag-provenance rule)

## Cipher
C = M3 * sigma * M1 (one S-layer): M1,M3 GF(2)-linear 128x128 mix maps seeded by
k1=sha256(key), k3=sha256(sha256(k1)); sigma = per-byte keyed AES S-box
sigma_i(x)=S(x)+k2_i mod 256. Block 16B. Game: 1 free chosen query, then 100
random 15B plaintexts (PKCS7 pad 0x01) whose plaintext hex must be returned.
Key is FRESH PER CONNECTION (verified empirically; no cross-session reuse).

## CORRECTED structural fact (the old "9/16 byte support" was a bug artifact)
Earlier sessions' diffuse_test.py result (M1 columns exactly 9-byte-sparse,
key-independent) came from a WRONG local_oracle.mix: it applied the global
rotation to a stale msg instead of b"".join(chunks). After fixing mix to match
one_round_crypto.py exactly (cross-checked against exec'd challenge source):
- M1/M3 columns are DENSE (byte support 15 for a few columns, 16 for the rest).
- For a RANDOM 128-bit difference d: Pr[byte j of M1*d == 0] ~ 2^-8, uniform
  over all 16 bytes (measured 1.4-3.0 hits per byte per 600 draws, 8 keys).
- Such "byte-killer" differences give ciphertext-difference spans of dim 120
  whose nullspace is exactly the dim-8 atom A_j = M3^-T(B_j).

## Enabling trick (this session): coset difference pools
Detecting rank<=120 needs >=121 realizations of the SAME difference, so random
pairs cost 242 blocks per probe (far too few probes). Instead send the message
as m cosets of a dim-7 GF(2) subspace U (blocks = s_i ^ u, u in U). Then for
EVERY coset pair (i,j) and every u in U, the difference D = s_i^s_j^u is
realized 128 times inside the same 3072-block message (~14s server time):
~10k byte-killer probes, enough to find all 16 atoms w.h.p.

## Attack pipeline (attack2.py; 31.3s wall, 3072 blocks)
1. build_message2(mcos=12, dim=7, extra=1536) -> 3072 blocks, 9972 probes.
2. Per probe: rank of its 128 ciphertext diffs (early-exit once >120). Rank<=120
   -> W = nullspace (dims 8/9/16/64 observed). dim-8 = atom; larger dims are
   intersected by BFS (annihilator identity) until all 16 atoms appear.
   All 16 matched ground-truth M3^-T byte atoms (verified offline).
3. Fiber tables: Phi_j(P) = (<u_t, C>)_t for atom basis u; blocks sharing a
   Phi value yield kernel K (dim 120); lam = K^perp (dim 8) gives 8 linear eqs
   lam(P)=lam(rep) per byte; 16 atoms -> unique P. sigma is never recovered
   (its unknown per-byte bijection is absorbed by fiber membership).
4. Answer 100 challenges by solving the 128x128 GF(2) system (padding byte
   0x01 resolves underdetermined cases).

## Root-cause bugs fixed (cumulative)
1. local_oracle.mix missing msg = b"".join(chunks) before the global rotation
   -> invalidated every earlier sparsity/atom measurement (the big one).
2. nullspace_basis & canon: stale pivot rows in an ascending RREF cleanup loop.
3. inter(): wrong coefficient solver; replaced by (A^perp+B^perp)^perp.
4. solve_linear: back-substitution must be ASCENDING (a pivot row's leading bit
   is its highest; it defines P_k from LOWER bits).
5. Test-harness padding bug: encrypt the raw 15B challenge, not the padded 16B
   block, else the wrong (all-0x01 pad) block is read and Phi looks constant.

## Files
- attack2.py        build_message2 / rank_le_120 / Decryptor2  (FINAL attack)
- test_local2.py    local end-to-end vs corrected oracle: 100/100 in 12.7s
- solve_remote2.py  live solve 100/100 in 31.3s, flag captured
- attack_core.py    GF(2) utilities + older single-bit-pair Decryptor (library)
- probe_remote.py   remote rank probe that exposed the local/remote mismatch
- flag_one_round_crypto-ecsc_2024_it.txt  captured flag

## References (differential framing)
- Biham & Shamir, doi 10.1007/BF00630563; theamazingking.com/crypto-diff.php;
  Dunkelman Lecture 2. Zero-difference preservation through an additive-keyed
  S-box is the invariant exploited here.

## Vulnerability (plain words)
The cipher applies one S-layer: C = M3 · σ · M1, where M1, M3 are GF(2)-linear 128×128 byte-mixing maps (seeded by hashes of the key) and σ is a per-byte additive-keyed AES S-box, σ_i(x) = S(x) + k2_i mod 256. An additive-keyed S-box preserves **zero byte differences**: if byte j of M1·Δ is 0, then byte j of the ciphertext difference of any pair with input difference Δ is also 0 — regardless of the unknown key. Such "byte-killer" differences Δ have ciphertext-difference spans of dimension ≤120, and the 8-dim nullspace of that span is exactly the byte atom A_j = M3⁻ᵀ(B_j). Recovering all 16 atoms lets you build per-byte linear "fibers" that pin down any plaintext from its ciphertext — inverting the cipher without ever recovering the key.

## How the answer follows
1. Structural ground truth (after fixing the local oracle — see failures): M1/M3 columns are DENSE; for a random 128-bit Δ, Pr[byte j of M1·Δ = 0] ≈ 2⁻⁸ uniformly (measured 1.4–3.0 hits/byte per 600 draws over 8 keys) ⇒ ~1 in 256 differences is a byte killer for a given j.
2. Detection economics: rank ≤120 needs ≥121 realizations of the SAME difference, so instead of 242-block random pairs, the message is sent as m cosets of a dim-7 GF(2) subspace U (blocks s_i ⊕ u): every coset-pair difference D = s_i⊕s_j⊕u is realized 128 times inside one chosen-query message of 3072 blocks (~14 s server time) ⇒ ~10k byte-killer probes.
3. Per probe: rank of its 128 ciphertext diffs (early exit >120). Rank ≤120 ⇒ nullspace W; dim-8 W = atom; dims 9/16/64 (intersections) resolved by BFS with the annihilator identity until all 16 atoms appear — all 16 matched ground-truth M3⁻ᵀ byte atoms offline.
4. Inversion: fiber table Φ_j(P) = (⟨u_t, C⟩)_t over the atom basis u; blocks sharing a Φ value yield kernel K (dim 120), and λ = K^⊥ (dim 8) gives 8 GF(2)-linear equations λ(P) = λ(rep) per byte; 16 atoms ⇒ unique P. σ is never recovered — its unknown per-byte bijection is absorbed by fiber membership.
5. Answer the 100 random challenges by solving the 128×128 GF(2) system (the fixed 0x01 PKCS7 pad byte resolves underdetermined cases). Local: 100/100 in 12.7 s (test_local2.py); live: 100/100 in 31.3 s (attack2.py/solve_remote2.py) → flag `ECSC{d035_7h15_d357r0y35_ASA?!_c25976c15c535a3d}` (solved-list 259→260). Key empirical fact: key is FRESH per connection (verified), so all learning must happen inside one chosen query.

## Limitations / attempts that failed
Cumulative root-cause failures (from "Root-cause bugs fixed"): (1) the old "M1 columns are 9-byte-sparse" structural model was entirely a bug artifact — local_oracle.mix applied the global rotation to a stale msg instead of b"".join(chunks), invalidating every earlier sparsity/atom measurement; (2) nullspace_basis/canon: stale pivot rows in an ascending RREF cleanup loop; (3) inter(): wrong coefficient solver (replaced by (A^⊥+B^⊥)^⊥); (4) solve_linear back-substitution direction (must be ASCENDING); (5) test harness encrypted the padded 16B block instead of the raw 15B challenge, making Φ look constant. A remote rank probe (probe_remote.py) exposed the local/remote mismatch that led to bug (1).

## Sources
Provided challenge source one_round_crypto.py (cross-checked by exec); differential framing references cited in the original AAR: Biham & Shamir (doi 10.1007/BF00630563), theamazingking.com/crypto-diff.php, Dunkelman Lecture 2 (zero-difference preservation through an additive-keyed S-box is the exploited invariant). Official writeup NOT consulted, per flag-provenance rule.
