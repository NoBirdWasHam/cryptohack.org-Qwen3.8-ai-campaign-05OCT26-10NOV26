---
record: agent-aar
puzzle: challenge-13390-cryptohack-one_round_crypto-ecsc_2024_it
category: misc
url: https://cryptohack.org/challenges/one_round_crypto-ecsc_2024_it/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/ctf-archive/challenge-13390-cryptohack-one_round_crypto-ecsc_2024_it/flag.txt"
flag_sha256: bd3dfca22e9f70be8e2471e835d257d01e9b2bb7e5e9cbf90e6215ba31dd3525
skills: []
human_twin: AAR.md
---

# AGENT — one_round_crypto (ECSC 2024 Italy), CryptoHack archive 13390
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack pipeline (attack2.py; 31.3s wall, 3072 blocks)" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
Cumulative root-cause failures (from "Root-cause bugs fixed"): (1) the old "M1 columns are 9-byte-sparse" structural model was entirely a bug artifact — local_oracle.mix applied the global rotation to a stale msg instead of b"".join(chunks), invalidating every earlier sparsity/atom measurement; (2) nullspace_basis/canon: stale pivot rows in an ascending RREF cleanup loop; (3) inter(): wrong coefficient solver (replaced by (A^⊥+B^⊥)^⊥); (4) solve_linear back-substitution direction (must be ASCENDING); (5) test harness encrypted the padded 16B block instead of the raw 15B challenge, making Φ look constant. A remote rank probe (probe_remote.py) exposed the local/remote mismatch that led to bug (1).

## artifacts [OBSERVED]
- code: atoms2.py, atoms_proto.py, attack2.py, attack_core.py, conv_test.py, diffuse_test.py, local_oracle.py, one_round_crypto.py, probe_remote.py, solve_remote.py, solve_remote2.py, test_local.py, test_local2.py
- data/logs: flag_one_round_crypto-ecsc_2024_it.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Biham & Shamir, doi 10.1007/BF00630563; theamazingking.com/crypto-diff.php;
  Dunkelman Lecture 2. Zero-difference preservation through an additive-keyed
  S-box is the invariant exploited here.
