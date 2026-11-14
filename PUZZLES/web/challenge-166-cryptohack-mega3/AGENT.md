---
record: agent-aar
puzzle: challenge-166-cryptohack-mega3
category: web
url: https://cryptohack.org/challenges/mega3/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/web/challenge-166-cryptohack-mega3/flag.txt"
flag_sha256: 593e6037d2d1702a4b8347d766715ffd163a9ca928ba4ccc6b640e344871b9b7
skills: []
human_twin: AAR.md
---

# AGENT — CryptoHack Megalomaniac 3 (challenge-166, socket 13410)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack (1 query, ~1.3s live)" [OBSERVED text; evidence tag applies to its source, not each claim]
Every block of the private-key blob is now **known plaintext** under AES_master — except
`X = D_master(node_key_enc)`. Submit `share_key_enc` = legit blob ciphertext with
**ciphertext block 39 replaced by `node_key_enc`** (block 39 is interior to the `u`
field; length prefixes and padding block untouched → parse + unpad succeed).
The server decrypts block 39 to X and runs CRT with genuine `p,q,d` but
`u_g = u + (X − orig)·2^64` (orig = known u-bytes 104–119).

With `SID_enc = M^e mod n` (M = 2^1024+12345): `mp = M mod p`, `mq = M mod q`,
`t = (mq−mp) mod q` are all computable, and the returned `SID = (h·p + mp) >> 128` with
`h = t·u_g mod q`. Since `h·p = m_top·2^128 + m_low − mp` and `2^128 < p`, h is pinned to
≤ 2 candidates; for each, `u_g = h·t⁻¹ mod q` (± k·q resolved by the constraint
`(u_g − u) ≡ 0 mod 2^64`, |u_g−u| < 2^192) → `X = orig + (u_g−u)/2^64` = **node_key**.
Then `file_enc` → AES-ECB(node_key) → unpad → flag.

## reusable-rules
- When part of the key is leaked, the "hard" secret moves to the next layer (here the
  AES master key); the parse-tolerant CRT oracle then acts as a **leak channel**: put the
  unknown ciphertext block into a field whose corruption keeps the parse valid, and
  invert the algebra.
- PyCryptodome conventions matter: `RSA.u = inv(p, q)` (not inv(q,p)) and
  `d = inv(e, lcm(p−1,q−1))` — wrong conventions silently produce a mismatched blob
  (first offline run failed exactly this way).
- Truncation of 16 low bytes still leaves enough precision because p ≫ 2^128.

## anti-patterns / limits
- Relies on `t ≠ 0 mod q` (holds w.h.p.) and d being 256 bytes (assert catches shifts;
  retry gets a fresh instance).
- Did not attempt the generic padding-oracle route (unnecessary once p is given).

## artifacts [OBSERVED]
- code: 13410.py, dbg20.py, solve_mega3.py, test_offline_mega3.py
- data/logs: flag_mega3.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- PyCryptodome documentation (library conventions for rsa.u / lcm-based d) — tool reference, allowed.
- Conceptual lineage (public math): Bellcore-style CRT fault attacks; ECB block-swapping as a decryption oracle — standard textbook material, not challenge writeups.
- No third-party writeup or solution artifact for this challenge consulted.
