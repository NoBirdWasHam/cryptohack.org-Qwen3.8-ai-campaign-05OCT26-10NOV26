---
record: agent-aar
puzzle: challenge-285-cryptohack-rsa_permutation-wacon2022
category: ctf-archive
url: https://cryptohack.org/challenges/rsa_permutation-wacon2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-285-cryptohack-rsa_permutation-wacon2022/flag.txt"
flag_sha256: 3cedd85294809758cb56d4691cfac2f975eae92807da57182a1f8c190a1c7f66
skills: []
human_twin: AAR.md
---

# AGENT — rsa_permutation (WACON 2022), challenge-285 — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Core relations: `e·d_p = k_p·(p−1) + 1`, `e·d_q = k_q·(q−1) + 1`, with `k_p, k_q ∈ [1,292]`,
plus `p·q = n`. Unknowns: k_p, k_q, and the symbol map M (observed→true, a bijection on 16 digits).

**Digit-DP (LSB-first base-16 DFS)** over the three simultaneous multi-precision
identities, state = (position i, carry of n-multiplication, two split carries of the
`e·d − k·p` chains, partial injective map M, p0, q0):
- i=0: p0 odd with `p0·q0 ≡ n₀ mod 16`; q0 forced; `e·d_{p,0} ≡ 1−k_p+k_p·p₀ (mod 16)`
  fixes M[obs_p[0]] (13 = e⁻¹ mod 16), similarly for d_q.
- digit i: branch on true digit `pᵢ` (16 choices); `qᵢ` is then uniquely forced by the
  `p·q = n` digit equation (p0 odd ⇒ invertible mod 16); the d_p/d_q equations then
  uniquely force the required true digits `d_{p,i}, d_{q,i}`, which must be consistent
  with M or extend it injectively. Two forced constraints per branch ⇒ the DFS
  collapses to ~1.1k nodes per (k_p,k_q) pair; full 292×292 scan ≈ 99M nodes ≈ **10–40 s**
  in C (`dp4.exe`).
- Leaf: exact big-int check of `e·d_p = k_p(p−1)+1`, same for q, and `p·q = n`; prints p.

Send `u = p`, `v = n//p` → server prints the flag.

Key numbers (live session): PoW answer found in 1–6 s (multiprocessing, 2²⁴ tries expected);
DP scan 1.6–38 s; well inside alarm(300).

## reusable-rules
- "Permutation of hex digits" on d_p/d_q + n is a **digit-DP problem**: two forced-digit
  equations plus the multiplication collapse the search to ~1k nodes per (k_p,k_q);
  the flag's Heninger–Shacham pun is the hint that factorization from d-like leakage is the theme.
- Parse structured solver output with anchored patterns (`\np=`); `kp=85` poisoned a live session.
- If a solver scans the full parameter space and finds nothing on a **ground-truthed**
  instance, suspect the solver — targeted test at the known-correct parameters is the
  cheapest soundness check (this is exactly what exposed the dp5 regression).

## anti-patterns / limits
1. **`dp5.exe` (child's last scanner) is broken**: targeted run at the *correct*
   (k_p,k_q)=(259,49) on the local instance explores only 1459 nodes and finds nothing,
   although the ground-truth solution must satisfy its constraints — unsound pruning was
   introduced in dp5. `dp4.exe` solves the same input. The pre-existing `full.log`/`prog.log`
   "done" with no solution was a dp5-era full scan (identical node counts to my dp5-class
   runs); the "scan exhausted, no answer" conclusion inherited from the child was **wrong**.
   Do not resume/extend dp5.
2. **First live session returned "fail"** because the client parsed the DP output with
   regex `p=([0-9a-f]+)`, which matched the `kp=85` on the SOLUTION line and sent 133.
   The correct factor was in the same log (`\np=` fix → solved on retry).
3. No Sage/fpylll needed; pure integer digit DP.

## artifacts [OBSERVED]
- code: local_gen.py, solve_live.py, solve_live2.py
- data/logs: flag_raw.txt, flag_rsa_permutation-wacon2022.txt, found.txt, full.log, full4.log, live_dp.log, live_run.log, local_instance.json, local_instance.txt, prog.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
chal.py (matches live behavior) + the live listener only; flag was handed by the service after our own factorization was accepted. No third-party solution/writeup consulted (per AAR). Mathematics: elementary modular arithmetic + carry-tracking digit DP; the e=293 small-multiplier range follows from gcd(e, p−1)=gcd(e, q−1)=1 with strong 1024-bit primes.
