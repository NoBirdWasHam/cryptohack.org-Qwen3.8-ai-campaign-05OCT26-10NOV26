---
record: agent-aar
puzzle: challenge-4-cryptohack-jwt-secrets
category: web
url: https://cryptohack.org/challenges/jwt-secrets/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-4-cryptohack-jwt-secrets/flag.txt"
flag_sha256: 554542589a054a7f64aea9af6a0996a5cecf8c588e28190f3e00fc948a9112c8
skills: []
human_twin: AAR.md
---

# AGENT — JWT Secrets (jwt-secrets, 25 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
HS256 JWTs are only as strong as their HMAC secret. The challenge's secret is guessable /
crackable (weak or published) — recover it (dictionary / the provided hint), re-sign a
forged token with it, and the server accepts it.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No failed submission recorded in run logs.
- No token/request artifact archived (course challenge; accepted flag recorded via progress.json only), so the crack step cannot be re-verified from this folder.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement text (cached) — HS256 vs RS256 trade-off and the weak-secret hint.
- Public specs (about the formats themselves): RFC 2104 (HMAC), RFC 7518 (JWA/HS256).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
