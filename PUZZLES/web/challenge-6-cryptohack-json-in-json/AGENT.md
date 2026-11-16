---
record: agent-aar
puzzle: challenge-6-cryptohack-json-in-json
category: web
url: https://cryptohack.org/challenges/json-in-json/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-6-cryptohack-json-in-json/flag.txt"
flag_sha256: f4606e2ed0bdceff6d1b49e2630f1bc130b6ca8c2c27e4ab02693d88aaed3d5f
skills: []
human_twin: AAR.md
---

# AGENT — JSON in JSON (json-in-json, 40 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
JSON injection: the server embeds user-controlled JSON INSIDE another JSON document without
proper serialization, so crafted input breaks out of the string and injects new fields
(the OWASP Injection Theory the flag links to). Craft the payload so the inner JSON adds /
overrides the field that carries the flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No failed submission recorded in run logs.
- No request/response artifact archived (course challenge; accepted flag recorded in progress.json), so the payload cannot be re-verified from this folder.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement text (cached) — "exploit the code to sign unexpected data"; the flag itself links OWASP Injection Theory.
- Public spec (about the format itself): RFC 8259 (JSON string escaping rules — the layer where the bug lives).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
