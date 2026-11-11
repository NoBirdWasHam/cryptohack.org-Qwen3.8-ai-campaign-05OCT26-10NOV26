---
name: ecdsa-nonce-xor-lattice
description: Use when ECDSA nonce k=d XOR z.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [ctf, crypto, lattice, ec]
    related_skills: [ctf-crypto-attacks]
---

## When to Use
A challenge signs with k = d XOR z (or any nonce linear/XOR-related to the key) and gives
several (z, r, s); or an ECDSA-adjacent flag is AES-CTR-encrypted under sha256(str(d)).

# ECDSA with nonce k = d XOR z (TSJ CTF 2022 style)

## Model
k = d^z = d + z - 2(d&z); s k = z + r d (mod q) gives per signature ONE linear equation
in the 256 bits d_j:
  sum_j 2^j d_j ((s-r) - 2 s z_j) = z(1-s)  (mod q)
m sigmas -> m equations, 256 binary unknowns -> unique solution.

## Correct lattice (NOT CVP on kernel of M)
Build dim N+7 Kannan lattice in Z^{263}: rows (q e_i, 0,0) for i<6; rows (M_col_j, -e_j, 0)
for j<256; target row (v, 0^256, 1). True bits appear as lattice vector (0^6, d, +-1),
norm ~11 vs GH ~230. LLL then SCAN rows: first 6 coords zero, |last|==1, middle in {0,-1}.
Why not CVP-on-kernel: binary constraint must be SHORTNESS in coordinates; in {x: Mx=0 mod q}
the solution sits at distance ~q*sqrt(m)/2 with ~2^63000 decoys — BKZ can never pick it.

## Verify d properly
- EC r-check must use UNreduced k (z is raw sha256, k>=q common).
- r AND s are blind to k -> k+-q: they cannot distinguish some XOR-shifted partners; the
  flag-key check is the real discriminator.
- Flag often key = sha256(str(d)).digest()[:16], AES-CTR.

## Missing-nonce CTR rescue (known plaintext)
If server pycryptodome dropped the random 8-byte CTR nonce (>=3.21: NOT prepended;
verify locally with a roundtrip), recover it by KPA: ks0 = P0 ^ ct[:16] with
P0='Congrats! This i'; cb = AES-ECB-decrypt(key, ks0); if cb[8:]==0 -> nonce=cb[:8],
decrypt whole ct with Counter.new(64, prefix=nonce, initial_value=0). Wrong key => random
looking cb (8 zero bytes = 2^-64): instant key diagnostic.

## fpylll on this host
- Enumeration dies silently at dim > 255 ('dimension is too high', prints, may abort proc).
- IntegerMatrix: no dump/load/.rows; use .nrows/.ncols + CSV snapshot. ALWAYS snapshot
  reduced bases before scanning (LLL here: 39s Kannan-lattice, 21min [M;qI] kernel basis).
- Run LLL/BKZ jobs in background; foreground caps at ~420s.
