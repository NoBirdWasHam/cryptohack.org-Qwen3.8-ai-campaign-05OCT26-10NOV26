---
record: agent-aar
puzzle: challenge-266-cryptohack-hide_and_seek-ecsc_2023_norwa
category: ctf-archive
url: https://cryptohack.org/challenges/hide_and_seek-ecsc_2023_norwa/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-23-cryptohack-hide_and_seek-ecsc_2023_norwa/flag.txt"
flag_sha256: 3a73d9f153625599e18e7865eaace776f9386e4e24898c1bd45026fb126a6667
skills: []
human_twin: AAR.md
---

# AGENT — hide_and_seek (ECSC 2023 Norway) / cryptohack slug `hide_and_seek-ecsc_2023_norwa`
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Curve order is smooth: `#E(F_p) = p+1-t` with `t = ellap` from PARI factors into 9 distinct primes of ~34 bits (`nn_ok=1` verified in PARI). So ECDLP on this curve is trivially solvable by Pohlig–Hellman + BSGS, once you can reduce the given oracle tuples to a bare `X = x·P` DLP instance.

## reusable-rules
- "Hidden value" framing (Q = x·P) is a red herring for lattices here — two-tuple elimination `b_i R_j − b_j R_i` kills the unknown multiplier of P using only known scalars (2D kernel of [[a_i,b_i],[a_j,b_j]] trick).
- Always run `ellap` + `factor` on the group order for EC challenges: squarefree smooth order ⇒ Pohlig–Hellman regardless of how the DLP instance was dressed up.

## anti-patterns / limits
- First plain-python BSGS attempt killed at ~27 min (too slow per-step `pow(x,-1,p)`); PARI `elladd` legacy API ~25 min/factor, killed after 1 of 9 factors. gmpy2 BSGS solved it in ~2 min.
- GP gotchas found the hard way: F_p curves via `ellinit`+Mod use the old API where **infinity is `[0]`** (`elladd` rejects `[]`); multi-statement `if` bodies need `{}`, but `{}` inside call args ("embedded braces") is rejected by the parser.
- No solutions/writeups consulted; no flag value retrieved from any artifact (flag only from own derivation, cross-checked against own second implementation).

## artifacts [OBSERVED]
- code: data.gp, dbg.gp, dbg2.gp, dbg3.gp, hide_and_seek.sage, ord.gp, ord2.gp, probe.gp, probe2.gp, run3.gp, solve.gp, solve.py, solve2.gp, solve3.gp, solve4.gp, solve5.gp, solve_fast.py, solve_rho.py, t.gp, t2.gp, t3.gp, t4.gp, t5.gp, t6.gp
- data/logs: flag_hide_and_seek-ecsc_2023_norwa.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
