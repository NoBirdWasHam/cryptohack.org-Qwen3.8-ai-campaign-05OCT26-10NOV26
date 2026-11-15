---
record: agent-aar
puzzle: challenge-319-cryptohack-chaos-zh3r0_ctf_v22021
category: CTF Archive
url: https://cryptohack.org/challenges/chaos-zh3r0_ctf_v22021/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-58-cryptohack-chaos-zh3r0_ctf_v22021/flag.txt"
flag_sha256: f4d0cde062c5d31a5ac381b9f2d0282a6f1eef78f04497058e6717246337e47c
skills: []
human_twin: AAR.md
---

# AGENT — chaos-zh3r0_ctf_v22021 (Chaos, Zh3r0 CTF V2)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Custom 128-bit "chaotic" hash (challenge.py). Two fatal design flaws:

1. **The "extra chaos" final loop is a no-op.** It loops 4 times computing
   `x := (X&0xffff)*(M-(Y>>16)) ^ ROTL(Z,1) ^ ROTR(U,1) ^ A` etc., but X,Y,Z,U are
   never updated inside the loop — every iteration recomputes the *identical* value
   and `RV ^= v^v^v^v` cancels to zero.
2. **The group-1 mask is a constant.** `X,Y,Z,U = words ^ x,y,z,u` with fixed
   initial constants, so the first 16 message bytes directly set the four pre-mix
   words. A single collision of the one-round map
   `v(X,Y,Z,U) = (v1..v4)` propagates identically through the whole chain
   (chained mask `x..u` = previous `v`), so `hash(m1)==hash(m2)` for two messages
   differing only in words 0..3 (both 58 bytes → identical padding).

## reusable-rules
- "Final extra rounds" that don't update their input state are a free cancellation —
  check loop-variable liveness before believing diffusion exists.
- Products `lo*(M-hi)` with `M-hi` a power of two are pure shifts: an easy way to pin
  a nonlinear design into a linear subspace and then collision-search between
  subspaces (affine-vs-affine GF(2) solve) when within-subspace rank is full.

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## anti-patterns / limits
- z3 direct modeling of the collision was tried once and timed out at 170 s; not retried
  with tactics — the structured GF(2) route replaced it immediately (loop-guard).
- Multi-block / 2-config-pair full search space not explored (unneeded).

## artifacts [OBSERVED]
- code: collide.py, lin_collide.py, solve.py
- data/logs: flag_chaos-zh3r0_ctf_v22021.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Self-derived per logs from the provided `challenge.py` alone; no writeups/solutions consulted. Background math (linearizing multiplication by restricting a factor to powers of two; GF(2) linear algebra) is standard and needed no external reference.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the per-config affinity and the 128x128 system from `lin_collide.py`/`solve.py`; no live re-run; flag provenance unchanged.
