---
record: agent-aar
puzzle: challenge-269-cryptohack-key_backup_service_1-hkcert_c
category: ctf-archive
url: https://cryptohack.org/challenges/key_backup_service_1-hkcert_c/
status: solved
date: 2026-10-28
flag_ref: "FLAGS/ctf-archive/challenge-269-cryptohack-key_backup_service_1-hkcert_c/flag.txt"
flag_sha256: 4749cd863f9fbb294c5a4f0d5c642f0a17fa5e4f18a407f683d25b8c49e66807
skills: []
human_twin: AAR.md
---

# AGENT — key_backup_service_1-hkcert_c (CryptoHack archive, folder challenge-269)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability" [OBSERVED text; evidence tag applies to its source, not each claim]
- Textbook (unpadded) RSA with e=17. The fixed 256-bit `master_secret` is encrypted
  (`backup` → `ms^17 mod n`) under a *fresh* RSA key every `pkey`, and `send` is an
  arbitrary-message raw encryption oracle. `flag` returns AES-CBC(flag, key=ms, IV=0).
- Server never reveals n, but the oracle lets you recover it: encrypt
  m = 2^61, so m^17 = 2^1037 > n (n < 2^1024 since p,q < 2^512).
  `m^17 − c = k·n` with k = ⌊m^17/n⌋ ∈ (2^13, 2^15] (guaranteed since n ∈ [2^1022, 2^1024)
  from the forced top bits of p,q). Scanning the ~24.5k k in that window for divisors of
  D = m^17 − c recovers n exactly — filters: odd, n%17≠0, bit-length window.
  In practice the divisor candidate was **unique for all 5 keys**, both locally and live.

## reusable-rules
- "Similar to Calm Down" author note and the sus N/G/H + MT19937-prime generator were red
  herrings for v1 — the MT/seed machinery is irrelevant; the break is pure broadcast on a
  re-used secret with small e and small message.
- An e-th-power oracle without the modulus is enough to leak the modulus when you can push
  m^e past n by a bounded factor: the quotient window is (m^e/n_max, m^e/n_min] and divisors
  of m^e−c in that window pin n.
- Budget fit: naive gcd-based n-recovery needs 2 sends/key (20 calls > 17); the divisor
  trick makes it 1 send/key (15+1 calls).

## anti-patterns / limits
- Divisor uniqueness is probabilistic (~expected 0.06 ambiguous keys per key over the
  4×-wide k window); solve.py handles ambiguity by trying the Cartesian product of
  candidates with the perfect-17th-power + per-modulus pow check as arbiter. Did not need
  the built-in 2 spare calls in practice.
- Assumed live server == posted chall.py; fingerprinted implicitly (identical `[cmd] `
  prompt, 16-call budget held, all 5 moduli verified by pow(r,17,n_i)==c_s,i).

## artifacts [OBSERVED]
- code: solve.py
- data/logs: flag_key_backup_service_1-hkcert_c.txt, live_err.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- see AAR.md `Sources`
