---
record: agent-aar
puzzle: challenge-16-cryptohack-wots_up_2-ecsc_2023_norway202
category: Hash Functions
url: https://cryptohack.org/challenges/wots_up_2-ecsc_2023_norway2023/
status: solved
date: 2026-10-16
flag_ref: "FLAGS/hashes/challenge-16-cryptohack-wots_up_2-ecsc_2023_norway202/flag.txt"
flag_sha256: e7562192e9278d527fd78d1e093ab7e14946b698e02c264d82b4ebd0a11ae5c0
skills: []
human_twin: AAR.md
---

# AGENT — WOTS Up 2 (wots_up_2-ecsc_2023_norway2023, 90 pts, Hashes)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
WOTS-256 forgery from **20 past transaction signatures** of the same key (the "fix" made the
32 chain starts independent, but the safe now holds 20 signatures). For chain position i
(byte i of the SHA-256 of each signed message), signature j gives the chain point
`H^(255-b_j[i])(priv[i])` on the 256-link chain toward `pub[i]`. Let `B_i = max_j b_j[i]`;
the closest known point to the private key is at exponent `e_i = 255 - B_i`. Any needed
point with `b2[i] <= B_i` is reached by forward hashing only. With the provided data,
`b2[i] <= B_i` for all 32 positions, so the target signature ("pub[0] sent 999999 WOTScoins
to me") is forged by forward hashing. The AES-CBC key comes from the first byte of each
forged element (per chal.py).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Single-shot solve; no failed attempts recorded in run logs. The b2 ≤ B coverage held on the provided data; the partial-backwards case was never needed.

## artifacts [OBSERVED]
- code: chal_provided.py, solve.py
- data/logs: data_provided.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided files only: `chal_provided.py`, `data_provided.json`. Self-derived; no writeups/solutions consulted; no external reference cited in run logs.
