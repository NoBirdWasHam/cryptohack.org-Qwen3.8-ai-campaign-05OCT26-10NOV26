---
record: agent-aar
puzzle: challenge-13391-cryptohack-maybe_someday-googlectf2022
category: CTF Archive
url: https://cryptohack.org/challenges/maybe_someday-googlectf2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-45-cryptohack-maybe_someday-googlectf2022/flag.txt"
flag_sha256: 92131e52026880783175ee826e5fc568a1f52eb169844b79581a91ada4146681
skills: []
human_twin: AAR.md
---

# AGENT — maybe_someday (GoogleCTF 2022) — CryptoHack archive 14846 — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
design3.py: pool of 1406 (K,t) columns (quantile thresholds for K=0/255, random t for
mid-K) over 65536 candidate patterns; greedy (max pairs removed) + hill-climb.
Result: 20 queries, 62040 unique patterns, 1730 collision patterns covering 3496
candidates. Decode: response word r → true pattern must be a **submask** of r (the
only noise, P_last==1 → P−1 borrow → extra zero byte, ~1/255/round, flips 😡→😀 only);
pick max-popcount table entry; if r is a known collision pattern → **abort session
without guessing** (free reconnect). Wrong-guess death is avoided, so ~2.7%/round
collision risk costs only session retries, not progress.
Live run: attempt1 hit collision at round 14, attempt2 at round 11, attempt3
survived 16/16 → flag. solve.py is runnable (DESIGN env var; --local runs against
chall.py subprocess with FLAG=TEST{...}).

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Design NOT collision-free (1730 dup patterns); survives only via abort+reconnect.
  repair.py (targeted t for remaining classes) ran in background toward a cleaner
  design4.json — not required for the solve.
- P−1 noise (1/255/round) tolerated only by submask decoding; no error-correction
  margin designed (min pattern distance unoptimized).
- `grab_int` bug cost a debug cycle: `re.search(r'\d+', 'c0 = …')` matched the '0'
  in "c0" → c0=0 → all-😡. Fixed with split('=').
- Predecessor's design_qs.json / design2.py are built on the wrong 512-bit layout —
  obsolete; kept for history.

## artifacts [OBSERVED]
- code: dbg1.py, design2.py, design3.py, fixdup.py, modelcheck.py, modelcheck2.py, probe.py, probe2.py, probe3.py, probe4.py, probe5.py, probe6.py, repair.py, solve.py, test_local.py
- data/logs: design3.log, design_qs.json, flag_maybe_someday-googlectf2022.txt, repair.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided materials only; self-derived per run logs. (Predecessor artifacts referenced in the AAR are this campaign's own earlier session, not external writeups.)
