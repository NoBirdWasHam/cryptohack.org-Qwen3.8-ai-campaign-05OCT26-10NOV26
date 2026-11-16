---
record: agent-aar
puzzle: challenge-20-cryptohack-ticket_maestro-cryptohack2024
category: ctf-archive
url: https://cryptohack.org/challenges/ticket_maestro-cryptohack2024/
status: solved
date: 2026-10-25
flag_ref: "FLAGS/ctf-archive/challenge-20-cryptohack-ticket_maestro-cryptohack2024/flag.txt"
flag_sha256: 5a0724223700de16086107c804d2c3561aa58271b8931210c1b66a1d064870c3
skills: []
human_twin: AAR.md
---

# AGENT — 299-cryptohack-ticket_maestro-cryptohack2024: Ticket Maestro (archive twin)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack run (this session)" [OBSERVED text; evidence tag applies to its source, not each claim]
Ran `solve.py` (copied from challenge-240, only the flag filename changed) against
archive.cryptohack.org:26896: BuyTicket → Redeem original → 11 forged redeems
(balance 9→20) → BuyFlag. All 11 forges accepted first try.

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- No independent re-derivation of the serialization format was done here; the
  proven challenge-240 solver was reused (same server, same files).
- score_delta was 0; credit verified via solved-list growth + readback instead.

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_ticket_maestro-cryptohack2024.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
No external sources; archive twin of challenge-240 whose own solve notes were reused internally. Disclosure wording preserved verbatim:
> ## Key implementation notes (from the original solve, reused verbatim)
> This is the CTF-archive twin of `snark-maestro` (solved 2026-10-23 in
