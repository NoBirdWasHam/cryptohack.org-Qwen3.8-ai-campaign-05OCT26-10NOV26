---
record: agent-aar
puzzle: challenge-13-cryptohack-hyper512-hitcon_ctf2024
category: ctf-archive
url: https://cryptohack.org/challenges/hyper512-hitcon_ctf2024/
status: solved
date: 2026-11-06
flag_ref: "FLAGS/ctf-archive/challenge-13-cryptohack-hyper512-hitcon_ctf2024/flag.txt"
flag_sha256: adeee0a94b1c41df8801bf1351f3b41cf1a293fb18b8929df43aa59a326ed9ec
skills: []
human_twin: AAR.md
---

# AGENT — hyper512-hitcon_ctf2024 (CryptoHack #267)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack chosen" [OBSERVED text; evidence tag applies to its source, not each claim]
Over-determined CryptoMiniSat 5.17 (venv pycryptosat) with native XOR clauses for the LFSR
recurrences + minimal Tseitin (4 AND + 3 XOR per keystream bit), correct ANF above.
All gift bits used (N selectable); incremental exclusion-clause loop: each SAT model is
checked against the FULL gift; spurious models excluded by a 512-literal clause, list
checkpointed to excl_N.json so a killed run resumes.
solve2.py implements this; self-test path uses a self-generated instance with a known key
(output_test.txt / key_test.txt) to validate the encoding end-to-end.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: author_solve.py, solve.py, solve2.py, solve3.py, solve4.py, solve5.py, solve6.py, solve7.py, validation_scaled_20261105.py
- data/logs: flag_hyper512-hitcon_ctf2024.txt, key_test.txt, output.txt, output_live.txt, output_test.txt, selftest.log, smoke6.log, smoke6b.log, solve5_real_n8192.log, solve6_live.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
chall.py (MASK taps / combiner), output.txt, self-generated self-test instance; own solve2.py, selftest.log. All algebra (ANF, Walsh spectrum, irreducibility) self-computed per run logs; no external reference named in run logs; no writeups/solutions consulted.
