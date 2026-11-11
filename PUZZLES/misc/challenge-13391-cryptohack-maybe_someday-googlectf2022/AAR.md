# AAR — maybe_someday (GoogleCTF 2022) — CryptoHack archive 14846 — SOLVED

Flag: `CTF{p4dd1n9_or4cl3_w1th_h0mom0rph1c_pr0p3r7y_c0m6in3d_in7o_a_w31rd_m47h_puzz1e}`
Submitted ok:true, solved count 257->258 (archive => score_delta 0, expected).

## Protocol
- Banner `n = ...`, `g = ...`; then 16 rounds: server prints `c0 = encrypt(secret)`
  (Paillier, PKCS1v1.5 pad), reads **20 ciphertexts batched**, replies 😀/😡 per
  line (fast_decrypt unpad success/fail), then reads one guess line; wrong guess or
  exception -> `👋`. 16 surviving rounds -> `🏁 flag`.
- secret = sha512(os.urandom(2)).hexdigest() — **128 hex chars = 1024 bits** (the
  predecessor AAR wrongly said 64 chars/512 bits; modelcheck vs real chall.py: their
  512-bit model mismatched 29% of samples, corrected model matched 240/240).

## The vuln
Paillier additive homomorphism + padding-structure oracle. For δ = K·2^1024 + t,
c = c0·g^{−δ} mod n² decrypts to m − δ; the PKCS1v1.5 unpad succeeds iff a zero byte
survives anywhere in m′[2:]. Layout: `00 02 ‖ pad(125 nonzero) ‖ 00 ‖ secret(128)`,
so the zero at byte 127 (the 2^1024 slot) is destroyed iff K+borrow ≠ 0 mod 256.
With S = int(secret), ge = [S ≥ t], h = haszero((S−t) mod 2^1024, 128 bytes):
- K = 0:   😀 ⟺ ge ∨ h
- K = 255: 😀 ⟺ ¬ge ∨ h
- 1..254:  😀 ⟺ h        (p(h) ≈ 1−(255/256)^128 ≈ 0.39 → ~0.975 bit/query)
All predicates computable offline for the 65536 candidate seeds.

## Attack
design3.py: pool of 1406 (K,t) columns (quantile thresholds for K=0/255, random t for
mid-K) over 65536 candidate patterns; greedy (max pairs removed) + hill-climb.
Result: 20 queries, 62040 unique patterns, 1730 collision patterns covering 3496
candidates. Decode: response word r → true pattern must be a **submask** of r (the
only noise, P_last==1 → P−1 borrow → extra zero byte, ~1/255/round, flips 😡→😀 only);
pick max-popcount table entry; if r is a known collision pattern → **abort session
without guessing** (free reconnect). Wrong-guess death is avoided, so ~2.7%/round
collision risk costs only session retries, not progress.
Live run: attempt1 hit collision at round 14, attempt2 at round 11, attempt3
survived 16/16 → flag. solve.py is runnable (DESIGN env var; --local runs against
chall.py subprocess with FLAG=TEST{...}).

## Key numbers
- 20 queries × ~0.98 bit vs 16 bits needed; greedy+HC: 4500→1812→1802 pairs (338s).
- Local smoke: 16/16 rounds first clean try. Live: flag on attempt 3 (~3 min).

## Limitations / honest notes
- Design NOT collision-free (1730 dup patterns); survives only via abort+reconnect.
  repair.py (targeted t for remaining classes) ran in background toward a cleaner
  design4.json — not required for the solve.
- P−1 noise (1/255/round) tolerated only by submask decoding; no error-correction
  margin designed (min pattern distance unoptimized).
- `grab_int` bug cost a debug cycle: `re.search(r'\d+', 'c0 = …')` matched the '0'
  in "c0" → c0=0 → all-😡. Fixed with split('=').
- Predecessor's design_qs.json / design2.py are built on the wrong 512-bit layout —
  obsolete; kept for history.

## Files
statement.txt, chall.py (= server file, verified identical by predecessor),
probe*.py (protocol recon), modelcheck.py (old-model refutation),
modelcheck2.py (new model 240/240), design3.py/design3.log/design3.json (attack
design), fixdup.py (dup-pattern tagging), repair.py/repair.log (optional cleaner
design4), solve.py (live solver), dbg1.py, flag_maybe_someday-googlectf2022.txt.

## Sources
Sources: challenge-provided materials only; self-derived per run logs. (Predecessor artifacts referenced in the AAR are this campaign's own earlier session, not external writeups.)
