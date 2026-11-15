---
record: agent-aar
puzzle: challenge-313-cryptohack-import_numpy_as_mt-zh3r0_ctf
category: CTF Archive
url: https://cryptohack.org/challenges/import_numpy_as_mt-zh3r0_ctf/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-313-cryptohack-import_numpy_as_mt-zh3r0_ctf/flag.txt"
flag_sha256: 4e85a0a307958defca747f2c2ae5f135139cf39deab0d37e44da0496a74e6d13
skills: []
human_twin: AAR.md
---

# AGENT — import numpy as MT (Zh3r0 CTF V2), cryptohack slug `import_numpy_as_mt-zh3r0_ctf`
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
`challenge.py` seeds numpy's legacy `RandomState` (Mersenne Twister 19937) with a
**32-bit** seed (`random.seed(rand_32())`), then derives AES-CBC `iv,key` from
`random.bytes(16)` twice. The MT19937 stream is fully determined by the 32-bit seed,
and the iv is transmitted in the clear — so the seed (hence the key) is recoverable.
The author's "double encryption so people don't bruteforce it" only doubles the work:
each AES layer is peeled independently, outermost first.
Note `pad()` runs ONCE before the loop: round 2 encrypts `iv1||ct1` **unpadded**
(unpadding the outer plaintext is wrong — cost two debug cycles).

## reusable-rules
- numpy legacy `RandomState` ≠ CPython `random`: same MT19937 core, but `bytes()` is
  LE-per-word and the first output comes **after** an initial twist — untemper(word0)
  is NOT the seed directly; you must model the twist (or brute the recurrence).
- The init_genrand recurrence is a bijection chain: any post-twist word is a function
  of the 32-bit seed alone, turning "state recovery" into a cheap 2^32 scan with
  early-exit checks instead of 624-word untempering.
- Don't paste hex from truncated terminal previews into scripts — fetch to a file.

## anti-patterns / limits
- First live attempt timed out at 180 s (two sequential 2^32 scans in one foreground
  call); fixed by backgrounding / raising timeout.
- First captured ciphertext was truncated to 200 hex chars by a terminal-preview
  paste → CBC length error; fixed by writing socket output to `ct_hex.txt`
  programmatically and never pasting hex.
- Wasted two cycles on `unpad(outer_plaintext)` — the outer layer has no padding
  (pad-once-before-loop). The iv-regeneration assert passing while padding failed was
  the diagnostic clue.
- No attempt to invert the twist analytically (a 4-equation MITM might avoid the
  2^32 scan); brute force was fast enough (~100 s/layer).

## artifacts [OBSERVED]
- code: live_solve.py, live_solve2.py, solve.py
- data/logs: ct_hex.txt, flag_import_numpy_as_mt-zh3r0_ctf.txt, live_run.log, live_run2.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
not recorded in run logs (pre-discipline solve)
