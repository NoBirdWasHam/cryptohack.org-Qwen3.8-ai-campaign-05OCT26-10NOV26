# AAR — chaos-zh3r0_ctf_v22021 (Chaos, Zh3r0 CTF V2)

**Result: SOLVED.** Flag handed by the live listener on the first connection.
Flag stored in `flag_chaos-zh3r0_ctf_v22021.txt` (provenance: service output, live socket).
Submission: `ok:true`, solved list 264 → 265 (archive challenge, score_delta 0 as expected).

## The vulnerability
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

## The attack (linearized GF(2) collision search)
Naive z3 on `v(X,Y,Z,U)=v(X',Y',Z',U')` timed out (4 nonlinear 16×16 multiplications).
Instead: restrict each high halfword h to `{M-2^k, M}`, k=0..15 — then each product
`lo*(M-hi)` becomes `lo<<k` (or 0), i.e. **GF(2)-linear** in the low halfwords.
Per config C the map `lo (64 bits) -> v (128 bits)` is affine: `v = Lin_C·lo ⊕ base_C`.
Take two configs A≠B differing in one halfword; the collision condition
`[Lin_A Lin_B]·(lo_A, lo_B) = base_A ⊕ base_B` is a 128×128 GF(2) system — generically
nonsingular, hence solvable. Solved after 97 random config pairs.

Key numbers: M=0xffff; chosen hi halves A=(0xffef,0x7fff,0xfffe,0xffef) vs
B=(0xffef,0x7fff,0xffbf,0xffef); masked collision found in seconds; local clone
verified digest equality `0f0ed78a0f82b3dcbb1a19ecb4c2fa29`; live server accepted
immediately (live build == posted file).

## Files
- `statement.txt`, `site.md` — card statement + analysis notes
- `collide.py` — z3 attempt (timed out; kept for reference)
- `lin_collide.py` — working GF(2) collision finder
- `solve.py` — exact hash clone + message construction + live socket solve (`--nolive` = local-only)

## Limitations
- z3 direct modeling of the collision was tried once and timed out at 170 s; not retried
  with tactics — the structured GF(2) route replaced it immediately (loop-guard).
- Multi-block / 2-config-pair full search space not explored (unneeded).

## Learning points
- "Final extra rounds" that don't update their input state are a free cancellation —
  check loop-variable liveness before believing diffusion exists.
- Products `lo*(M-hi)` with `M-hi` a power of two are pure shifts: an easy way to pin
  a nonlinear design into a linear subspace and then collision-search between
  subspaces (affine-vs-affine GF(2) solve) when within-subspace rank is full.

---

<!-- AAR batch #9 quality upgrade (2026-11-02): publication sections appended; everything above this marker byte-identical to the pre-append AAR (hash in aar_batch9_pre.sha). -->

## Vulnerability (plain words)
The custom 128-bit "chaotic" hash has two fatal design flaws: its 4-iteration "extra chaos" final loop is a literal no-op (X, Y, Z, U are never updated inside the loop, and `RV ^= v^v^v^v` cancels to zero), and the first mixing round's mask is a fixed constant, so message bytes 0-15 directly set the four pre-mix words. Consequently a collision found for the *one-round* map propagates identically through the whole chained construction — a one-round break is a full-hash break.

## How the answer follows
1. Naive z3 on `v(X,Y,Z,U) = v(X',Y',Z',U')` timed out (4 nonlinear 16x16 multiplications), so constrain each high halfword `h` to `{M-2^k, M}` (k = 0..15, M = 0xffff): then `lo*(M-hi)` becomes `lo << k` (or 0) — the round map is **affine over GF(2)** per configuration: `v = Lin_C * lo XOR base_C`.
2. Pick two configs A != B differing in one halfword; the collision condition `[Lin_A Lin_B] * (lo_A, lo_B) = base_A XOR base_B` is a 128x128 GF(2) system, generically nonsingular hence solvable — a solution was found after 97 random config pairs (chosen A = (0xffef, 0x7fff, 0xfffe, 0xffef) vs B = (0xffef, 0x7fff, 0xffbf, 0xffef)).
3. Two 58-byte messages differing only in words 0..3 share identical padding, so `hash(m1) = hash(m2)`; local clone verified equal digests `0f0ed78a0f82b3dcbb1a19ecb4c2fa29`; the live listener accepted them on the first connection (live build == posted file) and handed the flag — provenance: service output on a live socket.

## Limitations / attempts that failed
- The direct z3 modeling timed out at 170 s and was not retried with tactics — the structured GF(2) route replaced it immediately (loop-guard honored).
- The multi-block / full two-config-pair search space was never explored (unnecessary for a win).

## Sources
- Self-derived per logs from the provided `challenge.py` alone; no writeups/solutions consulted. Background math (linearizing multiplication by restricting a factor to powers of two; GF(2) linear algebra) is standard and needed no external reference.
- Upgrade-time comprehension check (batch #9, 2026-11-02): re-derived the per-config affinity and the 128x128 system from `lin_collide.py`/`solve.py`; no live re-run; flag provenance unchanged.
