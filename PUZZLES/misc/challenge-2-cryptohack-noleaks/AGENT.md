---
record: agent-aar
puzzle: challenge-189-cryptohack-noleaks
category: misc
url: https://cryptohack.org/challenges/noleaks/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/misc/challenge-2-cryptohack-noleaks/flag.txt"
flag_sha256: 38c5e968258ea59d2a46be811da654c2a7178e776757b9e427e06919741b79b0
skills: []
human_twin: AAR.md
---

# AGENT — noleaks (Misc 100) — SOLVED 2026-10-20 (+100)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
An OTP whose code asserts `ct[i] != flag[i]`: the key byte is never allowed to be 0 (key 0 would output the flag byte), which deletes exactly one ciphertext value per position — the flag byte itself. Each ciphertext byte is then uniform over the 255 values *excluding* flag[i]. Re-encrypting the same fixed plaintext under fresh keys turns the anti-leak assert into a membership oracle, and exhaustion finishes the message.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Nothing recorded as failed in run logs; the collect-and-exclude route was executed in one pass. (Sample-size tuning beyond the ~5500 collected is not recorded.)

## artifacts [OBSERVED]
- code: collect.py
- data/logs: collect.log, cts.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Own collection scripts/logs `collect.py`, `collect.log`, `cts.json`; coupon-collector probability (standard). No writeups consulted.
