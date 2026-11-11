# AAR — key_recovery-dctf2022 (SOLVED)

**Flag:** `dctf{M4k1ng_Sb0x3s_1s_t00_h4rd}` — accepted by site (solved count 252→253, confirmed via reconcile.py "LIVE solved" readback). Key recovered from listener `archive.cryptohack.org:44134`: `61f5bc36550413d15975e24136bbb0b2`.

## What the predecessor got wrong
The inherited `solve.py/solve2.py/solve3.py` modeled the round as `sub(x⊕k)` (XOR before S-box) and searched for an integral test invariant under key-byte conjugation — every such test is provably blind to half the bits of each key byte (XOR on one side of a byte S-box conjugates the confined structure). Hence endless "256 candidates" / "0 candidates" thrash.

## Actual cipher structure (the unlock)
`block()` does **sub → xor → per**: `u_r = S(z_{r-1}) ⊕ k_r`, `z_r = per(u_r)`, `ct = S(z3) ⊕ k3`; `per` is a pure **nibble permutation**. Key schedule: `k0 = K`, `k1‖k2‖k3 = sha512(K)[0:48]`.

## Attack (solve4.py, 2048/3000 blocks, 8 sets)
1. For each of 8 chosen plaintext bytes `i`, query 256 blocks varying byte `i`.
2. Because `per` permutes nibbles, every active byte at `z1/z2/z3` is **nibble-confined** (one fixed nibble, ≤16 values). The confinement sits on the **S-input** side while each round key XOR sits on the **S-output** side — so guessing a key byte (XOR on the output side) is NOT a conjugation of the confined set: `confined(candidate_layer_byte)` is an 8-bit-sensitive distinguisher (wrong guesses give random ~8-value sets failing confinement with prob ≈ 1−2^-40).
3. Peel exactly: `z3 = S_inv[ct⊕k3]`, `u2 = per_inv(z3)`, guess `k2` with `confined(S_inv[u2⊕g])`, `z2 = S_inv[u2⊕k2]`, same for `k1`; then `u0 = per_inv(z1)` is key-free and `k0 = u0 ⊕ S[x]` directly.
4. Bytes **{3,15} form a closed 2-byte island** of `per` — their key bytes are untestable, but island activity never contaminates the other 14 bytes. Brute force `K[3],K[15]` (2^16) against observed ciphertexts; verify with the sha512 key schedule. Unique candidate every time.
5. Submit full key via option 3.

## Validation
- 5/5 random local keys recovered end-to-end (`python3 solve4.py 5`).
- Remote: k3/k2/k1/k0 = 14/14 bytes, island unique, self-check vs all collected pairs, key accepted first try.

## Files
- `solve4.py` — working attack (importable: `choose_sets`, `_guess`).
- `remote.py` — socket oracle + attack + key submission.
- `dbg2.py`, `probe*.py` — layer-confinement measurements that pinned the round order.
- `flag_key_recovery-dctf2022.txt` — the flag.
- Superseded: `solve.py`, `solve2.py`, `solve3.py`, `attack.py`, `dbg.py`.

## Vulnerability (plain words)
The 4-round cipher is sub -> xor -> per (u_r = S(z_{r-1}) XOR k_r; z_r = per(u_r); ct = S(z3) XOR k3), and `per` is a pure NIBBLE permutation. The inherited solvers modeled the round as sub(x XOR k) and searched for integral tests invariant under key-byte conjugation -- provably blind to half the bits of each key byte (XOR on one side of a byte S-box conjugates the confined structure), hence their endless 256/0-candidate thrash. With the true order, nibble confinement sits on the S-INPUT side while each round key XOR sits on the S-OUTPUT side: guessing a key byte is NOT a conjugation of the confined set, so confinement of the candidate layer byte is an 8-bit-sensitive distinguisher (wrong guesses give random ~8-value sets failing confinement with prob ~1-2^-40).

## How the answer follows
1. For each of 8 chosen plaintext bytes i, query 256 blocks varying byte i (2048/3000 blocks, 8 sets); every active byte at z1/z2/z3 is nibble-confined (one fixed nibble, <=16 values).
2. Peel exactly: z3 = S_inv[ct XOR k3]; u2 = per_inv(z3); guess k2 via confined(S_inv[u2 XOR g]); peel z2; same for k1; u0 = per_inv(z1) is key-free so k0 = u0 XOR S[x] directly.
3. Bytes {3,15} form a closed 2-byte island of `per` -- untestable by confinement but island activity never contaminates the other 14 bytes; brute force K[3],K[15] (2^16) against observed ciphertexts and verify against the sha512 key schedule (k0 = K, k1||k2||k3 = sha512(K)[0:48]) -> unique candidate every time.
4. Submit full key (option 3): K = 61f5bc36550413d15975e24136bbb0b2 from listener archive.cryptohack.org:44134 -> flag dctf{M4k1ng_Sb0x3s_1s_t00_h4rd}, accepted (solved 252->253, reconcile.py LIVE readback). 5/5 random local keys recovered end-to-end (python3 solve4.py 5).

## Limitations / attempts that failed
- All superseded scripts (solve.py, solve2.py, solve3.py, attack.py, dbg.py) encoded the wrong round order sub(x XOR k) and are dead ends for the reason above; the unlock came from dbg2.py/probe*.py layer-confinement measurements that pinned the true round order.
- Beyond that, the run logs record no failed live approaches: remote gave k3/k2/k1/k0 14/14 bytes + unique island and the key was accepted first try, after local 5/5 validation.

## Sources
Live listener archive.cryptohack.org:44134 + statement; own solve4.py, remote.py, dbg2.py, probe*.py; reconcile.py solved-readback. No external reference named in run logs; no writeups/solutions consulted.
