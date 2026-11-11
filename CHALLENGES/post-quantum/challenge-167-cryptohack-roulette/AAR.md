<!-- AAR -->
# AAR — challenge-167-cryptohack-roulette: Nothing Up My Sleeve (CryptoHack)

**Result:** SOLVED (account NoBirdWasHam; date 2026-10-21) — flag `crypto{No_Str1ngs_Att4ch3d}`
**Date:** 2026-10-21

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "Nothing Up My Sleeve" (150 pts, slug `roulette`)
- **Interactive service:** socket.cryptohack.org 13387
- **NOT consulted:** solutions pages, search-engine writeups (no-cheat rule)

## The flag
`crypto{No_Str1ngs_Att4ch3d}`

## How it was solved
Roulette spin values are the low bits of P256 scalar-mult states seeded 'nothing up my sleeve' (Q=P trick): spin_k = s_{k+1} & mask30 with s on the EC ladder. State-1 digits observed -> r1; per state the unknown high part c gives 65536 candidates s=(c<<240)+r_prev, filtered by observed spins; once the candidate set collapsed to 1, bet the exact number. Bankroll grew to $2365 and the server returned the flag. See bot3.py / bot3.log (120 spins, cands=1 at bet time).

Artifacts in this folder: `bot3.py`, `bot3.log`, `p256.py`, `flag_roulette.txt`

## Learning points
EC-scalar-multiplication-based RNGs leak through partial output bits: the ladder state's low bits are visible, and the high part is brute-forceable when < 2^16 candidates remain per step; filter with observed outputs and bet only when the candidate set is a singleton.

## Limitations
- Flag captured directly from the live listener; site auto-marks solved on listener capture.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
