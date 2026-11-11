# AAR — better_than_linear (CryptoHack, isogenies, 85 pts) — SOLVED (documented in sibling folder)

## RECONSTRUCTED AAR (post-hoc)
Reconstructed 2026-11-01. This folder is a **ledger stub**: it holds only statement.txt (created 2026-10-21 01:23) and never contained a solve script or log. The actual work for this challenge (ledger nn217, status solved, date 2026-10-25) was done and documented in the sibling folder `challenge-167-cryptohack-better_than_linear/` — same statement parameters, file timestamps Oct 24–25 matching the ledger date, AAR records acceptance (`score_delta +85`, 2026-10-24). This is a duplicate-folder artifact of an nn/slug remap, not a second solve.

## Flag / answer
`48495725269*i + 91493879515` — the j-invariant answer accepted by the site. Provenance: derived in the sibling folder (solve_real.log, answer_real.txt, flag_better_than_linear.txt there; AAR.md "Flag" section). Copied verbatim into this folder's flag_better_than_linear.txt on 2026-11-01 so the stub is self-consistent. The ledger flag field for nn217 is null (answer-format challenge, not a crypto{...} string).

## Problem (from this folder's statement.txt)
Compute the j-invariant of the codomain of the degree-q isogeny of E/F_{p²}: y² = x³ + x, p = 92935740571, kernel generator K = (6312697112 + 11428792286i, 30552079595 + 78608501229i), q = ord(K) = 23233935143 — naive Vélu is O(q) ≈ 2.3e10, so the BDGLS sublinear algorithm is required.

## Method — pointer, not restatement
The full derivation (BDGLS elliptic-resultant algorithm 2 of Bernstein–De Feo–Leroux–Smith, "Faster computation of isogenies of large prime degree", eprint 2020/341, Edwards-form codomain update for A=0,B=1, numpy int64 19-bit-split vectorization, toy validation before the real instance) lives in `challenge-167-cryptohack-better_than_linear/AAR.md` with scripts solve.py, bdls.py, order.py, test_toy.py, verify_conj.py. No independent HOW can be claimed from THIS folder's contents.

## Limitations / honest notes
- No solve evidence exists inside this folder; everything above is cross-reference to our own sibling AAR, cited, not re-derived here.
- Recovery procedure not recorded; solve predates AAR discipline for this ledger row.
- Duplicate ledger rows (nn167 vs nn217 mapping to the same slug) should be reconciled by the ledger owner.

## Source disclosure
No third-party writeup. The sibling AAR is our own artifact; the only external reference cited there is the eprint named above (math reference, permitted).

## Files
statement.txt (original); flag_better_than_linear.txt (added 2026-11-01, copied from sibling folder's accepted answer).
