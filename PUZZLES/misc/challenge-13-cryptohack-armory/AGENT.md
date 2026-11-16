---
record: agent-aar
puzzle: challenge-13-cryptohack-armory
category: misc
url: https://cryptohack.org/challenges/armory/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/misc/challenge-13-cryptohack-armory/flag.txt"
flag_sha256: 2c72e38a9f5a35198c57ac05e75bb272aa26bb3fb9e2b77b54fa0161efe920bd
skills: []
human_twin: AAR.md
---

# AGENT — armory (Misc 100) — SOLVED 2026-10-20 (+100)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The "deterministic-share" backup builds the Shamir polynomial by hashing: coefs = [s, c1, c2] with c1 = sha256(s), c2 = sha256(c1) — and it evaluates share i at x = c_i, so the *published x-coordinates in share.txt are exactly the polynomial's own coefficients* (c1 verbatim; c2 recomputable as sha256(c1)). The "you need 3 shares" claim assumes evaluation points are public randomness irrelevant to the polynomial; here every term except s itself is readable from one share line plus a hash.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- The run log is a one-paragraph AAR: no failed attempts are recorded in run logs.

## artifacts [OBSERVED]
- code: armory.py
- data/logs: share.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Challenge-provided files `share.txt` and server source `armory.py`. No third-party writeups consulted.
