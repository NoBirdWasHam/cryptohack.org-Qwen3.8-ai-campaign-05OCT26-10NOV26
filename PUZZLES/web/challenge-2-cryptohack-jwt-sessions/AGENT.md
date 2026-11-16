---
record: agent-aar
puzzle: challenge-2-cryptohack-jwt-sessions
category: web
url: https://cryptohack.org/challenges/jwt-sessions/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt"
flag_sha256: 4d458161029653e9d3c7e0f65616e7bdf432e264a02d509f70d2b2ddb939f9cf
skills: []
human_twin: AAR.md
---

# AGENT — JWT Sessions (jwt-sessions, 10 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The "session" is a JWT, not a cookie — and it is transported in the `[flag — recorded in FLAGS/web/challenge-2-cryptohack-jwt-sessions/flag.txt]` header
(the flag is the header name itself). Read where the token lives (header vs cookie) per the
challenge statement.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Nothing failed; no further steps recorded in run logs. No artifacts archived beyond the backfilled statement in site.md.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Course statement (site.md backfill) + observed token transport. No external reference cited in run logs; no writeups consulted.
