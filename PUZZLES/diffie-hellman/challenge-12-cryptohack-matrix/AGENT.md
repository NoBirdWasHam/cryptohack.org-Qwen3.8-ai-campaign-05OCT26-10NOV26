---
record: agent-aar
puzzle: challenge-12-cryptohack-matrix
category: diffie-hellman
url: https://cryptohack.org/challenges/matrix/
status: solved
date: 16 Oct 2026
flag_ref: "FLAGS/diffie-hellman/challenge-12-cryptohack-matrix/flag.txt"
flag_sha256: 81be67a06e6f8f45b1a5189b29668a1e57a7a6fd0631f1c4ae73e1e025316a25
skills: []
human_twin: AAR.md
---

# AGENT — matrix (75 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Read the generator: 50×50 matrix M over GF(2); first 272 bits of `msg` = flag,
   rest random; require det ≠ 0 and multiplicative_order > 10^12; C = M^31337 saved
   as flag.enc.
2. Goal: recover M from C = M^E with E = 31337 (prime), without knowing ord(M).
   Key fact: ord(M) divides the **exponent of GL(50,2)**
   `L = lcm(2^d − 1 : 1 ≤ d ≤ 50) · 2^6` (the 2^6 comes from unipotent/Jordan
   blocks; each 2^d−1 is odd). L is 785 bits.
3. Since E ∤ L (order of 2 mod 31337 is > 50, so 31337 ∤ any 2^d−1, d≤50), solve
   `k ≡ −L·E⁻¹ (mod E)` and set `t0 = (1 + k·L)/E` — then `E·t0 ≡ 1 (mod L)`
   hence `E·t0 ≡ 1 (mod ord(M))`, so `M = C^{t0}`.
4. One fast exponentiation in GL(50,2): rows packed as 50-bit ints, mul = 2500
   AND+parity ops; ~785 squarings → under a second in pure Python.
5. Verify `M^E == C` (TRUE). Recover msg via M[i][j] = msg[i + j·N] (i.e.
   column-by-column: first 50 flag bits = column 0 of M), take 272 bits → flag.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Derived the group-exponent root from the provided generator source only.
- Did not attempt the (infeasible-looking) matrix DLP; not needed.

## artifacts [OBSERVED]
- code: debug1.py, solve.py
- data/logs: live_transcript_2026-10-15.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement: https://cryptohack.org/challenges/diffie-hellman/ (slug `matrix`)
- Files: `the_matrix.provided`, `flag.provided` (URLs in site.md)
- **NOT consulted:** /solutions/, /solves/, any external writeups.
