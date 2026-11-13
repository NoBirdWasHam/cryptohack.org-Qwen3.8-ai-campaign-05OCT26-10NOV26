---
record: agent-aar
puzzle: challenge-139-cryptohack-seventy_two
category: hashes
url: https://cryptohack.org/challenges/seventy_two/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/hashes/challenge-139-cryptohack-seventy_two/flag.txt"
flag_sha256: 100d45132d471c9ed3877f13b8d5b30fbea5c1d7a94032b59810161078ef927c
skills: []
human_twin: AAR.md
---

# AGENT — Challenge 139: Seventy-Two (50 pts, hashes → key derivation)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
The server binds credentials as `material = f"{TENANT}|{username}|{password}"` and stores
`bcrypt.hashpw(material, gensalt(cost=8))`. **bcrypt silently uses only the first 72 bytes
of its input** (the C implementation's `EXTRACT_SALT`/password loop bound) — the "Seventy-Two"
of the title.

Effective entropy per account = `72 − len("TENANT|user|")` bytes of the 32-char random
password (charset = 62 alnum):

| account | len("TENANT\|user\|") | effective pw bytes | search space |
|---|---|---|---|
| root | 42 | 30 | 62^30 — infeasible |
| backup@corp.bluerock.example | 66 | 6 | 5.7×10^10 — infeasible |
| m.laurent@corp.bluerock.example | 69 | 3 | 238,328 — feasible |
| **k.barrymore@corp.bluerock.example** | **71** | **1** | **62 — trivial** |

The directory service's own tenant/account binding is what creates the win: the long
Bluerock email usernames eat the 72-byte budget. `k.barrymore@...` leaves exactly **one**
password byte in the hash, so the stored hash is determined by a single character.

## reusable-rules
- **bcrypt's 72-byte input limit is a real, exploitable design flaw** (not just a lint
  warning): any scheme that concatenates identifiers into the bcrypt input gets its
  effective key material silently truncated. The fix is to hash the components (e.g.,
  HMAC/SHA-256 of the full material) or use a modern KDF (Argon2id, as the statement hints)
  with no such truncation.
- When a service concatenates `tenant|user|password` for a KDF, **compute the prefix length
  for every account** — the longest username minimizes the effective password space.
  Here the challenge was literally designed so one account sits 1 byte under the limit.
- Socket-listener challenges: probe the protocol once (`before_input` line, single JSON
  request, JSON response) before writing the loop; the listener gives one shot per
  connection, so sequential connections are the natural brute-force shape.

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: 13433.py, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs.
