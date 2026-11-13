---
record: agent-aar
puzzle: challenge-151-cryptohack-token-appreciation
category: web
url: https://cryptohack.org/challenges/token-appreciation/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-151-cryptohack-token-appreciation/flag.txt"
flag_sha256: 6d2f8ff9ede6f2fd78d38623bbd03ab9700a7d1e77ce70c8b67ec44447debb56
skills: []
human_twin: AAR.md
---

# AGENT — Token Appreciation (token-appreciation, 5 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
JWTs are base64url-encoded JSON — the payload ("claims") is readable by anyone. Decode the
middle segment of the provided token to read the flag. No key, no forgery: the lesson is
that JWTs are signed/encrypted, not obfuscated-by-default.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Single-step course solve; nothing failed and no further steps recorded in run logs. No artifacts archived beyond the backfilled statement in site.md (exact decode command not recorded).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided token from the course statement (site.md backfill). No external reference cited in run logs; no writeups consulted.
