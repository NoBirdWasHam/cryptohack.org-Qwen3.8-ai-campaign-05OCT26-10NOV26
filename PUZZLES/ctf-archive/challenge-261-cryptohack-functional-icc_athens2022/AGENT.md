---
record: agent-aar
puzzle: challenge-261-cryptohack-functional-icc_athens2022
category: ctf-archive
url: https://cryptohack.org/challenges/functional-icc_athens2022/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-261-cryptohack-functional-icc_athens2022/flag.txt"
flag_sha256: 42a5e39c6b94e50136635256d54be392923cf63a17df56df0dbbb73253949fd3
skills: []
human_twin: AAR.md
---

# AGENT — functional (ICC Athens 2022), CryptoHack slug `functional-icc_athens2022`
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
Not a cipher break -- a three-stage linear-recurrence reconstruction puzzle. Stage 1: the server prints only a 500-term window of a sequence f obeying an order-20 linear recurrence; Berlekamp-Massey recovers the recurrence and hence the hidden ITERS/state. Stage 2: the sequence i(n) is NEVER printed -- it must be computed from the g/h/i mutual recurrences via a companion-state matrix exponentiation. Stage 3: a digit-sum-initialized sequence j(n) with 100 delayed taps has to be evaluated at j(ITERS), whose value (hashed) is the AES key. Everything follows from linear-recurrence algebra: BM, 21x21 matrix exponentiation over F_p, and Bostan-Mori coefficient extraction on P/Q.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
Recorded root-cause failures (bugs killed, all with evidence): (1) old stage23.py regex-parsed a Stage-2 S3 list that is never in output.txt -- wrong by construction; (2) tap offsets off-by-one (used 9901..10000 vs correct 9900..9999; caught via (J*Q)==P and S*Q==0 residuals); (3) digit-sum single-digit bug -- ZZ(n).digits(1337) for n<1337 is 1-element, so S3[n//1337]=S3[0] silently corrupted every J[n<1337]; invisible at n=12345 (tap-tree bottom >= 2346), bites only at ITERS scale; symptom: mathematically 'proven' jt decrypting to junk; (4) gp64 quirks cost real time: Vec(t_POL)/Pol(list) are DESCENDING in this build (use Polrev; index Vec descending), no >>=, vector-as-index unsupported, vecextract 'o'/'e' matrix-only, multi-line while() loop bodies parse-fail in script files.
Cross-checks recorded: GP-BM vs fibonacci golden test, GP-BM vs python sequential at n=12345, mini_e2e.py full-structure test; AAR records ITERS, S3[:2], j(ITERS) matching the public soon-haari writeup values exactly (pre-existing claim preserved as written; ciphertext identical -- static archive instance).

## artifacts [OBSERVED]
- code: bm.gp, bm_data.gp, bm_test.gp, bmf.gp, bmr.gp, bmsmall.gp, bmt.gp, bmt10.gp, bmt11.gp, bmt12.gp, bmt13.gp, bmt2.gp, bmt3.gp, bmt4.gp, bmt5.gp, bmt6.gp, bmt7.gp, bmt8.gp, bmt9.gp, functional.sage, mini_e2e.py, p1.gp, stage23.py, stage2_s3.py, stage3_decrypt.py, stage3_prep.py, z1.gp, z2.gp, z3.gp, z4.gp, z5.gp
- data/logs: flag.json, output.txt, pq_full.json, s3.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided functional.sage + output.txt; own pipeline: stage2_s3.py (+s3.json), stage3_prep.py (+pq_full.json), bmr.gp/bmf.gp (bmr2.out = final jt), stage3_decrypt.py (+flag.json), mini_e2e.py. As recorded in the AAR itself: independent cross-check against soon-haari public writeup values (verification of self-derived quantities). Flag provenance: fully derived in-pipeline, no flag copy.
