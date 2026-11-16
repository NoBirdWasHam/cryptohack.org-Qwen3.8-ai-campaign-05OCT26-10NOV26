---
record: agent-aar
puzzle: challenge-47-cryptohack-probability-seetf2022
category: CTF Archive
url: https://cryptohack.org/challenges/probability-seetf2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-47-cryptohack-probability-seetf2022/flag.txt"
flag_sha256: 2392d5f09b68db256193cb30b7f8a8d56bdfa16a968bdfb7acde85c35be6b546
skills: []
human_twin: AAR.md
---

# AGENT — probability-seetf2022 (SEETF 'probability')
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Server prints every `random.random()` draw from a global CPython Mersenne Twister.
Each double leaks 27 bits of one MT word (bits 31..5 of temper(w)) + 26 bits of its
partner. Honest play wins ~0.42/round; 800/1337 needed -> must predict future draws.

## reusable-rules
- CPython twist is j-227 based, and Stream doubles need temper(state words).
- `for _ in range(2): y ^= y>>18` == identity (involution) — classic untemper trap.
- Full-foresight blackjack vs fixed dealer rule: per-round value 0.523 < the
  0.598 threshold; only cross-round phase control (global DP) bridges the gap.

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: probability.py, run_live.py, solve.py
- data/logs: flag_probability-seetf2022.txt, live.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs. (The 'prior session's solve.py' fixed in this AAR is this campaign's own earlier attempt, not an external writeup.)
