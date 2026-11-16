---
record: agent-aar
puzzle: challenge-4-cryptohack-origami-nns_ctf_20252025
category: ctf-archive
url: https://cryptohack.org/challenges/origami-nns_ctf_20252025/
status: solved
date: 2026-11-08
flag_ref: "FLAGS/ctf-archive/challenge-4-cryptohack-origami-nns_ctf_20252025/flag.txt"
flag_sha256: 3990a0d1733e20fc7f02ef297aa99231673858965110a7ee50ff757448d1bf12
skills: []
human_twin: AAR.md
---

# AGENT — Origami (NNS CTF 2025), cryptohack slug `origami-nns_ctf_20252025`
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Method-provenance annotation (owner ruling 2026-11-07; REQUIRED annotation added 2026-11-08 per external audit)" [OBSERVED text; evidence tag applies to its source, not each claim]
Attack-FAMILY direction was supplied by the owner in the 11-07 ruling (PROVENANCE_2026-11-07.md:
"NTRU key recovery — Lambda_q^h uSVP, Atamagorodov-Coster folding, May/Silverman projection,
Howgrave-Graham hybrid, dense-sublattice / overstretched, subfield attacks, symplectic structure,
CVP formulations"). Per that ruling this is NOT contamination: the directions name published attack
families from the general cryptanalysis literature, not this instance's writeup content, and no
per-challenge solution details were provided. Everything downstream — implementation, parameter
choice, the final k=3 symmetric ring-fold construction, the parity-recovery finisher, and the flag —
was independently executed and re-derived on synthetic instances before the real one, from
service-given data. Classification per campaign taxonomy: SELF_DERIVED_METHOD with OWNER-DIRECTED
family guidance, per the ruling's mandated "Honest annotation" clause.

## reusable-rules
- gp 2.17 on Windows: statements must be SINGLE-LINE (multi-line for() bodies
  are parse errors); `lll`→`qflll`; `clock()`→`gettime()`; no `transpose` → `M~`;
  NO `flush` function; `random(a,b)` invalid — `random(n)` = [0,n).
- `qflll(X,3)` reduces COLUMNS of X. My first matrices reduced the trivial
  column-lattice {(a,b): q|b} — membership-test any candidate (b ≡ a·h mod q)!
- p=2 NTRU: try the no-wrap parity decryption first.
- Silent background deaths here were (a) 3 zombie gp64 × 3.2 GB → 0xC0000142
  init failures, (b) genuine stack overflow in fplll enumeration. Use
  `tasklist | grep -a`, powershell Get-Process counts, and
  Get-WinEvent 'Application Error' for the exception code.

## anti-patterns / limits
- No flag this session; nothing submitted. No writeups/solution files consulted.
- Failed: fpylll BKZ-40/25/20 @1024 (stack crash ×3), fpylll LLL @1024 (>7 min,
  killed under memory pressure), PARI exact LLL (reach), first three scramble
  scripts (gp syntax/column/flush bugs), python-flint, micromamba fpylll/sage.
- Math fully worked and unit-verified; only the BKZ execution is missing
  (minutes on Linux).

## artifacts [OBSERVED]
- code: chain60_dd.sh, chain60b_dd.sh, chain_dd.sh, dec.py, dec2.py, fixdec.py, flush.gp, fplllpipe.py, lll.gp, lll2.gp, lll3.gp, lll4.gp, lll5.gp, mattest.py, mattest2.py, mini.gp, mini2.gp, mini3.gp, mk_real_fplll.py, mt.gp, p1.gp, p2.gp, p3.gp, p4.gp, p5.gp, p6.gp, p7.gp, p8.gp, p9.gp, pA.gp, pB.gp, paritytest.py, paritytest2.py, pk.gp, pkv128.gp, probe.py, probe10.py, probe11.py, probe12.py, probe_fpy_t280.py, probebkz.py, probebkz2.py, pt.gp, pt2.gp, pt_h.gp, run_bkz.sh, run_cli_toy.py, scan_cli.py, scram.gp, scram2.gp, scram3.gp, scram4.gp, scram5.gp, selftest.py, solo.gp, solo2.gp, solo3.gp, solo4.gp, solo5.gp, solo6.gp, solo6b.gp, solo7.gp, solo8.gp, solve.py, solve2.py, solve3.py, solve5.py, solve6.py, solve7.py, solve8.py, t280_bench.sh, t280_chain70p_dd.sh, t280_ctl_mk.py, t280_ctlrun.sh, t280_fin2.py, t280_fold.py, t280_fold2toycli.py, t280_fold_mk.py, t280_fold_toy.py, t280_foldchain.sh, t280_foldscan.py, t280_foldtoycli.py, t280_fpy_probe.sh, t280_gen_mid.py, t280_gluecheck.py, t280_mk_noprune.py, t280_real3.py, t280_run2tag.sh, t280_watch.py, toy512_run.py, toy_decrypt_check.py, toy_ntrugen.py
- data/logs: FLAG_FOUND.txt, REAL_FPP_RECOVERED.txt, err60c_1.txt, gtoy60.json, output.txt, probe_fpy_rc.txt, run8.log, run_bkz.log, run_bkz2.log, solo6.log, solo7.log, solve.log, solve2.log, solve2b.log, solve3.log, solve5.log, solve6.log, t280_bench_b40.txt, t280_bench_results.txt, t280_cvp_math.txt, t280_fold_profiles.json, toy64_truth.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.

---
