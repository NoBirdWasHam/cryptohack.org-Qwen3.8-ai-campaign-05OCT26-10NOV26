---
record: agent-aar
puzzle: challenge-156-cryptohack-saying-hello
category: web
url: https://cryptohack.org/challenges/saying-hello/
status: solved
date: 2026-10-13
flag_ref: "FLAGS/web/challenge-11-cryptohack-saying-hello/flag.txt"
flag_sha256: 3dc8734418fb2c835e2f002da0359665edfb09a3306dab2f11bb417fa1158663
skills: []
human_twin: AAR.md
---

# AGENT — Saying Hello (saying-hello, 20 pts, Web course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
TLS handshake reading: the client's `ClientHello` and the server's `ServerHello` exchange
cipher suites in the clear. The flag is the negotiated cipher suite — read it from the
handshake (the challenge provides the handshake to inspect).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No failed submission recorded in run logs.
- The specific reader/tool used to view the handshake was not recorded (course challenge; the handshake to inspect was provided by the challenge itself, and no capture artifact was archived beyond the backfilled statement in site.md).

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement text (cached) — it defines record format and suite-name components.
- Public spec (about TLS itself): RFC 5246 appendix A (cipher-suite naming/IDs).
- No third-party writeup or solution artifact consulted (source-disclosure rule).
