---
record: agent-aar
puzzle: challenge-9-cryptohack-lwin
category: misc
url: https://cryptohack.org/challenges/lwin/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/misc/challenge-9-cryptohack-lwin/flag.txt"
flag_sha256: aee8128a3184e324ced50b975c8b80248e40a240510824c197f468e108d16fe8
skills: []
human_twin: AAR.md
---

# AGENT — CryptoHack "lwin" (L-Win, 120 pts, misc)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Recover the taps linearly.** For n ∈ [768, 2431] every index `n+t` and `n+384` lies inside
   the known window, so `Σ_t v_t·s[n+t] = s[n+384]` is a GF(2) linear system in the 384-bit
   tap-indicator vector v (1664 equations). [flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt] (rows as Python ints) gave
   rank 384 → unique solution: taps **[0, 6, 15, 16]**.
2. **Backward extension.** Characteristic polynomial `p(x) = x^384 + Σ_t x^t`. Since tap 0 is
   present, p(0)=1 and the state transition is invertible; directly `s[m] = s[m+384] + Σ_{t≠0} s[m+t]`
   (equivalently divide p by x^{t_min}=1) extends the sequence backwards from the window to
   s[0..383].
3. **Verify:** forward-simulated from recovered s[0..383] with the recovered taps — reproduced
   all 2048 window bits; bytes decode to printable `crypto{...}`.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- **Naive Berlekamp–Massey fails.** BM on the window returns the *tail's* minimal polynomial
  (degree 265 on a toy), which annihilates the sequence only from n ≥ 768 onward, so backward
  extension through it corrupts the first ~119 bits. Verified by checking the BM recurrence
  against a ground-truth toy sequence (56 violations at small n).
- **Singular transition when 0 ∉ taps:** p(x) has factor x^{t_min}; the first t_min initial bits
  are then information-theoretically lost through 768 clocks (toy trials with t_min=119/191
  recovered the tail but not the head). Here tap 0 was present, so recovery was unique.
- Two coding bugs fixed during dev (pivot-store falling into consistency check; back-substitution
  direction) — caught only by the toy harness.

## artifacts [OBSERVED]
- code: lwin.py, solve.py, solve2.py, toy.py, toy2.py
- data/logs: flag_lwin.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Challenge files `lwin.py`, `output.txt`; own solvers `solve2.py` (working) / `solve.py` (failed BM); toy harnesses `toy.py`, `toy2.py`. No writeups consulted.
