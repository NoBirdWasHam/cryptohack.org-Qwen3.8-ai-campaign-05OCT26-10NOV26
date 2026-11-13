# AAR — key_backup_service_2-hkcert_c (CryptoHack ctf-archive, folder challenge-270)

## Status: IN PROGRESS

## Setup / fingerprint
- v2 = offline transcript variant of v1 (sibling folder challenge-269): same
  server code shape but E=65537, CALLS=65537, primes from MT19937 seeded with
  master_secret || (G|H)^id mod N (sus constants; N prime, H = ASCII "these
  numbers are of course sus!"). No listener; archive ships transcript.log.
- transcript.log = exactly `flag` + 16384 blocks of [pkey / send 2 / send 3 /
  backup] = 65537 calls (full budget). First line after `[cmd] flag` is the
  AES-CBC(ms, IV=0) flag ciphertext we must decrypt offline.

## Attack
1. Modulus recovery without knowing n: c2 = 2^65537 mod n, c3 = 3^65537 mod n
   ⇒ n | gcd(2^65537 − c2, 3^65537 − c3); verify pow(2,e,n)==c2, pow(3,e,n)==c3.
   (v1 needed a divisor-window probe because it only had 1 send/key; the
   transcript gives 2 fixed sends/key so plain gcd works.)
2. Håstad broadcast on the fixed master_secret: cb_i = ms^65537 mod n_i over
   16384 moduli. ms ~ uniform 256-bit ⇒ ms^e ≈ 2^16.68M bits; product M of
   16384 ~1023-bit moduli ≈ 2^16.76M bits ⇒ product exceeds ms^e w.h.p.
   (≈85% by the E[log ms]=254.56 calculation) — no Coppersmith needed.
3. CRT all cb_i → R = ms^e (exact integer) → gmpy2.iroot(R, 65537) → ms;
   verify pow(ms,e,n_i)==cb_i; AES-CBC-decrypt the first-line flag ciphertext, IV=0.

## Key numbers
- e=65537; 16384 blocks; n_i ≈ 2^1023; M bits vs 256·65537 = 16,777,472.

## Results
## Solved: YES — flag submitted, ok:true, solved-list 268→269 (archive = 0 pts, expected).
Flag: `[flag — recorded in FLAGS/ctf-archive/challenge-270-cryptohack-key_backup_service_2-hkcert_c/flag.txt]`
(self-derived; never read from any answer source)
- kept 16384/16384 blocks, 0 zero-candidate (L-gcd trick fully recovers s≤2^24
  in every block; the earlier trial-division scan2 had windowing bugs).
- M = 16,760,612 bits > ms^e = 16,730,390 bits → slack ~30 kbit; iroot(R,65537)
  exact; full pow(ms,e,n_i)==cb_i verify over all 16384 blocks: 0 failures.
- ms (256-bit) → AES-CBC(key=ms, IV=0) on the transcript's first-line
  ciphertext → flag, 40-byte plaintext un-pads cleanly.

## Learning points
- The two fixed sends (2, 3) are a modulus oracle: n | gcd(2^e−c2, 3^e−c3);
  the random cofactor s of that gcd is neutralized by gcd with a "primorial-
  style" L, because a product of two 512-bit primes has no factor ≤ 8192.
- cb < n is a free extra filter for candidate moduli.
- With ms uniform on [0, 2^256), E[log2 ms] ≈ 254.56, so 16384 ≈2^1023 moduli
  carry ~80 kbit of expected slack over ms^65537 — Håstad without padding or
  Coppersmith; that's why the author shipped exactly CALLS/4 blocks.
- The sus N/G/H + MT19937 keygen is (again) mostly flavor: it does leak via
  occasional prime collisions between keys (ord(G|H mod N) is small enough
  for 16384 random ids to collide a few times), but the solve needs only
  collision-aware CRT (divide shared factor out, keep the cofactor equation).
- Flag text itself hints at batch gcd (product tree) for the 16k-way gcd step.

## Limitations
- Relied on P(s ≤ 2^24 with 24-bit-capped prime powers) for the L-gcd trick;
  held for all 16384 blocks (zero-cand list empty), but a block with a huge
  s would be silently dropped — slack budget was only ~30 blocks, so a handful
  of such blocks would have needed a fallback (larger L or extended search).
- MT19937/N/G/H path was never needed; prime-collision origin (ord(G) vs ord(H)
  mod N) was not confirmed by DLP, only inferred from 512-bit cross-gcds.

## Files
- chall.py, transcript.zip/transcript.log, statement.txt, site.md
- solve.py (parse+CRT pipeline), scan2.py + scan.log (diagnostics), solve2.py
  (first broadcast attempt), solve3.py (final pipeline), cands.json, run/solve logs,
  ms_hex.txt, flag_key_backup_service_2-hkcert_c.txt

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
