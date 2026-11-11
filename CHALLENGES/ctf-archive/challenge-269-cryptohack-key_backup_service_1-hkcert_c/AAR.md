# AAR — key_backup_service_1-hkcert_c (CryptoHack archive, folder challenge-269)

## Solved: YES (flag submitted, ok:true, solved-list 267→268)

Flag: `hkcert21{y0u_d0nt_n33d_e_m3ss4g3s_f0r_br0adc4s7_4t7ack_wh3n_m_i5_sm41l}`
(self-derived via the attack below; never read from any answer source)

## Vulnerability
- Textbook (unpadded) RSA with e=17. The fixed 256-bit `master_secret` is encrypted
  (`backup` → `ms^17 mod n`) under a *fresh* RSA key every `pkey`, and `send` is an
  arbitrary-message raw encryption oracle. `flag` returns AES-CBC(flag, key=ms, IV=0).
- Server never reveals n, but the oracle lets you recover it: encrypt
  m = 2^61, so m^17 = 2^1037 > n (n < 2^1024 since p,q < 2^512).
  `m^17 − c = k·n` with k = ⌊m^17/n⌋ ∈ (2^13, 2^15] (guaranteed since n ∈ [2^1022, 2^1024)
  from the forced top bits of p,q). Scanning the ~24.5k k in that window for divisors of
  D = m^17 − c recovers n exactly — filters: odd, n%17≠0, bit-length window.
  In practice the divisor candidate was **unique for all 5 keys**, both locally and live.

## Attack (Håstad broadcast, e=17)
ms < 2^256 ⇒ ms^17 < 2^4352 < ∏(5 moduli ≥ 2^1022 each) ≥ 2^5110.
Call sequence (16 of the 17 allowed commands): `[pkey, backup, send 0x2000000000000000] × 5`, then `flag`.
CRT the five `ms^17 mod n_i` → exact integer ms^17 → integer 17th root → ms →
AES-CBC-decrypt the `flag` ciphertext offline with IV=0.
Verification before printing: r^17 mod n_i == backup ciphertext for all i.

## Key numbers
- e=17, CALLS=17, primes 512-bit ⇒ n ∈ [2^1022, 2^1024); probe m=2^61 ⇒ k-window (8192, 32768].
- 5 keys sufficed (slack: product 2^5110 vs needed 2^4352).

## Learning points
- "Similar to Calm Down" author note and the sus N/G/H + MT19937-prime generator were red
  herrings for v1 — the MT/seed machinery is irrelevant; the break is pure broadcast on a
  re-used secret with small e and small message.
- An e-th-power oracle without the modulus is enough to leak the modulus when you can push
  m^e past n by a bounded factor: the quotient window is (m^e/n_max, m^e/n_min] and divisors
  of m^e−c in that window pin n.
- Budget fit: naive gcd-based n-recovery needs 2 sends/key (20 calls > 17); the divisor
  trick makes it 1 send/key (15+1 calls).

## Limitations
- Divisor uniqueness is probabilistic (~expected 0.06 ambiguous keys per key over the
  4×-wide k window); solve.py handles ambiguity by trying the Cartesian product of
  candidates with the perfect-17th-power + per-modulus pow check as arbiter. Did not need
  the built-in 2 spare calls in practice.
- Assumed live server == posted chall.py; fingerprinted implicitly (identical `[cmd] `
  prompt, 16-call budget held, all 5 moduli verified by pow(r,17,n_i)==c_s,i).

## Files
- chall.py (downloaded), statement.txt, site.md, solve.py (run: `python3 solve.py local|live`),
  live_err.txt, flag_key_backup_service_1-hkcert_c.txt
