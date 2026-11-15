# Chaos — Zh3r0 CTF V2 (CryptoHack archive)

- Slug: `chaos-zh3r0_ctf_v22021`
- Category page entry: card in `../cat_ctfarch.html` (51 solves, 0 solutions)
- Listener: `archive.cryptohack.org:18948` (xinetd, python-base:3.12, per-connection fresh process)
- Files: Dockerfile, challenge.py, chaos.xinetd (all saved in this folder)

## Provided-code summary (challenge.py)
Custom 128-bit hash over 64-byte blocks:
- `ROTL/ROTR` rotate-within-32 helpers, Merkle–Damgård-ish `pad` (0x80 + zeros + 4-byte big-endian length).
- State: 4 chaining vars `RV1..RV4`, mask vars `x,y,z,u` (initialized `0x0124fdce,0x89ab57ea,0xba89370a,0xfedc45ef`), consts `A..D`.
- Per 4-word group: `X,Y,Z,U = words ^ x,y,z,u`; then
  `RV1 ^= (x := (X&0xffff)*(M-(Y>>16)) ^ ROTL(Z,1) ^ ROTR(U,1) ^ A)` (and cyclic y/z/u variants with rotate amounts 2/2, 3/3, 4/4), `M = 0xffff`.
- **Final "extra chaos" loop is a no-op**: it never updates X,Y,Z,U, so each iteration recomputes the identical x,y,z,u and `RV ^= same ^ same ^ same ^ same` cancels.
- Win check: `m1 != m2 and hash(m1) == hash(m2)` -> print flag.

## Attack surface
First group's masked values X,Y,Z,U are fully attacker-controlled (message words 0..3 XOR fixed constants). One collision of the single-group map `v(X,Y,Z,U)` propagates through the whole chain identically -> full-hash collision. Solve `v(X,Y,Z,U) = v(X',Y',Z',U')` with distinct inputs.
