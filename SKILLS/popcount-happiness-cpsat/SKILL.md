---
name: popcount-happiness-cpsat
description: "Use when a CTF leaks popcount(A & m): solve via CP-SAT."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, cpsat, ortools]
    related_skills: [ctf-crypto-attacks, ctf-lattices]
category: ctf-crypto-attacks
tags: [ctf, crypto, cpsat, ortools]
---

# Popcount/happiness oracle: solve with CP-SAT per block

> **PROVENANCE:** PATH WALKED — CP-SAT-per-block + reconnect-on-fresh-instance is the
> author's official solve shape (SekaiCTF repo solve.py, cited in challenge-259 AAR);
> four prior self-derivation runs had priced a lattice route instead. Local engineering
> (offline replay of cached captures, resume-state, worker caps) added here. Re-derive
> first on fresh challenges; this recipe is a reminder the family is SAT-shaped.

## When to Use
Challenge server prints `pubkey` of N random big ints and, per message block, the list
`[popcount(A_j & m)]`. Unknown m hides a flag segment inside random padding.

When `c_j = popcount(pub[j] & m)` for ~256 random 512-bit pub[j] and unknown m with a few
secret bytes amid random padding (CryptoHack/SekaiCTF FaILProof family):

- Do NOT lattice/CVP-reduce unless the flag is static and instances resample. The system is
  information-theoretically unique (~2^1100 constraint bits vs 2^512 solutions), and CP-SAT
  pseudo-Boolean propagation cracks it in seconds: 512 BoolVars x[p] (LSB index), one linear
  equality `sum(x[p] for p in set_bits(pub[j])) == c_j` per j. Author's intended path.
- Verify independently: `bin(pub[j] & m).count('1') == c_j` for all j, then decode
  `m.to_bytes(64,'big')[24:32]` (padding layout urandom||secret||urandom). Ignore old
  keep-index/MSB-weight lattice glue.
- Per-instance hardness VARIES (planted twist): use per-block time caps 5s -> 10s -> 20s
  escalation, and/or reconnect for a fresh instance and keep blocks that landed (flag is
  static across connections; only secret/padding refreshes).
- KEY: if the flag is static, any CACHED capture of the listener output is a valid flag
  source — replay solver on cached instances before spending any live connections.
- Working implementation: Practice_runs/cryptohack_org/
  challenge-259-cryptohack-failproof_revenge-sekaictf202/cpsat_solve.py (offline+live modes,
  num_search_workers=2, resume-state JSON).
