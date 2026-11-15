---
record: agent-aar
puzzle: challenge-112-cryptohack-double_and_broken
category: ecc
url: https://cryptohack.org/challenges/double_and_broken/
status: solved
date: 2026-10-14
flag_ref: "FLAGS/ecc/challenge-23-cryptohack-double_and_broken/flag.txt"
flag_sha256: d60e927fcebf51c827b769c23396eed0f778f08809ae71f4a6d536323c642c98
skills: []
human_twin: AAR.md
---

# AGENT — Double and Broken (double_and_broken, 60 pts, ECC)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Scalar-multiplication side channel on secp256k1. The server's `double_and_add(G, d)`
returns, alongside Q, a `leak` trace per run; 50 traces (359 entries each) are provided
(`collected_data.txt`). Crucially, the private scalar IS the flag: `d =
bytes_to_long(FLAG)` (see `source_snippet.py`). The per-step leak values (151 distinct,
ASCII-range) encode the double/add decisions driven by the bits of d, so the traces
reconstruct d bit-by-bit and the flag is `long_to_bytes(d)`.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Bit-recovery script and the `ecc_side_channel` module not archived: the recovery cannot be re-run offline from the remaining artifacts (re-derivation would need that module). (Stated in "Verification" above; carried here as the run's main limitation.)
- Beyond that: no failed mathematical paths logged (2026-10-14 session notes begin at the successful recovery).

## artifacts [OBSERVED]
- code: source_snippet.py
- data/logs: collected_data.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided files only: `source_snippet.py` (server snippet establishing d = bytes_to_long(FLAG)) and `collected_data.txt` (50 leak traces). Self-derived per logs; no textbook or third-party reference cited in the original AAR; no writeups/solutions consulted.
