---
record: agent-aar
puzzle: challenge-217-cryptohack-better_than_linear
category: isogenies
url: https://cryptohack.org/challenges/better_than_linear/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/isogenies/challenge-19-cryptohack-better_than_linear/flag.txt (absent — honest null; see note in FLAGS/INDEX.jsonl)"
flag_sha256: null — flag withheld (note in FLAGS/INDEX.jsonl)
skills: []
human_twin: AAR.md
---

# AGENT — better_than_linear (CryptoHack, isogenies, 85 pts) — SOLVED (documented in sibling folder)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Method — pointer, not restatement" [OBSERVED text; evidence tag applies to its source, not each claim]
The full derivation (BDGLS elliptic-resultant algorithm 2 of Bernstein–De Feo–Leroux–Smith, "Faster computation of isogenies of large prime degree", eprint 2020/341, Edwards-form codomain update for A=0,B=1, numpy int64 19-bit-split vectorization, toy validation before the real instance) lives in `challenge-167-cryptohack-better_than_linear/AAR.md` with scripts solve.py, bdls.py, order.py, test_toy.py, verify_conj.py. No independent HOW can be claimed from THIS folder's contents.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No solve evidence exists inside this folder; everything above is cross-reference to our own sibling AAR, cited, not re-derived here.
- Recovery procedure not recorded; solve predates AAR discipline for this ledger row.
- Duplicate ledger rows (nn167 vs nn217 mapping to the same slug) should be reconciled by the ledger owner.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: flag_better_than_linear.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
No third-party writeup. The sibling AAR is our own artifact; the only external reference cited there is the eprint named above (math reference, permitted).
