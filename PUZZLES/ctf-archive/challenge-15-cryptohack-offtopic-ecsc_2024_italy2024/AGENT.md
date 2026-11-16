---
record: agent-aar
puzzle: challenge-15-cryptohack-offtopic-ecsc_2024_italy2024
category: ctf-archive
url: https://cryptohack.org/challenges/offtopic-ecsc_2024_italy2024/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-15-cryptohack-offtopic-ecsc_2024_italy2024/flag.txt"
flag_sha256: 6b76b64c9124d066e4bcd4379e43643f0941f7236f821d0f31f8616f0fc24a11
skills: []
human_twin: AAR.md
---

# AGENT — OffTopic (ECSC 2024 Italy), CryptoHack ctf-archive
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability (malicious receiver, first principles from the source)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `H` is attacker-chosen. Send `H = O` (point at infinity, `(0,0)`).
   `assert H != G` passes, and pycryptodome's `EccPoint(0,0)` is the identity.
2. Every re-randomization term is `r*H` → with `H = O` all noise in the S
   component collapses to zero: `from_pt(m).S = mG`, `rand.S = 0`.
3. Our ciphertext needs no validity check either: pick `C.S = K·G` with `K = 10^9`
   (a "ciphertext" of unknown r, which the server never verifies).
   Then exactly: `res.S = (m0·(1−K) + m1·K)·G` — noise-free (the R component
   keeps its `rG` noise and is useless, but R is not needed).
4. On digits [0,9]² the map `(m0,m1) ↦ m0 + K·(m1−m0) mod q` is injective
   (`|K·(m1−m0)| ≤ 9K ≪ q`, distinct pairs give distinct integers). Recovery =
   a precomputed 100-entry table (100 EC scalings, done once).
So one round leaks BOTH messages: OT's 1-out-of-2 choice property is broken —
soundness relies on the receiver not controlling `H`, and on S-noise, neither of
which is enforced. (The statement's joke: with a fully-homomorphic scheme that
mangles re-randomization, "FHE ⇒ OT" loses the obliviousness/soundness.)

## reusable-rules
- Malicious receiver + identity public key: whenever a scheme's re-randomization
  or blinding term is `r·H` and `H` is receiver-supplied, test `H = O` FIRST —
  it is the canonical way to strip all additive noise in one move.
- "Encrypt a bit" servers that never validate that the ciphertext is a valid
  encryption let you feed any pair of points; only the component the server
  reads (here S) must be on the curve.
- Encoding two small unknowns in one group element: pick a base K > digit range
  so a single linear combination `m0 + K·(m1−m0)` is injective — a digit-CRT.

## anti-patterns / limits
- Local subprocess test harness (`solve.py --local`, `--local-sock`) died on
  Windows pipe/text-mode quirks (OSError errno 22 on flush; buffering). Abandoned
  in favor of the in-process sim — protocol math was the real risk, not plumbing.
- `solve.py`'s local path is kept for reference but `sim_test.py` + `solve_live.py`
  are the runnable artifacts.
- First live attempt crashed at round 1 JSON parsing: server prints the next
  round's prompt on the same line as the res JSON; fixed by extracting the
  `{...}` substring (live build otherwise byte-matched the file).

## artifacts [OBSERVED]
- code: offtopic.py, sim_test.py, solve.py, solve_live.py
- data/logs: flag_offtopic-ecsc_2024_italy2024.txt, live_out.log, run3.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
1. `H` is attacker-chosen. Send `H = O` (point at infinity, `(0,0)`).
   `assert H != G` passes, and pycryptodome's `EccPoint(0,0)` is the identity.
2. Every re-randomization term is `r*H` → with `H = O` all noise in the S
   component collapses to zero: `from_pt(m).S = mG`, `rand.S = 0`.
3. Our ciphertext needs no validity check either: pick `C.S = K·G` with `K = 10^9`
   (a "ciphertext" of unknown r, which the server never verifies).
   Then exactly: `res.S = (m0·(1−K) + m1·K)·G` — noise-free (the R component
   keeps its `rG` noise and is useless, but R is not needed).
4. On digits [0,9]² the map `(m0,m1) ↦ m0 + K·(m1−m0) mod q` is injective
   (`|K·(m1−m0)| ≤ 9K ≪ q`, distinct pairs give distinct integers). Recovery =
   a precomputed 100-entry table (100 EC scalings, done once).
So one round leaks BOTH messages: OT's 1-out-of-2 choice property is broken —
soundness relies on the receiver not controlling `H`, and on S-noise, neither of
which is enforced. (The statement's joke: with a fully-homomorphic scheme that
mangles re-randomization, "FHE ⇒ OT" loses the obliviousness/soundness.)
