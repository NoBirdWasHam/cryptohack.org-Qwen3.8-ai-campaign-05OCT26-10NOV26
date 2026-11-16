---
record: agent-aar
puzzle: challenge-7-cryptohack-sigma-or-proof
category: zkp
url: https://cryptohack.org/challenges/sigma-or-proof/
status: solved
date: 2026-10-19
flag_ref: "FLAGS/zkp/challenge-7-cryptohack-sigma-or-proof/flag.txt"
flag_sha256: 3cfef71a5b8eb5fcc0897918315a87a243b9014ae05ea01edbec2e610fe27c45
skills: []
human_twin: AAR.md
---

# AGENT — 231-cryptohack-sigma-or-proof: OR Proof / Sigma Protocols (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved (3 phases, one connection)" [OBSERVED text; evidence tag applies to its source, not each claim]
The protocol is a textbook OR-proof (disjunction of two discrete-log relations
`g^w_i = y_i`, i=0,1) with verification `g^z_i == a_i · y_i^e_i (mod p)` and
`e0 ^ e1 == s` (integer XOR, challenges sampled in [0, 2^511)).

1. **Correctness — WE are the prover.** `chal.py` gives `w0` (so `g^w0 == y0`), `w1` redacted.
   Be honest on side 0: pick `r`, commit `a0 = g^r`. Simulate side 1: pick `z1`,
   `a1 = y1^{-e1} · g^{z1}`. After the verifier sends `s`, set `e0 = s ^ e1`,
   `z0 = r + e0·w0`. Accepted.
2. **Special soundness — WE are the verifier (extraction).** Server sends TWO transcripts
   with the SAME commitments `(a0,a1)` but different challenges `(e0,e1)` vs `(e0*,e1*)`.
   On whichever side `e_i != e_i*`, the witness is `w_i = (z_i − z_i*)·(e_i − e_i*)^{-1} mod q`.
   Verify `g^w == y_i` before returning it. (At least one side differs, since `s != s*`.) Accepted.
3. **SHVZK — WE simulate.** Given `s`, build a full accepting transcript for a fresh
   `(y0',y1')` with NO witness: pick `e0`, `z0`, set `a0 = y0'^{-e0}·g^{z0}`; `e1 = s^e0`,
   `z1`, `a1 = y1'^{-e1}·g^{z1}`. Accepted → flag.

## reusable-rules
- **OR-proof = honest-on-one-branch + simulate-the-other.** The redacted witness only
  matters on the branch you can't witness; commit to a *simulatable* value there.
- **Special soundness extraction** is the same `w=(z−z*)/(e−e*)` trick as sigma-protocol
  rewinding — it works on whichever branch's challenge changed.
- **SHVZK simulation** is the reverse of honest proof: pick the challenge/response first,
  back out the commitment as `a = y^{-e}·g^z`.
- **Raw-socket integer protocols: parse with regex grabs, not line splits**, when the
  server's prompts lack trailing newlines.
- One challenge can wear two slugs (current + CTF-archive twin) on the same server;
  the same flag satisfies both.

## anti-patterns / limits
The server's `input()` prompts (`a0:`, `a1:`, …) are **not newline-terminated**, so naive
line-splitting merges prompt+value into one token and the first `expect()` fails. Fix:
a streaming buffer + **regex grab** (`grab(r"...(\d+)")`) that accumulates until the pattern
matches and consumes only through the match. (`solve.py` failed this way; `solve2.py` is the
regex-grab version that succeeded.)

## artifacts [OBSERVED]
- code: params.py, solve2.py
- data/logs: raw_transcript.txt, run1.log, run_ok.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/zkp/
- **Challenge:** "OR Proof" (75 pts, slug `sigma-or-proof`)
- **Service:** `archive.cryptohack.org:11840` (raw socket, integer protocol)
- **Provided files:** `chal.py` (ships `w0`; `w1 = REDACTED`), `params.py` (p, q, g=2, y0, y1)
- **NOT consulted:** solutions page, search-engine writeups (no-cheat rule)
