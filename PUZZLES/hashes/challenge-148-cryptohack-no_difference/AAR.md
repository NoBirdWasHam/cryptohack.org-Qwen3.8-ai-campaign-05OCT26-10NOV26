<!-- AAR -->
# AAR — challenge-148-cryptohack-no_difference: No Difference (CryptoHack)

**Result:** SOLVED (account NoBirdWasHam; date 2026-10-21) — flag `[flag — recorded in FLAGS/hashes/challenge-148-cryptohack-no_difference/flag.txt]`
**Date:** 2026-10-21

## Source
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "No Difference" (175 pts, slug `no-difference`)
- **Interactive service:** socket.cryptohack.org 13395
- **NOT consulted:** solutions pages, search-engine writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/hashes/challenge-148-cryptohack-no_difference/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## How it was solved
The hash's SBOX is NOT injective (rows satisfy S[x]=S[x^0x0F] plus cross-row duplicates).
permute = bit-transpose (involution): bit i of t_j = bit j of x_i. Message byte k XORs
state byte 4+k, so in permuted coords the HIGH nibble of every t_j is fully controllable
while the LOW nibble is fixed by INIT. Found a colliding SBOX pair (0x50,0x80) sharing the
fixed low nibble at position j=0, built two one-block messages whose post-substitute states
coincide -> identical hashes. Server returned the flag. See solve2.py.

## Learning points
- A hash SBOX that is a non-injective map gives trivial collisions: match the FIXED bits of
  the pre-substitute state and swap only the controllable bits through a colliding pair.
- Listener protocol gotcha: this listener sends only the before_input quote (no JSON prompt
  line) — send the dict immediately after the first line.

## Limitations
- Flag captured directly from the live listener; site auto-marks solved on listener capture.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
