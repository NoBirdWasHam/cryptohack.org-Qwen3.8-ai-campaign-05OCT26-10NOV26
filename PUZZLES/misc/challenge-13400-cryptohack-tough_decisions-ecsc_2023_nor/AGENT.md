---
record: agent-aar
puzzle: challenge-13400-cryptohack-tough_decisions-ecsc_2023_nor
category: misc
url: https://cryptohack.org/challenges/tough_decisions-ecsc_2023_nor/
status: solved
date: 2026-10-30
flag_ref: "FLAGS/ctf-archive/challenge-13400-cryptohack-tough_decisions-ecsc_2023_nor/flag.txt"
flag_sha256: cc3e78cfcf129dcb538372961d519210ecdf8f0dcf609f8d0ad3146d44dec77c
skills: []
human_twin: AAR.md
---

# AGENT — tough_decisions (ECSC 2023 Norway, ctf-archive)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
LWE samples `(a, a·s + e mod 256)` vs uniform `(a, uniform)`, key = 16 bytes, 6 samples
per flag bit. The "PRNG" noise `sample_noise(7)` builds
`e = ((...((b1)|<<1)...)) = 2*(64b1+32b2+...+b7)` — i.e. **e is always even**.
So for real samples, `LSB(b) = LSB(a·s)` deterministically (the higher bits of e are
uniform mod 128, so parity is the *only* leak, and it's a perfect one).
Key gotcha: `[[real, fake][b](s)]` indexes with `b`, so **bit=0 → real**, bit=1 → fake.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- First decode attempt inverted real/fake and produced garbage that *didn't* fit the
  assumed `crypto{` prefix — this challenge's flag prefix is `ECSC{`, and the index
  list `[real, fake][b]` means 0→real. Validate hypotheses with a prefix-fit scan
  (dbg1.py fits both labelings over 2^16 masks against a candidate prefix) rather
  than assuming `crypto{`.
- A GF(2) mask indexes the **per-byte LSB vector**, not the raw byte string — ANDing
  the mask against the 16-byte integer is wrong (bit j of mask must gate `a_j & 1`).

## artifacts [OBSERVED]
- code: dbg1.py, solve.py, solve2.py, tough_decisions.py
- data/logs: flag_tough_decisions-ecsc_2023_nor.txt, output.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
