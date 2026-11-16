---
record: agent-aar
puzzle: challenge-56-cryptohack-1n_jection-zh3r0_ctf_v22021
category: ctf-archive
url: https://cryptohack.org/challenges/1n_jection-zh3r0_ctf_v22021/
status: solved
date: 2026-10-26
flag_ref: "FLAGS/ctf-archive/challenge-56-cryptohack-1n_jection-zh3r0_ctf_v22021/flag.txt"
flag_sha256: 5769a5c2250c4ee7af7b4d76e754436b81dea03ac572377c96e898d47d196053
skills: []
human_twin: AAR.md
---

# AGENT — 1n_jection (Zh3r0 CTF V2), CryptoHack archive slug 1n_jection-zh3r0_ctf_v22021
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Pure inversion — no oracle, no lattice:
1. Cantor unpairing: `w = (isqrt(8z+1)-1)//2`, `j = z - w(w+1)/2`, `i = w-j`.
2. Tree shape depends only on the flag length `L` (halving rule is deterministic), so
   unroll the pairing tree for each candidate `L` and test that every leaf lands in
   printable ASCII. `L=70` is the unique fully-printable decode.
3. Flag format was `zh3r0{...}`, not `crypto{...}` — first pass filtering on the
   `crypto{` prefix found nothing; loosening to "all printable + braces" hit immediately.

Verified `rec(nk2n(msg),L)==msg` round-trip for all L in 1..129 with random bytes before
trusting the inversion.

## reusable-rules
- Card name ≠ challenge type; read the provided source before designing an attack.
- Cantor pairing is invertible in integers (floor-sqrt trick); a pairing tree only needs
  the top-level length to fix its shape — brute-force length, verify charset.
- CTF flag prefix varies by source CTF (Zh3r0 archive → `zh3r0{`); don't hard-code `crypto{`.

## anti-patterns / limits
- None material. Length brute force was capped at 200 (flag was 70); uniqueness of the
  printable decode was observed (single hit) but not proven.

No third-party writeups consulted. Reference for Cantor inversion: standard textbook
pairing-function inverse (e.g. HPS-adjacent set theory), no external tooling used.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_1n_jection-zh3r0_ctf_v22021.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
