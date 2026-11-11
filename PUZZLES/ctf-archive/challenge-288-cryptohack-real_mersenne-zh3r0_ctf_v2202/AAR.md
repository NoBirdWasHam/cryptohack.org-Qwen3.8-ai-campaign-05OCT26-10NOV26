# AAR — real_mersenne (zh3r0_ctf_v2, CryptoHack archive #288)

## Vulnerability
Server-side `random.random()` (CPython MT19937) used to draw the hidden `x` each
round. The score line leaks, for y=0 probes, `u = int(2**53 * random())`, i.e.
the top 27 bits of output word o_2i and top 26 bits of o_{2i+1} per round.

## Attack
1. Probe 936 rounds with guess `0` → `round score: 2^53/u` reveals u exactly
   (parse as d·2^53//n). ~1/1024 rounds score the capped-1024 branch (x<2^-10)
   → no u; the GF(2) solver tolerates misses outside the 312–935 equation window
   (if a miss lands inside the window, reconnect: fresh MT state, retry loop).
2. State recovery (`mt_lib.py`): unknowns = the 5 hidden low bits of every even
   output + 6 hidden low bits of every odd output of the first 624 outputs
   (312·11 = 3432 GF(2) unknowns). Symbolic propagation of MT19937 two cycles
   forward, tempering modelled as GF(2) maps (untamper matrix via [A|I] Gauss),
   observed bits of cycle-2 outputs give the equations; Gaussian elimination;
   30-round holdout check passes.
3. Predict all future rounds, guess the exact float x (`%.17g` — round-trip
   exact) → |x−y|=0 < 2^-10 → round score 1024 every round.
4. 936 probes + ~972 perfect rounds > 10^6 → server prints the flag.

## Key gotcha (why earlier attempts "bailed")
On a win the server does `print(flag); exit(0)` INSIDE a `try:` whose bare
`except:` catches `SystemExit` → prints "Error, exiting". If the reader stops at
the score line it never consumes the flag line and reports a false server error.
The real flag text does not trigger "flag"-substring detection either. Fix:
after the score line keep reading until next prompt, regex any `prefix{...}`
token, and dump every raw line to raw_log.txt.

## Key numbers
- threshold 10^6, cap 1024/round → 977 capped rounds minimum; total budget 2000 rounds.
- RTT ≈ 0.13–0.25 s → full run ≈ 4 min; must run in background (foreground tool
  timeout killed the predecessor's identical run mid-harvest).

## Result
SOLVED. Flag: `zh3r0{r34l_m3n_d34l_w17h_m3r53nn3_w17h_r34l_v4lu3s}`
(caught live_run5 H1906 right after total score crossed 10^6; submit ok:true,
account solved count 255→256; reconcile.py lists it under LIVE-solved.
score_delta 0 — archive challenge, 0 points, as expected.)

## Limitations / failed paths (evidence)
- live_run2.log: bailed "Error, exiting" — cause unknown at that point
  (round()-stopped-at-score-line discarded the flag line; confirmed by
  round_log.txt of live_run3: H1906 total 1000487.04 > 10^6, next line
  'Error, exiting' — the flag was printed but never read).
- live_run4: EOFError after H1907 (total 1000081.87) — flag line printed but
  `crypto{...}` regex didn't match the actual flag prefix; fixed with generic
  token{...} regex + raw line logging.
- Local mock (`--local`) with decoy flags `crypto{zzqx_9182}` and
  `zh3r0{...}` verified the fixed reader before the live run.

## Sources
not recorded in run logs (pre-discipline solve)
