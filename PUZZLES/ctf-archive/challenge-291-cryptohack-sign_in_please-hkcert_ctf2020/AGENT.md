---
record: agent-aar
puzzle: challenge-291-cryptohack-sign_in_please-hkcert_ctf2020
category: ctf-archive
url: https://cryptohack.org/challenges/sign_in_please-hkcert_ctf2020/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-291-cryptohack-sign_in_please-hkcert_ctf2020/flag.txt"
flag_sha256: 6473c2e7a50f443e4a559c19fd9bf233881e820da2ef99c1998caba5c0231668
skills: []
human_twin: AAR.md
---

# AGENT — Sign in Please (HKCERT CTF 2020, CryptoHack archive #291)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
- Q1: pbox `0,1,2,3,4,5,-20,-19,-18,-17,-16,-15,16,17,18,19,-4,-3,-2,-1`,
  salt `AAAA` → hash over `[c0..c5][c0..c5][AAAA][AAAA]` → brute force chars 0–5.
- Q2: same trick on positions 6–11 → chars 6–11.
- Q3: positions 12–15 plus already-known 0,1 → only 4 unknowns (64^4, trivial).
- `auth`: read server pbox/salt, compute the hash from the recovered password, get flag.
- 4 of the 10 allowed commands; brute force done between spy and auth on the same
  connection (server has no idle timeout observed).

## reusable-rules
- `len(set(x)) == n` guards on index lists are broken by Python negative indices.
- A hash oracle over a permutable structure leaks per-position entropy: minimize
  covered positions via duplicate representatives, then brute force the commitment.
- 64^6 is the practical floor here (2 reps/position × 4 salt slots ⇒ ≥6 unknowns).

## anti-patterns / limits
- MT19937 prediction of server `random.shuffle` was rejected early: only 10
  commands/connection, ~76 bits of randrange output per auth, password fresh per
  connection — infeasible.
- Brute force is the bottleneck (~10 min/query worst case); no MITM/structure
  shortcut exists for sha256 commitments.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_sign_in_please-hkcert_ctf2020.txt, run2.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
not recorded in run logs (pre-discipline solve)
