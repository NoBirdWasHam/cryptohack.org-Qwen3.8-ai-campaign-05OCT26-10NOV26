---
record: agent-aar
puzzle: challenge-259-cryptohack-failproof_revenge-sekaictf202
category: ctf-archive
url: https://cryptohack.org/challenges/failproof_revenge-sekaictf202/
status: solved
date: 2026-11-06
flag_ref: "FLAGS/ctf-archive/challenge-41-cryptohack-failproof_revenge-sekaictf202/flag.txt"
flag_sha256: f9b0b844b98544bcdd0fd94b82610fc922eb64fec48cd753efbc15937c79c6f4
skills: [ctf-lattices]
human_twin: AAR.md
---

# AGENT — FaILProof Revenge (SekaiCTF 2022), CryptoHack slug `failproof_revenge-sekaictf202`
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Current state of the attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Three runs complete, all ending on the enumeration-cost wall at dim 249 (quantified above: BKZ-25 plateau spread 1.0875 vs the ~1.05 needed; run 2's raw GP wall was substantially GP-basis-quality, NOT intrinsic -- fplll LLL gives min||b*||^2 77.9 / spread 1.1057). Everything EXCEPT the final enumeration leg is built and verified: prep from live_output.txt, m0 verification for all blocks, exact integer target handling (raw-T0 Kannan embedding rows [(2K|0);(T0|1)], beta=1, solution norm^2 504-506), kernel recovery from the BKZ'd Kannan checkpoint, and the decode recipe (decode with ORIGINAL T0; m = m0 + (T0 - pt)/2; seg = bytes 24..31 with MSB weights 2^(7-k); flag = seg0..seg6, strip trailing NULs). Ready-to-replay inputs: revb0..b6.gp + runrev_b0..b6.gp (GP) or feed (K, m0p, c) straight into Sage; also solve10.py <bi>, run_all.py.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- GP: Mat(t_VEC) is a ROW -> column = Mat(v)~; MAT*t_VEC invalid, use MAT*t_MAT col; no
  listincludes/vecnorm; loop bodies need {} or single-statement apply(); write per-row Str(Vec(row)).
- fpylll: GSO.Mat(...).update_gso(); fplll module fns (lll_reduction/bkz_reduction(BKZParam));
  from_iterable; shortest_vector has no radius kwargs; enumeration wrapper lacks radius control via CVP.
- Flag provenance respected: derivation from live session only; no writeups searched.

---

# RUN#2 (2026-11-01): port 321's pure-PARI bounded-CVP pipeline

Strategy (from sibling 321 SOLVED same day): LLL-only Kannan + exact-Fraction Babai + qfminim
with CORRECT small bound (bounded CVP beats uSVP strength). Key re-read of the source:
each 64-byte block = rand24 || flag8 || rand32 — ONLY the 8 flag-byte MSBs are provably 0.
The run#1 variants b0 (crypto{) and b6 (tail zeros) were WRONG ASSUMPTIONS for this instance
(crypto{ prefix never appears — flag is SEKAI{; padding is zeros APPENDED TO FLAG, which then
sits mid-block, so no zero columns exist in the tail block either) — same trap class as 321's
prefix bug. Correct single setup for ALL blocks: keep 504 free bits (drop bytes 24..31 MSBs),
rhs = c raw. Kerdim 248, Kannan dim 249.

## artifacts [OBSERVED]
- code: A.gp, assemble3.py, c1adj.gp, chk_rev.py, clean_prep.py, cpsat_solve.py, cvecs.gp, engine3.py, engine3b.py, engine4.py, gen_rev.py, gen_rev2.py, gen_rev3.py, gp4.gp, kern2.gp, kern3.gp, kern3b.gp, measure.gp, measure2.gp, prep_gp.py, probe_a.py, probe_b.py, probe_bkz.py, probe_c.py, probe_d.py, real4.py, rev_K.gp, revb0.gp, revb1.gp, revb2.gp, revb3.gp, revb4.gp, revb5.gp, revb6.gp, run_all.py, runbot_b0.gp, runbot_b1.gp, runbot_b2.gp, runbot_b3.gp, runbot_b4.gp, runbot_b5.gp, runbot_b6.gp, runbot_toy0.gp, runbot_toy1.gp, runbot_toy2.gp, runbot_toy3.gp, runbot_toy4.gp, runbot_toy5.gp, runbot_toy6.gp, runrev_b0.gp, runrev_b1.gp, runrev_b2.gp, runrev_b3.gp, runrev_b4.gp, runrev_b5.gp, runrev_b6.gp, runrev_toy0.gp, runrev_toy1.gp, runrev_toy2.gp, runrev_toy3.gp, runrev_toy4.gp, runrev_toy5.gp, runrev_toy6.gp, snf06.gp, snf06b.gp, solve10.py, solve2.py, solve5.py, solve6.py, solve7.py, solve8.py, solve9.py, solve_bp.py, solve_bp2.py, solve_lattice.py, toy_b0.gp, toy_b1.gp, toy_b2.gp, toy_b3.gp, toy_b4.gp, toy_b5.gp, toy_b6.gp, toygate4.py
- data/logs: cpsat_segs.json, engine3.log, engine3b.log, engine4.log, flag_failproof_revenge-sekaictf202.txt, live_output.txt, rev_K.txt, rev_keep.txt, rev_m0_b0.txt, rev_m0_b6.txt, s10_b0.log, s6b_b0.log, s9_b0.log, solve2.log, solve3.log, toy_expect.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
All run artifacts in-folder: prep_gp.py, kern3.gp/Kred, snf06b.gp, chk_rev.py, clean_prep.py, gen_rev2/3.py, measure2.gp, engine3.py/engine3b.py, curve3.csv, engine3.log/engine3b.log, basis3_ckpt.json/kannan3_ckpt.json, rev_K/rev_m0_b*/revb*/runrev*, logs s6b/s9/s10_b0, toy_* files. Live listener (fresh-session derivation) + provided source.py only; flag provenance respected: nothing submitted, no flag recovered, no external solution consulted (stated in every run section); no external reference named in run logs.
