---
record: agent-aar
puzzle: challenge-141-cryptohack-wots_up-ecsc_2023_norway2023
category: hashes
url: https://cryptohack.org/challenges/wots_up-ecsc_2023_norway2023/
status: solved
date: 2026-10-16
flag_ref: "FLAGS/hashes/challenge-15-cryptohack-wots_up-ecsc_2023_norway2023/flag.txt"
flag_sha256: 9d4f0f944528d157ed4950a2a2d50e1c81aa4ddcc75e096d2a7fb52226ca51a0
skills: []
human_twin: AAR.md
---

# AGENT — WOTS Up (wots_up-ecsc_2023_norway2023, 75 pts, Hashes)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
WOTS-256 (SHA-256) signature forgery via a **seeded private-key chain**. In `__init__`
(`chal_provided.py`), the 32 private-key chain starts are successive hashes of ONE seed:
`priv[i] = H^(i+1)(seed)`. So every element `sig1[i] = H^(255-b1[i])(priv[i])` of the given
signature sits at chain position `p1[i] = 256 + i - b1[i]` on a SINGLE chain from the seed,
where `b1 = SHA-256("WOTS Up???")`. Any chain element at position >= min(p1) is reachable by
plain forward hashing from the known sig1 elements. The target message "Sign for flag" has
bytes `b2`; the provided data satisfies `b2[i] <= B_i` at all 32 positions (B_i from the
known elements), so the whole target signature is forged by forward hashing only — no
collision search. The AES-CBC key for the vault is built from the first byte of each forged
signature element (per chal.py), decrypting the flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Single-shot solve; no failed attempts recorded in run logs. The forward-reachability check b2 ≤ B held everywhere on the provided data — the harder "some positions behind" case (needing collision search) never occurred and was never implemented.

## artifacts [OBSERVED]
- code: chal_provided.py, solve.py
- data/logs: data_provided.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided files only: `chal_provided.py`, `data_provided.json`. Self-derived from provided code; no writeups/solutions consulted; no external reference cited in run logs.
