---
name: wagner-generalized-birthday
description: Use on k-sum list puzzles and iterated hash collision tasks.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, birthday, ctf]
    related_skills: [hash-collision-md5-engineering, ctf-crypto-attacks]
---

# Wagner's generalized birthday problem (k-sum)

## When to Use
Challenge gives 2^a-sized lists of hashes/vectors and asks for a k-way sum = 0 (LCS/Iterated-Merkle-Damgard
collisions, Merkle tree second-preimage ladders, subset-sum-lite with slack bits).

## The algorithm
- k = 2^m lists of n-bit values. Pair lists with matching FIRST n - log2(k) bits (keep ~log2(k) slack per
  level), xoring away matched bits each level; ~2^(n/(1+log2 k)) total work with list memory at the same
  order.
- Recursion bookkeeping is where implementations die: store PARENT POINTERS at every merge (path
  reconstruction from level-m pair back to k originals); xored values carry the FULL original vector
  alongside the trimmed key.

## CTF variants to recognize
1. Iterated hash tree (LCS): find k leaves whose combined 'collision path' meets — Wagner on the tree's
   level-2 nodes, not raw leaves.
2. k-XOR over GF(2)^n given as oracle: same ladder; budget memory honestly (level-1 list ~2^(n-log k)).
3. Subset-sum with enough slack bits is Wagner-able over the bit vectors; without slack -> lattice route
   (qary-cvp-ternary-ringlwe / ctf-lattices) instead.
- Memory discipline on this host: cap lists, spill to disk-backed arrays over 2GB/proc (host rules).

## Canonical reference
[R33] Wagner, "A Generalized Birthday Problem", CRYPTO 2002, LNCS 2442, pp.288-303.
