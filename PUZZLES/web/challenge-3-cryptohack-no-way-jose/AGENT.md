---
record: agent-aar
puzzle: challenge-155-cryptohack-no-way-jose
category: web
url: https://cryptohack.org/challenges/no-way-jose/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/web/challenge-3-cryptohack-no-way-jose/flag.txt"
flag_sha256: 060d2161389afbeb67fe2c3a4c07df2ac80153b07f304dc8dcf3cee63e46222c
skills: []
human_twin: AAR.md
---

# AGENT — No Way JOSE (no-way-jose, 20 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The Cryptographic Doom Principle: a single token carrying BOTH a signature and encryption
is attackable — tamper with the JOSE header (e.g., flip the `alg` so the verifier checks a
signature you can produce, or drop the encryption layer) and the "protected" payload is
yours. The challenge walks the JOSE header fields to set this up.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No failed submission recorded in run logs.
- No request/response artifact was archived (course challenge; only the server-accepted flag string lives in progress.json), so the exact token bytes cannot be re-verified from the folder.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement text (cached in statement.txt / site.md) — it names the none-alg issue and the doom principle.
- Public format specs (about JWT itself, not the solution): RFC 7515 (JWS header/`alg`), RFC 7519 (JWT claims).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
