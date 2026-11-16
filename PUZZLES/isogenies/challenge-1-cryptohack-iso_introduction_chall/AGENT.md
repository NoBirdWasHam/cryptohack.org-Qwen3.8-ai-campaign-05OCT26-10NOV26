---
record: agent-aar
puzzle: challenge-1-cryptohack-iso_introduction_chall
category: isogenies
url: https://cryptohack.org/challenges/iso_introduction_chall/
status: solved
date: 2026-10-12
flag_ref: "FLAGS/isogenies/challenge-1-cryptohack-iso_introduction_chall/flag.txt"
flag_sha256: 018e914ceb5838afa60e91525610af43f4e9480763468b507e75f2a6a41ff84d
skills: [ctf-answer-challenges]
human_twin: AAR.md
---

# AGENT — Introduction to Isogenies (iso_introduction_chall)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "How it was solved" [OBSERVED text; evidence tag applies to its source, not each claim]
1. Read the section intro. The question: *"what would the size of a kernel be for a
   separable isogeny of degree 65537?"*
2. The text defines separable isogenies earlier: *"the degree of the map is exactly
   equal to the size of the kernel."*
3. Therefore kernel size = degree = **65537**.
4. Submitted the bare number via `submit_flag.py iso_introduction_chall 65537`.

No computation needed — this is a reading-comprehension check on the definition.

## reusable-rules
- For a **separable** isogeny, deg(φ) = #ker(φ) exactly. (For a *non*-separable /
  inseparable isogeny in char p, the degree = [ker size] · p^e where e is the
  inseparability exponent — the "size of the kernel" as a scheme is p^e times the
  geometric kernel.) The challenge tests that you can find the definition and apply it.
- Answer-type challenges want the **bare value** (see `ctf-answer-challenges`).

## anti-patterns / limits
- Did: read the provided statement, applied its own definition, submitted the flag.
- Did not: use any external writeup or the solutions page.

## artifacts [OBSERVED]
- code: none in dir
- data/logs: none
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement page: https://cryptohack.org/challenges/isogenies/ (the section intro; this
  challenge is the "wall of text" itself — the answer lives in its final paragraph).
- No provided files. No `/solutions/`, `/solves/`, or search-engine writeups consulted.
