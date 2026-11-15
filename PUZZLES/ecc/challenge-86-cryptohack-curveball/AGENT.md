---
record: agent-aar
puzzle: challenge-86-cryptohack-curveball
category: Elliptic Curves
url: https://cryptohack.org/challenges/course__curveball/
status: solved
date: 07 Oct 2026
flag_ref: "FLAGS/Elliptic Curves/challenge-86-cryptohack-curveball/flag.txt"
flag_sha256: c99418b07057057f300842a2f5901c544afe0032128837cb5195da63d25d0441
skills: []
human_twin: AAR.md
---

# AGENT — Curveball (curveball, 100 pts, ECC course)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The server takes MY "generator" `g` (no validation) and computes `Q = g * d`, then matches
`Q` against its trusted-cert cache. Send `g = Q_bing` (Bing's trusted public key) and
`d = n + 1` (P-256 order + 1): `Q = (n+1) Q_bing = Q_bing + n Q_bing = Q_bing + O =
Q_bing` — a cache hit for Bing's cert without solving any DLP or changing the curve.
Protocol: one JSON object over the socket (private_key, host, curve, generator [x,y]).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
None recorded — solve.py's single-socket attack worked on the first try (2026-10-07 session); no
failed attempts are in the run notes. Evidence limit (not a failure): the flag STRING was never
archived (pre-convention solve); solved-list presence was verified 2026-10-17.

## artifacts [OBSERVED]
- code: solve.py, source_provided.py, verify_math.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Server behavior + provided `source_provided.py`; P-256 group law (order n ⇒ (n+1)·Q = Q); archived
`solve.py` + `verify_math.py`; self-derived; no writeups consulted.
