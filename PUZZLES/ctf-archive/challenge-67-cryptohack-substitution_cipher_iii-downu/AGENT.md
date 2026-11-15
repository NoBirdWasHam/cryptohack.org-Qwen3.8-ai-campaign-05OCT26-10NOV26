---
record: agent-aar
puzzle: challenge-296-cryptohack-substitution_cipher_iii-downu
category: ctf-archive
url: https://cryptohack.org/challenges/substitution_cipher_iii-downu/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-67-cryptohack-substitution_cipher_iii-downu/flag.txt"
flag_sha256: 37e958a95f9e84a525b62ea10586e65339af1b8626c7b8414124b893a86d7d1a
skills: []
human_twin: AAR.md
---

# AGENT — substitution_cipher_iii-downu (DownUnderCTF2020 "Substitution Cipher III")
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Direct MQ solving (no need for MI key-recovery): system = {f_i + ct_i} + Boolean
constraints. For msg2: exploit zero padding — if inner length L in [15,20] (prior session
proved >=15 by exhaustive guess-determine UNSAT for 11..14), then msg2 unknowns = first
L-10 bytes; variables x_{8b..79} fixed to 0 => b=5..10 gives 40..80 unknowns.
msg1: all 80 unknowns (+ASCII bit7=0 linear constraints as extra polys).

## reusable-rules
- VERIFY BIT-ORDER CONVENTIONS FROM THE SOURCE before constraining: one index off
  (8k vs 8k+7) poisoned the whole prior sweep and its "UNSAT ⇒ length" conclusion.
- A solver result that violates its own equations is a pipeline bug, never a crypto hint:
  re-ground with a fully self-generated instance whose plaintext is planted (mi_gen2.py).
- msolve `-g 2` (reduced GB) decodes unambiguously (x_i+c ⇒ x_i=c) whereas the rational
  parametrization needs GF(2^80) arithmetic to read; use the GB route when the ideal is
  expected 0-dimensional with linear staircase.
- ASCII MSB constraints cut the MQ from 80 to 70 unknowns — this is what made msolve
  finish in minutes instead of the prior 1500 s timeouts.

## anti-patterns / limits
- Did not attempt MI key-recovery (Patarin-style); direct MQ is sufficient here.
- msg2-shorter-than-10 case was inferred (UNSAT sweep + ≤10 byte bound), not re-swept
  with correct bit order; not needed — recovered msg2 is exactly 10 printable chars and
  verifies against ct2.

## artifacts [OBSERVED]
- code: check_lens.py, decode_v2.py, gen_ms.py, mi_gen2.py, mq.py, runsolve.py, selftest.py, verify.py
- data/logs: flag_substitution_cipher_iii-downu.txt, ms_sweep.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
No external sources; provided materials only plus own in-campaign prior attempt/fresh self-derived tooling. Disclosure wording preserved verbatim:
> (prior attempt: challenge-296-...-downunderctf2020 — FAILED, no flag; this folder = retry with real F4)
> fresh fully-self-derived MI generator
