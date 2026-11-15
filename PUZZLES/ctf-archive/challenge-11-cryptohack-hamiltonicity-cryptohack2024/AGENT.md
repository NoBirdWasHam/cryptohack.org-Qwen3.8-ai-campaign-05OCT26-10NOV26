---
record: agent-aar
puzzle: challenge-264-cryptohack-hamiltonicity-cryptohack2024
category: ctf-archive
url: https://cryptohack.org/challenges/hamiltonicity-cryptohack2024/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/ctf-archive/challenge-11-cryptohack-hamiltonicity-cryptohack2024/flag.txt"
flag_sha256: d7f32b82c53e72bc367797bd34b4ac2cfba720813515f217ce1c43a3b5cb9b2f
skills: []
human_twin: AAR.md
---

# AGENT — 264-cryptohack-hamiltonicity-cryptohack2024: Hamiltonicity (CryptoHack2024, CTF-archive mirror)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
Per-round Fiat–Shamir challenge bit depends **only on the prover's commitment matrix A** (the graph openings / permutation are not hashed). Pedersen commitments are re-randomizable: `c·h2^r'` opens to the same message with randomness `r+r'`. So the prover can re-randomize commitments until the FS bit is 0, then always answer the "reveal permutation + all openings" branch — trivially satisfiable for a permuted copy of the public G. Soundness 1/2 per round collapses to 1: the prover picks the challenge.

## reusable-rules
- Archive "mirror" challenges can be byte-identical re-hosts of main-site challenges: diff the provided files against solved twins **before** re-deriving anything; the port lives in the ctf-archive card HTML, not on archive.cryptohack.org pages.
- The solver's flag scraper missed the save because the final `f.read()` tokens were bytes-repr (`b'crypto{...}'`); the printed output was still authoritative. Match `crypto{` anywhere in the token, not `startswith`.

## anti-patterns / limits
- No independent re-implementation of the protocol was written for this twin; correctness rests on the byte-identical diff + live 128/128 accept + solved-list readback.
- score_delta was 0 (archive credit), so the solved-list readback was the sole credit signal, as anticipated in the brief.

## artifacts [OBSERVED]
- code: example.py, hamiltonicity.py, solve.py
- data/logs: flag_hamiltonicity-cryptohack2024.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Statement + file links extracted from the `<li data-challenge="hamiltonicity-cryptohack2024">` card of the scraped ctf-archive category page (saved to `statement.txt`).
- Provided files downloaded from `/static/challenges/`: `chal.py`, `example.py`, `hamiltonicity.py`.
- **NOT consulted:** any /solutions/, /solves/, or third-party writeups.
