# VOW trajectory-DP rho for capacity collisions (Spongebob battle, walker3, 2026-11-06)

## The construction rule that decides life vs death
- Pollard-rho/VOW collision search needs a random MAPPING f:S->S whose closures ARE the collisions
  (VOW'99 §2, same domain and range). Compose F = g∘h with h:X->Y the collision predicate
  (needs FULL image 2^|Y|) and g:Y->X injective. Then im(F)=encodings of Y (|im F|=|Y|, e.g.
  2^80) and a closure at ~1.25*2^(y/2) steps is a true collision.
- The literal partition rule G(x)=g_{pi(h(x))}(x) with g_i INJECTIVE ON X is a BIJECTION on X:
  never merges (2-cycle prob ~2^-126), fires == 0, yet ins/steps DP sanity still passes.
  Measured control: 707M steps -> hits=0, fires=0; its attractor orbits were even DP-degenerate
  (mask ~never fires). "Healthy stats, zero detection" = walker2 failure class.
- Channel lemma: the walk IMAGE must live where the predicate reads. If |im(h)|=2^64 (e.g.
  capacity-after-1-block of a 16B-message sponge where block1 is injective) but the collision
  predicate is 80-bit, closures are dominated ~2^63:2^46 by trivial pairs sharing the 64-bit
  channel. Fix used: predicate = capacity AFTER BLOCK 2 (2-block prefixes, 3-block messages):
  H(b1 b2 x)=H(b1' b2' x') iff c2=c2' AND x'=x^r2^r2' (permute linear+bijective), and the last
  block rebuild completes prefix-collision -> full-state collision (server accepts 24B msgs).

## Gate order before ANY launch (walker2 skipped the last one and died for it)
1. Kernel TV gate: byte-match C cap against python H on >=50 random vectors; print the message
   BYTE STRING (to_bytes little-endian), not word-hex — word-vs-bytes order confusion wastes hours.
   Table pitfall: T1-style init tables fold INIT into rate bytes (spread(INIT[i]^x)); absorbing a
   SECOND block must use raw SPREAD[i][x] or INIT gets re-XORed.
2. Firing harness at small truncated capacity T~20 with theta 2^-8: must FIRE in ~few*2^(T/2)
   steps end-to-end (hit -> traceback -> verify -> file). ins/steps==theta alone certifies only
   the DP filter, NEVER collision detection.
3. Bijection control (expected: healthy ins, hits=0, fires=0) documents the dead construction.
4. 60-s production smoke: assert SMOKE-DP-CHECK ins/steps == theta within +-60%.

## Details that bit
- Trajectory DP is detection-lossless ONLY because closures=collisions on a mapping; same-start
  self-closure (own rho) is a REAL closure — verify predecessors distinct, don't drop it.
- VOW: end trail at every DP (restart-on-DP); abandon cap 20/theta (e^-20 loss).
- T-blend table: slot = (mix*odd)>> (64-LOGT) to break lo&0xFFFFFF aliasing; probe -O3 vs -O2
  (walker3: O3 +8%, opposite of walker2's regression).
- FILE-NAMING SAFETY RULE: production fires write found_PROD_<n>.txt only; self-tests write only
  ./selftest/; harvest chain consumes found_PROD*.txt exclusively (never bare found*.txt) so test
  artifacts can never trigger live harvest/submit.
- Chain harvest in the same process: launch loop `walker3 && harvest3.py found_PROD_<n>.txt`
  (rebuild msg, re-verify with reference python BEFORE socket, submit on pass, restart on fail).
