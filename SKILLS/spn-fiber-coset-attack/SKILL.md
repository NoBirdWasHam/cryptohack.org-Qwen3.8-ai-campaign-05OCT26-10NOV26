---
name: spn-fiber-coset-attack
description: Use when inverting a 1-round SPN with unknown mix layers.
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [crypto, spn, gf2, cryptohack]
    related_skills: [ctf-crypto-attacks, cryptohack-socket-challenges]
---

# One-round SPN fiber attack (C = M3·σ·M1, unknown linear layers)

## When to use
Cipher is one keyed S-box layer between two secret GF(2)-linear layers (or the
game asks to invert such a permutation with one bulk chosen-plaintext query).

Solved CryptoHack `one_round_crypto-ecsc_2024_it` (100 inversions/one chosen query, 300s).

## Core invariant
Zero S-box differences survive an additive-keyed S-box: σ(x)^σ(x^d)=0 iff d_j=0.
So a plaintext diff with byte j of M1·d == 0 (a "byte-killer", prob ~2^-8 per byte
for random d) makes ≥121 ciphertext diffs span only dim 120; its nullspace is the
dim-8 atom A_j = M3^-T(byte-j subspace). 16 atoms = byte access to middle space.

## Coset difference pools (the enabling message design)
Rank-≤120 detection needs ≥121 realizations of the SAME difference; random pairs
cost 242 blocks/probe. Instead send m cosets of a dim-7 GF(2) subspace U
(blocks = s_i ^ u): for every coset pair (i,j) and every u∈U, diff s_i^s_j^u is
realized 128 times for free. ~10k probes from 3072 blocks (~15s server).
General rule: put the chosen-plaintext set under additive structure so many
differences come with many samples.

## Decryption without recovering σ
Φ_j(P)=(⟨u_t, C⟩) for atom basis: value depends only on middle byte j.
Blocks sharing a Φ-value give kernel vectors; K reaches dim 120, λ=K^⊥ gives 8
linear eqs λ(P)=λ(rep) per atom; 16 atoms → unique P by GF(2) solve. Known
padding byte breaks underdetermined ties (enumerate free bits, filter by pad).

## Pitfalls that cost days here
- Validate the local oracle against the real server cipher FIRST (a one-line
  stale-variable bug in a simulated mix() poisoned every measurement: apparent
  column sparsity 9/16 vs true dense 15/16).
- GF(2) utils: nullspace RREF cleanup must iterate pivots DESCENDING using
  current rows; intersections via annihilator (A^⊥+B^⊥)^⊥; back-substitution
  ASCENDING (pivot = highest bit, depends on lower bits).
- Encrypt the RAW challenge bytes; PKCS7-padding a full 16B test block reads the
  wrong (pad) ciphertext block → Φ looks constant.
- Archive listeners rotate key per connection: no cross-session reuse; one shot.
