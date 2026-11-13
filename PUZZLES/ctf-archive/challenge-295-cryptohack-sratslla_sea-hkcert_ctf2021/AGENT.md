---
record: agent-aar
puzzle: challenge-295-cryptohack-sratslla_sea-hkcert_ctf2021
category: ctf-archive
url: https://cryptohack.org/challenges/sratslla_sea-hkcert_ctf2021/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-295-cryptohack-sratslla_sea-hkcert_ctf2021/flag.txt"
flag_sha256: 90c6dafa63b77c6fae799f717cee601311517a955c824583f2bfc6a8d6b3af8d
skills: []
human_twin: AAR.md
---

# AGENT — sratslla_sea-hkcert_ctf2021 ("Sratslla SEA", HKCERT CTF 2021)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How the partial recovery follows (attack mechanism)" [OBSERVED text; evidence tag applies to its source, not each claim]
1. `ark` mode no-ops every AddRoundKey (incl. the final one) ⇒ a public permutation; locally
   inverting the `ark secret` reply through the keyless round structure exposes schedule word w0
   ⇒ k0..k3 = 1b807af1.
2. `sb` mode no-ops SubBytes ⇒ every round is GF(2)-affine with a PUBLIC linear part (SR and MC are
   GF(2)-linear; the key only contributes a constant). Measuring E(x)⊕E(0) on unit vectors builds the
   128×128 matrix M; solving M·x = (sb secret ⊕ sb zero) over GF(2) gives w1 ⇒ k4..k7 = 13d3e047.
3. mc/sr stages: key-schedule coupling (w6 = w2⊕w5, w7 = w3⊕w6, RotWord drift) spreads every unknown
   byte into every output byte — probes confirm changing any of k8..k15 changes all 16 output bytes;
   the remaining 64 bits stayed unsolved in THIS session (z3 bit-blast timed out; the fast "sat" was
   an unsound QF_BV artifact, documented above).

Corpus note (batch #11, append-only; claims above untouched): this folder records the EARLY PARTIAL
attempt (8/16 key bytes, no flag). The canonical solve for `sratslla_sea-hkcert_ctf2021` lives in the
sibling misspelled folder `challenge-295-cryptohack-srateslla_sea-hkcert_ctf2021/AAR.md` (Run #3:
4-stage single-session attack, full key + flag, flag.txt archived). The ledger credits the slug ONCE
(nn 295, SOLVED) — that credit is the sibling folder's work, not this folder's.

## reusable-rules
1. **ark mode is keyless** (every ARK, incl. final, no-oped ⇒ public permutation).
   Inverting it locally on `ark secret` ciphertext yields slice 0 ⇒ **k0..k3 = 1b807af1**.
   Verified: ark enc identical under two random keys (probe.py).
2. **sb mode is GF(2)-affine** (SB off ⇒ rounds are SR∘MC∘XOR; linear part M is public,
   key only shifts a constant). `E(x)⊕E(0)` measured via `sb data 00*16`; M built from unit
   vectors, GF(2) 128×128 solve gives slice 1 ⇒ **k4..k7 = 13d3e047**. Affineness verified
   empirically (xor3-identity holds against E(0)).
3. Collected full probe set (7 queries): ark_sec, sb_zero, sb_sec, mc_zero, mc_sec,
   sr_zero, sr_sec + flag ciphertext (collect.json). All stage slices show the exact
   repeated-column structure predicted — server matches provided aes.py on ark path.

## anti-patterns / limits
- **z3 bit-blasted model** (sound: verified exact vs pure-python AES with key pinned —
  diag.py SAT, outputs identical). Search through 10 S-box layers over the free 64 bits is
  not tractable: full constraint set → `unknown` (timeout 240 s and 400 s runs);
  `mc_zero`-only → still `unknown` at 300 s (diag3). A quick "sat" in 6 s under
  `SolverFor('QF_BV')` with S-box arrays was an artifact (Selects uninterpreted ⇒ unsound
  model; candidate key fails every stage check — documented so nobody reuses it).
- Planned but out of budget: GF(2^8) F4/Groebner formulation of the σ-atom system
  (σ_r,m = S(affine in σ_{<r}, x, y)) — z3's ff tactic API not exposed in this build.

## artifacts [OBSERVED]
- code: aes.py, collect.py, diag.py, diag2.py, diag3.py, probe.py, solve12.py, solve34.py, solve34b.py
- data/logs: collect.json, partial.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
