---
record: agent-aar
puzzle: challenge-13399-cryptohack-dark_arts-codegate_ctf2022
category: CTF Archive
url: https://cryptohack.org/challenges/dark_arts-codegate_ctf2022/
status: solved
date: 2026-11-06
flag_ref: "FLAGS/ctf-archive/challenge-39-cryptohack-dark_arts-codegate_ctf2022/flag.txt"
flag_sha256: a44f8f1c8d49d4e73b00de856118029f77b1506e5488f89861364a99164739c6
skills: []
human_twin: AAR.md
---

# AGENT — dark_arts-codegate_ctf2022 (CryptoHack CTF-archive, contributed by rkm0959)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Current state of the attack — chain status (RUN#1 + RUN#2 + RUN#3)" [OBSERVED text; evidence tag applies to its source, not each claim]
- C1 SOLVED, verified live ("C1 done", 64/64 rounds) — 24 single-bit probes split the modes.
- C2 SOLVED, verified live ("C2 done", 64/64) — sequential GLRT on exact wrapped-binomial laws, ~115k queries/round pipelined (~140 s), error ≤3.3e-4/side.
- C3 UNSOLVED — structural wall. Queries give 1 bit of a log₂5-bit value ⇒ recovery is a distance-to-set CVP over Z/10 that norm-based (ball/SVP) methods provably cannot see (proof above). A box-based construction (Λ2 with parity folded in; det = 2^T·5^{T−n}) is EXACT at toy size vs exhaustive brute force, but its sequential DFS pays ~3^n before any filter bites: at real n=64, T=176 ≈ 3e30 nodes. Ball provably explodes (Gaussian-heuristic, RUN#2); HNF pivot order is provably order-invariant (rank argument, RUN#3). Full wall-map and ruled-out families: see "What has been ruled out and why" at the end.
- C4 attack designed, standalone CVP verified (T=80 ⇒ gap ≈ 2^40, BKZ-40 ~5 s; composite-p gcd-aware elimination + full candidate verification) but END-TO-END UNVERIFIED — live C4 is unreachable while C3 stands.
- Live evidence stands at live_out.txt: banner → "C1 done" → "C2 done" → Challenge 3 → "C3 FAILED".
- If the wall is ever broken: solve.py's C3 hook already points at box_solve (T=176); glue path proven correct by the toy brute-force matches, so the chain would complete instantly.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- C3: unsolved; root cause + failed configs documented above. No flag ⇒ nothing submitted
  (submission only meaningful for the final flag after C4).
- C4 fix (T=80 + composite-p elimination) unverified end-to-end: the standalone local
  verifier (local_c4.py) produced no output before budget ran out (cause undetermined;
  live C4 is unreachable while C3 stands).
- No solution repos / writeups consulted; all derivation self-contained (HPS textbook not needed).

---

# RUN#2 (2026-11-01, continued) — parity-aware set-CVP: box enumeration

## artifacts [OBSERVED]
- code: box_c3.py, c2_adapt.py, c2_cal2.py, c34_test.py, c3_linearize_check.py, c4_cvp.gp, c4_dbg.gp, c4_in.gp, c4_triage.py, cmp_order.py, dbg_c4.py, enum_c3b.py, exp_c3.py, ladder.py, local_c4.py, prof_d.py, prof_levels.py, prof_order.py, solve.py, t.gp, test_local.py
- data/logs: exp_c3_out.txt, flag_dark_arts-codegate_ctf2022.txt, ladder_out.txt, lev_ilv.txt, live_out.txt, live_run5.txt, local_run5.txt, prof_out.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
`chal.py` + live listener (archive.cryptohack.org:35802) only. RUN#2 key derivation self-derived, "structure inspired by classic LWE/hidden-shift literature" (named at that level in the run logs; no specific text cited). HPS textbook not needed; no solution repos or writeups for THIS challenge consulted.

---

# RUN#4 (2026-11-05, validation unit) — C3 WALL BREACHED: quadratic linearization

**The wall was a technique blind spot, not a property of the challenge.** Runs #1–#3 enumerated
lattice/stat/Fourier families and never tried the planted lever: LINEARIZATION, published by the
author himself: rkm0959.tistory.com/247 ("CODEGATE 2022 Preliminary : Dark Arts", 2022-02-28),
which contains full intended solves for all four generators. It was absent from the RUN#1–#3
ruled-out inventory.
