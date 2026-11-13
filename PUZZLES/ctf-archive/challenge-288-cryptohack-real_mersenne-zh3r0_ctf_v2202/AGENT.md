---
record: agent-aar
puzzle: challenge-288-cryptohack-real_mersenne-zh3r0_ctf_v2202
category: ctf-archive
url: https://cryptohack.org/challenges/real_mersenne-zh3r0_ctf_v2202/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-288-cryptohack-real_mersenne-zh3r0_ctf_v2202/flag.txt"
flag_sha256: ac3eef2bc3abbd04a38d567bcc42377d6b95fb1279f216d40ed6eaf3a08d789b
skills: []
human_twin: AAR.md
---

# AGENT — real_mersenne (zh3r0_ctf_v2, CryptoHack archive #288)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Server-side `random.random()` (CPython MT19937) used to draw the hidden `x` each
round. The score line leaks, for y=0 probes, `u = int(2**53 * random())`, i.e.
the top 27 bits of output word o_2i and top 26 bits of o_{2i+1} per round.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- live_run2.log: bailed "Error, exiting" — cause unknown at that point
  (round()-stopped-at-score-line discarded the flag line; confirmed by
  round_log.txt of live_run3: H1906 total 1000487.04 > 10^6, next line
  'Error, exiting' — the flag was printed but never read).
- live_run4: EOFError after H1907 (total 1000081.87) — flag line printed but
  `crypto{...}` regex didn't match the actual flag prefix; fixed with generic
  token{...} regex + raw line logging.
- Local mock (`--local`) with decoy flags `[flag value withheld — real-flag strings live only under FLAGS/]` and
  `zh3r0{...}` verified the fixed reader before the live run.

## artifacts [OBSERVED]
- code: live_probe.py, live_solve.py, live_solve2.py, mt_lib.py
- data/logs: flag_real_mersenne-zh3r0_ctf_v2202.txt, live_run.log, live_run2.log, live_run3.log, live_run4.log, live_run5.log, raw_log.txt, round_log.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
not recorded in run logs (pre-discipline solve)
