---
name: fhe-integers-agcd

description: Use for approximate-GCD FHE-integer CTF challenges.
---

# FHE over the integers (DGH) and the CS15 break

## Scheme (DGH10 = van Dijk–Gentry–Halevi–Vaikuntanathan, EUROCRYPT 2010, LNCS 6110, eprint 2009/616)
- Secret odd p (~gamma bits). Ciphertext for bit m: c = m + 2r + 2*(integer combination of public
  zero-ciphertexts); all noise terms are EVEN multiples of p: c mod p = m + 2r'; decrypt (c mod p) mod 2;
  correct while |noise| < p/4.
- Public key = many level-0 ciphertexts of ZERO (plus multiset in the original).

## The break to cite + reuse (Cheon–Stehlé, EUROCRYPT 2015 / eprint 2016/837)
- The original public-key construction leaks approximate multiples of p; CS15 shows the key can be
  SIMPLIFIED and recovers the secret from those near-multiples via an ACD-style lattice. The hardened
  variant applies the substitution x -> x^2 - 2 to the multiset (leveling) — challenges shipping
  UNSUBSTITUTED multsets are vulnerable to the 2010-paper flaw directly.

## CTF attack recipe
1. From pk pairs/differences: obtain y_i ≈ (multiple of p)/2^rho (rho = noise bits).
2. Build the ACD / Cohn–Heninger relation lattice over products of y's; LLL; read off the small vector ->
   combination of errors -> p (or gcd step).
3. p recovered -> m = (c mod p) mod 2 per ciphertext -> flag.
- Sanity gates: p must be ODD; verify decryption against a known/derived test vector before claiming.
- Parameter-regime honesty (D5 residual): correctness needs noise < p/4 and CS15's key-recovery succeeds
  when the pk leaks approximate multiples with rho below its bound — read eprint 2016/837 section 3 for the
  EXACT gamma/rho inequalities before asserting an instance is in the broken regime (no memorized number
  here on purpose: getting the regime wrong turns a real attack into 3 wasted hours).

## Canonical references
[R12] DGH, EUROCRYPT 2010, LNCS 6110. https://eprint.iacr.org/2009/616
[R15] Cheon–Stehlé, "FHE over the Integers Revisited", EUROCRYPT 2015. https://eprint.iacr.org/2016/837
- [R13/R14] ACD lattice machinery: skill approximate-common-divisor.

## Service variant: byte-wise DGHV toy with decrypt oracle (no public key at all)
Shape: per byte c = p*q + N*r + m with p a ~128-bit prime FIXED per session, decrypt oracle prints
(c mod p) mod N, N user-pickable in ~[2^7, 2^8), and an `add` menu item accumulates encryptions of
chosen messages. No lattice or gcd needed — the homomorphism overflow is the whole attack:
1. Per-add noise N*r < 2^126 < p/2, so between two decryptions the accumulator crosses a multiple
   of p AT MOST once. Encrypt ZERO bytes, add+decrypt until the first nonzero byte x: that crossing
   is exactly one wrap => x = (-p) mod N => p = N - x (mod N), k=1 exactly.
2. Multi-byte messages give independent per-position votes: all nonzero bytes of that first nonzero
   decrypt must yield the same residue — a vote split means transport desync, discard the round.
3. Repeat for many N (lcm of ~30 consecutive N in [128,256) already exceeds 2^128), CRT -> p,
   plaintext byte = (c mod p) mod N. Generalization for nonzero known plaintext m: observation is
   (sum(noise) + sum(m) - w*p) mod N with w bounded by total-noise/p; intersect per-step candidate
   sets of p mod N instead of the k=1 shortcut.
Pitfalls:
- The `new` menu action may already seed ONE encryption — the baseline decrypt can echo the message
  (w=0), not zeros; assert the baseline the source implies before deriving anything.
- Wrap-bound math must count EVERY encryption in the accumulator (the `new` one included) and keep
  the message term inside the sum — subtracting only noise silently poisons residues.
- Gates before claiming: p odd and in the stated bit range; recovered p must reproduce every
  observed decrypt value AND the known-plaintext bytes.
- This variant appears in archived CTF services (e.g. ctf_archive repo, folder `cscbe2024-additional-problems`
  ships the intended exploit.py under the original CTF's writeups repo) — locate it for post-derivation
  method verification only, per the campaign source policy.
