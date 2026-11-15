---
record: agent-aar
puzzle: challenge-247-cryptohack-blind-ecsc_2023_norway2023
category: ctf-archive
url: https://cryptohack.org/challenges/authenticator-firebird_intern/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-21-cryptohack-blind-ecsc_2023_norway2023/flag.txt"
flag_sha256: d17d8b10ffd3e187be2c99753d623dcdf1cdc061236fcd7505e3db2badf6bed6
skills: []
human_twin: AAR.md
---

# AGENT — blind (ECSC 2023 Norway) — challenge-247
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
The masking only hides m *inside* the signature — verification still pins R:
R = z·G + c·Y = ω·G, so m1' = r ⊕ x(R) must equal the mask structure. For any m1'
candidate, m = F2(m1'[:40]) ⊕ m1'[40:56] is forced, and the 320-bit test
m1'[:40] == F1(m) holds w.p. 1 for the real sig and ≈2^-320 for random ones.
Scan all 10000 sigs → exactly one hit (index 7135) → _k = 078ca69012d65278484caaacc28ebe4f
→ bcrypt.kdf → AES-CTR(nonce=b"") decrypt → flag. Pure offline; no listener used.

## reusable-rules
- "Message blinding" with a *keyed-by-message* mask is not blind: the signature
  equation is still verifiable once you invert the mask's own definition.
- Flag the design flaw vs my bugs by testing group axioms first: G on curve,
  ORDER·G = O, Edwards↔Weierstrass round-trip.

## anti-patterns / limits
- First scan run: 0 hits. Root cause was MY typo: Ed448 d constant transcribed with
  2 extra hex digits (114 vs 112). Diagnosed by comparing A/B and to_w(G) against an
  independent pure-int computation; fixed, then solved. No crypto difficulty, no
  timeouts; archive file links (cryptohack.org/static/challenges/...) downloaded fine.

## artifacts [OBSERVED]
- code: blind.sage, solve.py
- data/logs: flag_blind-ecsc_2023_norway2023.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
