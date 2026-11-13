---
record: agent-aar
puzzle: challenge-219-cryptohack-csidh_key_exchange
category: isogenies
url: https://cryptohack.org/challenges/csidh_key_exchange/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/isogenies/challenge-219-cryptohack-csidh_key_exchange/flag.txt"
flag_sha256: 9fba9f31408ed30651c94e7e11c65e8d63a34261a9cda020d1c0efc9760664a3
skills: []
human_twin: AAR.md
---

# AGENT — challenge-219: CSIDH Key Exchange (cryptohack.org, 90 pts)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability (plain words)" [OBSERVED text; evidence tag applies to its source, not each claim]
The challenge exposes both CSIDH private exponent vectors a_priv, b_priv
(teaching setup). The mathematical property exploited is CSIDH's own design: the
class-group action is abelian, so the shared curve depends only on the SUM of the
exponent vectors — shared = action of (a+b) on E0 — one combined walk instead of
two independent ones.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- Python `open(...,"w")` on Windows wrote CRLF into the .gp file → gp echoed `\r` garbage
  and polrootsmod output was unparseable. Fix: avoid gp here entirely (Cardano), or write
  with `newline="\n"`.
- First EC-doubling draft dropped the `+a4` term in the slope — caught by the
  GA==[2^ea]G-style sanity checks, not by a crash. Always assert on-curve/order checks.
- Brute-force helpers from velu_engine.py (point enumeration, root scan) are O(p) —
  fine at p=419, hopeless at 512 bits; replaced with O(ℓ)-per-step code.

## artifacts [OBSERVED]
- code: cubic.gp, dbg.gp, solve.py, solve3.py
- data/logs: solve.log, walk_cache.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Galbraith et al. Thm 25.1.6 Vélu formulas (inherited from prime_power,
  re-validated).
- CSIDH protocol and instance parameters from the challenge's own source.sage.
- No third-party writeups or solution pages consulted (run log).
