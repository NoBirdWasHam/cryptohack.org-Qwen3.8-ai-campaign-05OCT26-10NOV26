---
record: agent-aar
puzzle: challenge-11-cryptohack-lfsr-destroyer
category: Misc
url: https://cryptohack.org/challenges/lfsr-destroyer/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/misc/challenge-11-cryptohack-lfsr-destroyer/flag.txt"
flag_sha256: 51ebad63188c069257c7f94900c3063539defe473309c063793110e767265ed7
skills: []
human_twin: AAR.md
---

# AGENT — lfsr-destroyer (CryptoHack, 250 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability / attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Chosen plaintext ⇒ encrypt 512 zero bytes ⇒ raw keystream (4096 bits).
Each keystream bit is a degree-5 polynomial in the 128 key bits (the tapped
bits are linear forms in the key, since the LFSR is linear). The system is
small enough to hand to a SAT solver: 128 Boolean key variables, symbolic
simulation of skip+512 output clocks, one equality constraint per keystream
bit. z3 (5.3.1) recovers the key in ~9 s; verified locally by re-running the
keystream, then sent `{"option":"get_flag","key":...}`.

## reusable-rules
- Chosen-plaintext on a keystream generator = free keystream; always try
  all-zero plaintext first.
- Filter generators with ≤128-bit state are routinely SAT-tractable even
  with degree-5 filters; bit-blasted symbolic simulation of the exact
  reference class is ~30 lines and beats hand-rolled algebra.
- Check the filter's Walsh spectrum to know whether correlation attacks are
  on the table (here bias 0.25 — surprisingly strong for a "destroyer").

## anti-patterns / limits
- Did not implement a fast-correlation (lattice) attack despite the bias;
  SAT was faster to build and comfortably within time.
- z3 runtime (6–14 s) is close to the 15 s per-message timeout; a slower
  machine could need fewer keystream bits or a different solver.
- Folder hygiene: the challenge folder also contains `source_b7cb...py` +
  `output_1078...txt`, which belong to a different (ElGamal-style per-bit
  padding) challenge, not lfsr-destroyer. Left untouched.
- No third-party writeups consulted; math derived locally. Reference for
  filter-generator theory: standard textbook material (e.g. Stinson &
  Paterson, *Cryptography: Theory and Practice*, stream-cipher chapters).

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_lfsr-destroyer.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
