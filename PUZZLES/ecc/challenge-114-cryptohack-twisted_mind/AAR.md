# AAR — 114-cryptohack-twisted_mind: Twisted Mind (CryptoHack)

**Result:** SOLVED — submitted, API-verified (`score_delta +80`, 9195→9275, 181 solved).
**Date:** 2026-10-20 (UTC). (Earlier attempts 2026-10-19 stalled at "k mod S only" — see
correction below: the documented "wall" was WRONG.)

## Sources
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Challenge:** "Twisted Mind" (slug `twisted_mind`, 80 pts), service `13416.py` provided
- **Service:** socket.cryptohack.org:13416 — 2 x-coordinate queries, 120 s, then guess key
- **NOT consulted:** solutions page, search-engine writeups (no-cheat rule)

## The flag
Recorded in `FLAGS/ecc/challenge-114-cryptohack-twisted_mind/flag.txt` — kept out of AAR prose per the flag-separation rule; sha256 in `FLAGS/INDEX.jsonl`.

## Problem
- p = 2^192 − 237, a = −3, b = 1379137549983732744405137513333094987949371790433997718123.
- Server answers `pubkey = x(k·P)` for up to 2 submitted x-coords; k = min(k0 mod N, N − k0 mod N).
- #E = N = 2·11·269·2985973·1631363213·123462957881·Q (Q 91-bit prime) — verified via ellcard.
- Twist #E' = 2p+2−N = 2·3³·1607·693493·1483406443·40202856427·Q' (Q' 91-bit prime).

## How it was solved
1. **Key insight (corrects the 2026-10-19 AAR):** the server's Montgomery-style (X,Z) ladder
   on a WEIERSTRASS curve with an OFF-CURVE x0 (t = x0³+ax0+b non-residue) computes
   x([k]P') on the QUADRATIC TWIST. Verified locally 39/39 (`twist_verify.py`): work in
   F_p[s]/(s²=t) with P'=(x0,s); x([k]P') ∈ F_p always.
2. So query 1 = on-curve x_on → k mod S (S = smooth part of #E, 102 bits);
   query 2 = off-curve x_tw → k mod S' (smooth part of #E', 102 bits).
   **lcm(S,S') ≈ 2^202 > N ⇒ the two residues pin k uniquely in [0, N/2] — the two
   91-bit prime factors are irrelevant.** The 10-19 "wall" (Q-part infeasible) was real
   for E alone but bypassed via the twist.
3. Pohlig–Hellman + BSGS per prime power on BOTH sides (twist side over F_p²; target
   y-lift w = sqrt(rhs(A2)/t), Tp = (A2, w·s)).
4. **Timeout discipline:** server clock (120 s) starts at connect → ALL BSGS tables
   precomputed BEFORE connecting (base points are attacker's choice). Live phase took 7 s.
5. x-only ⇒ global ± per side: 4 CRT sign-combos, filter to [0,N/2], local check
   x([c]P) == A1 → unique candidate → `get_flag` → flag.
6. Live run: `live_twist_run4.log` (runs 1–3 = protocol/bug fixes, see below).

## Bugs found the hard way (each documented with a failing test)
- **Affine P+(−P) test:** `y1+y2 == 0` misses the reduced case `y1+y2 == p` → [N]P ≠ O.
  Invisible to random tests; caught only by the #E·P == O invariant + PARI ellmul.
- **Base point must cover every prime power:** x_on=3 had ord(P) | N/11 (silent degenerate
  q=11 projection); twist point at x_tw=5 missed the factor 2. Now asserted in prep().
- 3-line banner must be fully read before first response.

## Learning points
- **A Weierstrass x-only ladder IS a twist oracle** — "twist attacks are Montgomery-only"
  is FALSE; the (X,Z) formulas are generic rational functions that evaluate the twist
  group law for off-curve x.
- **Two partial orders beat one big prime:** when #E and #E' each have a large factor,
  the smooth parts' lcm can still exceed the group order — always factor the TWIST too.
- Assert algebraic invariants (#E·P == O, projection orders) before trusting any pipeline.

## What I did / did not do
- 4 live connections total (3 aborted by my own bugs before key-relevant queries;
  1 successful). 2 point-queries + 1 get_flag on the successful session. No writeups.

## Limitations
- None material; flag verified by submission (score_delta +80).

## Configuration (environment for this run)
- **Date:** 2026-10-20 ~15:05 UTC · **Host OS:** Windows 11, git-bash/MSYS · **User:** OWNER
- **Interpreter:** venv `~\tools\crypto-ctf\venv\Scripts\python.exe`; PARI/GP `~\tools\gp64.exe`
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-114-cryptohack-twisted_mind`
- **Agent:** Hermes Agent (desktop, qwen3.8-flash-next-unsloth-ud-q4_k_xl @ qwen3-8-flash)
- **Network:** socket.cryptohack.org:13416, cryptohack.org HTTPS (submit)
- **Artifacts:** `13416.py` (provided), `twist_verify.py` (ladder==twist proof),
  `solve_twist.py` (working), `live_twist_run1..4.log`, `twist.gp`/`card.gp`/`mul.gp`
  (order/factor/ellmul checks), plus 2026-10-19 artifacts (`solve.py`, `live_result.json`, …)
