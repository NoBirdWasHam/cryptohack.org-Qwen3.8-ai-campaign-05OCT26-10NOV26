---
record: agent-aar
puzzle: challenge-68-cryptohack-tenet_the_plagarism-hkcert_ct
category: ctf-archive
url: https://cryptohack.org/challenges/tenet_the_plagarism-hkcert_ct/
status: solved
date: 2026-11-06
flag_ref: "FLAGS/ctf-archive/challenge-68-cryptohack-tenet_the_plagarism-hkcert_ct/flag.txt"
flag_sha256: c034bf214c456fa1f0d920853568d81742612daf353c7c8366c6a0617a80b518
skills: []
human_twin: AAR.md
---

# AGENT — tenet_the_plagarism-hkcert_ct (CryptoHack ctf-archive, nn=298)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attacks attempted / analyzed, with bounds" [OBSERVED text; evidence tag applies to its source, not each claim]
1. **Ordered 8+8 MITM** over slots: 256^8 = 2^64 per side — infeasible.
2. **Parity-subset MITM (best known self-derivable attack).** Split S (weight ≤16) into two
   weight-≤8 halves from 256 items: C(256,8) = 2^50.0 entries/side, Schroeppel–Shamir space
   2^25.4; matching on block 0 (128-bit target) then filtering with block-1 prefix (80 bits) +
   byte 61 gives E[false] ≈ 2^{100-128} < 0 — i.e. **unique candidate, algorithm correct**
   (toy version with 16-byte alphabet returns exactly 1 candidate = true subset, `probe.py`),
   but **time ≈ 2^50 subset sums ≈ 10^15 AES-block XORs — weeks-to-months of machine time and
   effectively unbounded external sort**. Declined; not run.
3. **Wagner generalized birthday:** needs list size ≥ 2^{128/(1+log2 k)}; with the parity
   collapse the smallest lists (all subsets of k/4 slots, 2^23.4 at 4 slots) still need
   2^{42.7} (k=4) — condition fails; with raw 256-item lists it fails worse. No.
4. **ISD framing (Prange/Lee-Brickell/Stern, syndrome decoding of 256 vectors in GF(2)^128 at
   weight ≤16):** weight is far below δn, so ISD degenerates to the C(256,8) MITM — no gain.
5. **AES single-byte-key structure:** every round key byte of AES_{b||0^15} is one of
   {const, b⊕const, sbox(b⊕const), ...} — 44 nested-sbox bytes; gives 256 related keys but no
   linear relation among v(b) usable for a weight-16 XOR-sum; AES internals (Sbox) kill any
   GF(2)-linear shortcut. No practical distinguisher-based speedup for this search.
6. **Oracle routes:** none — ctf-archive is offline (no listener on the card), no decrypt API.

## reusable-rules
- CTR chaining = keystream XOR; chained single-byte AES instances whose keys share the same
  **shape** collapse the space to parity subsets (duplicates cancel) — always check the actual
  key layout (`key[i:i+1] + zeros` put every byte in position 0 here).
- Cancellation reduces 2^128 → ~2^83 (search floor 2^50) — a real break *conceptually*, but the
  residual 2^50 is still CTF-solo-infeasible, which is why the historical solves were OSINT.

## anti-patterns / limits
- Not run: the ~2^50 parity-subset MITM (would need a compute cluster + disk sort; documented
  bounds above, toy-validated algorithm in `probe.py`). If such tooling existed, this challenge
  becomes feasible at ~2^50 with UNIQUE candidate (no regex needed even).
- Did not consult cryptohack solutions/solves pages, the author's blog post, or any third-party
  writeup (provenance rule); the leak location (author blog post linked from the card, containing
  original-flag discussion) is recorded here without values.
- Assumed the 216-bit known-plaintext (prefix + '}') is correct; the given ciphertext length (62 B)
  is consistent, and self-generated ciphertexts validate the attack model end-to-end.

## artifacts [OBSERVED]
- code: probe.py, solve.py
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only; the AAR names the historical third-party solve route (author blog post) and records it was NOT opened. Disclosure wording preserved verbatim:
> The statement's own hint (author blog post "interesting flag
> submissions — OSINT master", linked in the challenge card) is the historical solve route:
> the original HKCERT flag value circulating among teams. **That route is exactly what the
> provenance rule forbids** (answer from web/author writeup), and it was NOT opened.
> Did not consult cryptohack solutions/solves pages, the author's blog post, or any third-party
>   writeup (provenance rule); the leak location (author blog post linked from the card, containing
>   original-flag discussion) is recorded here without values.
