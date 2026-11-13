---
record: agent-aar
puzzle: challenge-13398-cryptohack-2020-tetctf2020
category: misc
url: https://cryptohack.org/challenges/2020-tetctf2020/
status: solved
date: 2026-11-05
flag_ref: "FLAGS/ctf-archive/challenge-13398-cryptohack-2020-tetctf2020/flag.txt"
flag_sha256: c506648a67162d843817f48ff76c0bdbe5fd1d6ccb15a4f07b92f96ff2e332ec
skills: []
human_twin: AAR.md
---

# AGENT — 2020 (TETCTF 2020), archive.cryptohack.org:63222
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack I derived (and why it is the intended one)" [OBSERVED text; evidence tag applies to its source, not each claim]
MT19937 is GF(2)-linear; temper is a bijection, so each revealed output gives
the exact internal word behind it. CPython emits the word at linear position
X_{624+j} for output j (state index starts at 624, so the FIRST output comes
after the first twist). The twist in linear index m:

    X_m = X_{m-227} ^ (( (msb(X_{m-624})<<31 | low31(X_{m-623})) >> 1 )) ^ (MAGIC if X_{m-623}&1)

For the target X_2643 (output 2019): X_2643 = X_2416 ^ ((X_2020 & 0x7fffffff)>>1)
^ MAGIC·(X_2020&1) ^ msb(X_2019)<<30. Reveal indices **1792** (gives X_2416) and
**1396** (gives X_2020): 31 of 32 target bits are pinned; the only unknown is
msb(X_2019) (bit 30). Guess with msb=0 ⇒ **expected win-rate 1/2 per session**.
The formula is shift-invariant: any fixed number of extra draws before/around
the loop shifts reveals and target together and the same pair still works.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First two live runs wasted 60 sessions on a reveal-order swap bug (numbers
  arrive in increasing index order; fixed and retested).
- Could not fingerprint the live build further within budget: the two-reveals-
  per-connection, fresh-seed design gives no cross-session ground truth, and the
  WIN/MISS oracle bit was all that responded to hypotheses (5 hypothesis families
  tested, all rejected).
- Possibilities I could not test cheaply: FLAG env missing in the live container
  (correct guess crashing via KeyError would be indistinguishable from wrong),
  a non-MT PRNG in a patched `random` module, or an old/alternate build (cf.
  sigma-hamiltonicity2 "live build ≠ posted file" lesson). Per campaign rules I
  did NOT consult the archive repo/writeups for the flag.

## artifacts [OBSERVED]
- code: 2020.py, cone.py, cone2.py, diag.py, diag2.py, diag3.py, probe.py, probe2.py, probe3.py, probe4.py, probe5.py, probe6_drift.py, solve.py, solve2.py, solve3.py
- data/logs: flag_2020-tetctf2020.txt, probe5_stats.json, probe6_drift.json, probe6_drift.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Posted `2020.py` + live service I/O only. GF(2) linearity, untemper and the word/output mapping self-derived and self-verified with own tooling (`cone.py`, `cone2.py`, `solve3.py --local`); no external reference named in run logs. No writeups/solutions consulted (campaign rule).
