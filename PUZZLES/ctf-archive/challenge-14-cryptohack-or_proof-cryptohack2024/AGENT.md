---
record: agent-aar
puzzle: challenge-14-cryptohack-or_proof-cryptohack2024
category: ctf-archive
url: https://cryptohack.org/challenges/or_proof-cryptohack2024/
status: solved
date: 2026-10-19
flag_ref: "FLAGS/ctf-archive/challenge-14-cryptohack-or_proof-cryptohack2024/flag.txt"
flag_sha256: 3cfef71a5b8eb5fcc0897918315a87a243b9014ae05ea01edbec2e610fe27c45
skills: []
human_twin: AAR.md
---

# AGENT — 276-cryptohack-or_proof-cryptohack2024: OR Proof (CryptoHack) — CTF Archive
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
Solved as part of the 231 sigma-or-proof run (2026-10-19): 3-phase OR-protocol protocol —
honest proof on the witnessed branch (w0 shipped in `chal.py`), witness extraction from the
double transcript (special soundness), SHVZK simulation for the given `s`. Full details,
flag ground truth, and the regex-grab protocol pitfall are in
`../challenge-231-cryptohack-sigma-or-proof/AAR.md`.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
None in this folder — no distinct attack was attempted for the archive slug. The limitations are
inherited from the 231 sigma-or-proof run (see `../challenge-231-cryptohack-sigma-or-proof/AAR.md`),
including its regex-grab protocol pitfall. Folder thinness is scope, not failure: statement provenance
is a CTF archive page scrape.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: flag_or_proof-cryptohack2024.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Canonical solve record: `../challenge-231-cryptohack-sigma-or-proof/AAR.md` (same server
archive.cryptohack.org:11840; the same flag satisfies both slugs — one credit per slug in the ledger).
No third-party writeups.
