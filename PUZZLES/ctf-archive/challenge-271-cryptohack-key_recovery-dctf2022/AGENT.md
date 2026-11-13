---
record: agent-aar
puzzle: challenge-271-cryptohack-key_recovery-dctf2022
category: ctf-archive
url: https://cryptohack.org/challenges/key_recovery-dctf2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-271-cryptohack-key_recovery-dctf2022/flag.txt"
flag_sha256: 149886a635bd87392c67e6b6b412ef2ababbc723370f24eddc175fef12466d48
skills: []
human_twin: AAR.md
---

# AGENT — key_recovery-dctf2022 (SOLVED)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (solve4.py, 2048/3000 blocks, 8 sets)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. For each of 8 chosen plaintext bytes `i`, query 256 blocks varying byte `i`.
2. Because `per` permutes nibbles, every active byte at `z1/z2/z3` is **nibble-confined** (one fixed nibble, ≤16 values). The confinement sits on the **S-input** side while each round key XOR sits on the **S-output** side — so guessing a key byte (XOR on the output side) is NOT a conjugation of the confined set: `confined(candidate_layer_byte)` is an 8-bit-sensitive distinguisher (wrong guesses give random ~8-value sets failing confinement with prob ≈ 1−2^-40).
3. Peel exactly: `z3 = S_inv[ct⊕k3]`, `u2 = per_inv(z3)`, guess `k2` with `confined(S_inv[u2⊕g])`, `z2 = S_inv[u2⊕k2]`, same for `k1`; then `u0 = per_inv(z1)` is key-free and `k0 = u0 ⊕ S[x]` directly.
4. Bytes **{3,15} form a closed 2-byte island** of `per` — their key bytes are untestable, but island activity never contaminates the other 14 bytes. Brute force `K[3],K[15]` (2^16) against observed ciphertexts; verify with the sha512 key schedule. Unique candidate every time.
5. Submit full key via option 3.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- All superseded scripts (solve.py, solve2.py, solve3.py, attack.py, dbg.py) encoded the wrong round order sub(x XOR k) and are dead ends for the reason above; the unlock came from dbg2.py/probe*.py layer-confinement measurements that pinned the true round order.
- Beyond that, the run logs record no failed live approaches: remote gave k3/k2/k1/k0 14/14 bytes + unique island and the key was accepted first try, after local 5/5 validation.

## artifacts [OBSERVED]
- code: attack.py, dbg.py, dbg2.py, probe.py, probe2.py, probe3.py, remote.py, solve.py, solve2.py, solve3.py, solve4.py
- data/logs: flag_key_recovery-dctf2022.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Live listener archive.cryptohack.org:44134 + statement; own solve4.py, remote.py, dbg2.py, probe*.py; reconcile.py solved-readback. No external reference named in run logs; no writeups/solutions consulted.
