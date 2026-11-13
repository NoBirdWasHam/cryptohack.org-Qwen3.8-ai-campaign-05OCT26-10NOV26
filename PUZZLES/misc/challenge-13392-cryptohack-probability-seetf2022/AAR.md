# AAR — probability-seetf2022 (SEETF 'probability')

## Status: SOLVED — flag [flag — recorded in FLAGS/ctf-archive/challenge-13392-cryptohack-probability-seetf2022/flag.txt]
(server-printed flag at round 1276 of live connection #4; submitted, ok:true,
solved count 260->261, archive score_delta 0 as expected)


## Vulnerability
Server prints every `random.random()` draw from a global CPython Mersenne Twister.
Each double leaks 27 bits of one MT word (bits 31..5 of temper(w)) + 26 bits of its
partner. Honest play wins ~0.42/round; 800/1337 needed -> must predict future draws.

## Bugs found in prior session's solve.py (this session)
1. `untemper()` was broken two ways: `for _ in range(2): y ^= y >> 18` is an
   involution (double application = identity, so >>18 was never inverted), and the
   masked-shift inverses read from a frozen copy instead of the accumulator.
   The file's own built-in assert at import failed -> nothing could ever work.
   Fixed with standard doubling-inv_rshift / bit-accumulator inv_lshift (verified
   2000/2000 round-trips).
2. `mt_next()` used the WRONG twist recurrence: `ws[i] = ws[i-624] ^ f(ws[i-624], ws[i-623])`.
   Empirically verified against live CPython (1400 words): correct is
   `ws[i] = ws[i-227] ^ f(ws[i-624], ws[i-623])`. (j-624 form: False, j-227: True.)
3. recover() twist loop never propagated constraints back to base words
   (candidate sets per twist word computed independently, mutually inconsistent).
   Replaced with a GF(2) linear-algebra recovery: parametrize each base word by its
   5 (even slot) / 6 (odd slot) unknown low bits, propagate symbolic bit-rows through
   the (linear) twist + temper, feed all observed twist words' top bits as equations,
   Gaussian-eliminate (bitset rows), check rank == 3432, round-trip verify.

## Strategy layers (this session)
1. Prediction: GF(2) recover at 630 doubles (theoretical min: word 623's free
   bits first enter equations at j=1247). rank 3428/3432 + proven-irrelevant
   w0-low-4 kernel. 0.1 s.
2. Per-round foresight play: max ~696/1337. NOT ENOUGH (per-round win prob
   0.523 is the ceiling, 800/1337=0.598 required).
3. GLOBAL lookahead DP: rounds share one stream; player hit-choices move the
   round-boundary PHASE. Forward DP over (round, stream pos) with up to 12
   hits/round: optimal ~800-850 wins over a fresh 1337 rounds from round 1
   (mean ~835, sd ~20). Starting the DP at crack (round ~195, honest phase
   ~0.4276/round, THRESH retuned 0.55) costs ~40 wins -> P(flag) per
   connection ~25-40%. run_live.py retries connections until the flag.

## Live protocol notes
- Server = exact probability.py (banner/rules verified by raw probe).
- input() flushes stdout each prompt; prompts arrive as '...hit or stand? '.
- crack at ~630 doubles verified live: zero DESYNC through thousands of doubles.

## Status
- local: predict 3000/3000 exact; end-to-end sim flags on ~8/30 seeds (others
  759-799 wins = stream genuinely unwinnable-from-crack, DP is optimal there).
- live: retry loop in progress (run_live.py -> live.log).

## Learning points
- CPython twist is j-227 based, and Stream doubles need temper(state words).
- `for _ in range(2): y ^= y>>18` == identity (involution) — classic untemper trap.
- Full-foresight blackjack vs fixed dealer rule: per-round value 0.523 < the
  0.598 threshold; only cross-round phase control (global DP) bridges the gap.


## Sources
Sources: challenge-provided materials only; self-derived per run logs. (The 'prior session's solve.py' fixed in this AAR is this campaign's own earlier attempt, not an external writeup.)
