---
record: agent-aar
puzzle: challenge-270-cryptohack-key_backup_service_2-hkcert_c
category: ctf-archive
url: https://cryptohack.org/challenges/key_backup_service_2-hkcert_c/
status: solved
date: 2026-11-02
flag_ref: "FLAGS/ctf-archive/challenge-61-cryptohack-key_backup_service_2-hkcert_c/flag.txt"
flag_sha256: d1bf207b7bd2fca10270e6e89541eab5e822cf9f12d258ff7b9da320d3fd9974
skills: []
human_twin: AAR.md
---

# AGENT — key_backup_service_2-hkcert_c (CryptoHack ctf-archive, folder challenge-270)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
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

## anti-patterns / limits
- Relied on P(s ≤ 2^24 with 24-bit-capped prime powers) for the L-gcd trick;
  held for all 16384 blocks (zero-cand list empty), but a block with a huge
  s would be silently dropped — slack budget was only ~30 blocks, so a handful
  of such blocks would have needed a fallback (larger L or extended search).
- MT19937/N/G/H path was never needed; prime-collision origin (ord(G) vs ord(H)
  mod N) was not confirmed by DLP, only inferred from 512-bit cross-gcds.

## artifacts [OBSERVED]
- code: scan2.py, solve.py, solve2.py, solve3.py
- data/logs: flag_key_backup_service_2-hkcert_c.txt, ms_hex.txt, scan.log, solve2.log, solve3.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
