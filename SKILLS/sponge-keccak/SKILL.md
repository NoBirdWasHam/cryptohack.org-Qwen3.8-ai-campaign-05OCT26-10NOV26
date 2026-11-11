---
name: sponge-keccak
description: Use for sponge/Keccak CTF rate-capacity-duplex attacks.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, hash, keccak, ctf]
    related_skills: [hash-collision-md5-engineering, ctf-crypto-attacks]
---

# Sponge constructions (Keccak/SHA-3) — CTF surface

## When to Use
A challenge implements Keccak/SHA-3/Shake, a toy sponge, or a keyed-sponge MAC and you need the exact
absorb/squeeze semantics to attack it.

## The model (Bertoni–Daemen–Peeters–Van Assche, "Sponge Functions", 2007)
- State b = rate r + capacity c; absorb XORs message blocks into the FIRST r bits only, permute f each block;
  squeeze reads the first r bits. Security budget = c/2 (collision/preimage vs capacity).
- Keccak-f[1600]: 24 rounds of theta-rho-pi-chi-iota over the 5x5 lane state (rho offsets and iota round
  constants are the classic 'implement the spec exactly' bug farm — test vectors from the SHA-3 draft).
- Domain separation: SHA-3 pads with 01, Shake with 11c4 (multi-rate padding 10*1 inside the rate).
  A challenge omitting/altering padding = absorption bug, yours OR theirs — check both against the spec.

## CTF play patterns
1. STATE RECOVERY puzzles: observe >= r output bits between absorbs and only capacity bits stay secret —
   count what the permutation leaks (theta spreads column parity; single-round teasers solve linear-algebra-clean).
2. A raw sponge as 'MAC' with exposed mid-stream squeeze = free append (no capping) — the intended break in
   forge-the-MAC variants.
3. Duplex/keyed sponges cap the KEY into capacity first; 'ratcheted-state reuse across sessions' = state
   progression forensics.
4. CryptoHack 'Spongebob' wall: capacity-recovery hunt — walker2 threads carry live state; read that
   folder's AAR before re-deriving theory. Capacity-collision rho hunt: see references/walker3-vow-rho.md
   (mapping-vs-bijection rule, channel lemma, mandatory firing-harness gate, T1/SPREAD INIT pitfall,
   found_PROD naming safety rule).

## Canonical reference
[R32] BDPvA, "Sponge Functions", ECRYPT Hash Workshop 2007. http://sponge.noekeon.org/SpongeFunctions.pdf — NOTE: the sponge paper has no 2007 ePrint number; "IACR 2007/012" is Mashatan–Stinson (interactive authentication), a different paper. Do not cite an ePrint id for BDPvA 2007.
