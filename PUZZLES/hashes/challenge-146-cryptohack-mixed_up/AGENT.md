---
record: agent-aar
puzzle: challenge-146-cryptohack-mixed_up
category: hashes
url: https://cryptohack.org/challenges/mixed_up/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/hashes/challenge-146-cryptohack-mixed_up/flag.txt"
flag_sha256: 995265264f1dafdc60ce5dc4c4f9c77149cccca855e8b3b1b2674d341c4eea99
skills: []
human_twin: AAR.md
---

# AGENT — mixed_up (CryptoHack, hashes, 120 pts) — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability / Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Recorded in solve.py's own docstring and confirmed by the mock server in test_local.py:
- The **AND** branch leaks FLAG bits *as indices*: if `data[j] = 2^b`, then `mixed_and[j] = FLAG[j] & 2^b` is either 0 or `2^b` — the index into the value pool reveals bit b of FLAG[j].
- **Length recovery:** send `data = 00*96` → all indices 0 → very_mixed = one random byte c repeated L times. Brute force all (c, m≤96) against the returned hash → L = 39, "probe byte c=235" (live_run.log line 1).
- **Bit recovery:** for each bit b (0..6) and each of 4 position-groups, send `data[j]=2^b` on the group, 0 elsewhere. Then very_mixed is byte x0 at positions where FLAG bit b is 0 and x1 where it is 1 (x0, x1 unknown random pool bytes). Brute force (x0, x1, subset) = ~2^(16+k) SHA-256 hashes (k = group size ≤ 10, Gray-code enumeration in `_brute`), unique match → 10-bit mask of the group's bit. 7 bits × 4 groups = 28 probes, each 2–4.5 s (live_run.log lines 2–29), 8-worker process pool.
- Assembled prefix/suffix verification passed (live_run.log line 30).

## reusable-rules
- A hash over a *structured, low-entropy preimage* is a brute-force oracle, not a shield: the preimage space here was 256² × subsets, not 2²⁵⁶.
- AND leaks information through *indices/positions* while XOR leaks through *values*; randomizing one channel does not silence the other.

## anti-patterns / limits
- Original session transcript does not exist; reconstruction is from the solver script + its own logs only. The uniqueness argument for the (x0, x1, subset) brute force is asserted in solve.py's docstring ("unique match reveals the bits"); we did not re-derive uniqueness here.
- ledger notes carry no method text ("| API-verified"); dates: folder artifacts span Oct 12 (statement fetch) → Oct 22 (live run logs), ledger date 2026-10-21.

## artifacts [OBSERVED]
- code: 13402.py, solve.py, test_local.py
- data/logs: flag_mixed_up.txt, live_run.log, local_test.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
No third-party writeup consulted (reconstruction from our own artifacts only). No external math reference used.
