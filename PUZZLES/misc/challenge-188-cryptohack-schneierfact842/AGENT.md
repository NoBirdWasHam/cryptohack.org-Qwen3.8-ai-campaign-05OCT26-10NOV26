---
record: agent-aar
puzzle: challenge-188-cryptohack-schneierfact842
category: misc
url: https://cryptohack.org/challenges/schneierfact842/
status: solved
date: 2026-11-01
flag_ref: "FLAGS/challenge-188-cryptohack-schneierfact842/challenge-188-cryptohack-schneierfact842/flag.txt"
flag_sha256: 8265045d368269eefa414bfd7ffd0aec4e9da3512d75f196a359a73b37bfa3fd
skills: []
human_twin: AAR.md
---

# AGENT — schneierfact842 (Misc 100) — SOLVED 2026-10-20 (+100)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The server accepts a password when the sum *and* the product of its character codes are prime — both computed with 64-bit numpy. A product of >= 2 integers > 1 can never be prime mathematically, but int64 multiplication silently wraps modulo 2^64, and the wrapped residue *can* be prime. Integer overflow turns an impossible check into a ~1/44 probabilistic one.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Local primality checks disagreed until the int32-vs-int64 pitfall was caught: Windows numpy defaults to int32, so early local emulation wrapped the product at the wrong width; fixed by explicit int64 (signed mod 2^64) emulation.
- No other failed attempts recorded in run logs.

## artifacts [OBSERVED]
- code: find_pw.py, find_pw2.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Own search scripts `find_pw.py` / `find_pw2.py`; numpy integer-wrap semantics (documented two's-complement wrap). No writeups consulted.
