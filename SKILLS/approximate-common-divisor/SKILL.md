---
name: approximate-common-divisor
description: Use when a CTF hides an approximate common divisor.
---

# Approximate Common Divisor (ACD) — detection and lattice solve

## Recognition
Inputs of form c_i = p*x_i + r_i with |r_i| << p (often several INDEPENDENT approximate multiples of a
common hidden p): FHE-integer public keys, ACD-based cryptosystems, RSA-with-hints puzzles.

## Attack (Howgrave-Graham CaLC 2001 LNCS 2146 -> Cohn–Heninger ePrint 2011/437)
1. Products of SUBSETS of the c_i share the same leading p-product with additive error terms ->
   integer relations among products whose coefficient vectors hide the small errors.
2. Lattice: rows = those relations (Cohn–Heninger relation lattice); LLL/BKZ; a short vector gives an
   error combination -> gcd/p -> factor/decrypt.
3. Small instances (few inputs, tiny rho): brute-force combinations + gcd FIRST — one afternoon of code
   beats one week of lattice setup.
4. Verify: recovered p must reproduce |c_i mod p| = |r_i| within the stated bound for ALL inputs.

## Host engines
fpylll LLL/BKZ per ctf-lattices; Kannan embedding per gp-kannan-msp-cvp (AUTO_ABORT + spread-monitoring
pitfalls documented there apply).

## Decrypt-oracle variant (interactive DGHV-toy service) — no lattice needed
Recognition: an interactive service with `c = p*q + N*r + m`, a `decrypt` op printing
`(c mod p) mod N`, homomorphic ADD of ciphertexts, and attacker-chosen `N` in [128,256).
When the oracle exists, SKIP the lattice: in the eta-rho = 2 noise regime SDA/OL need dimension
> (gamma-rho)/(eta-rho) ~ 513 and the target norm still beats lambda1 — pure oracle algebra wins.
Recipe (verified end-to-end):
1. Read the server source for the RESET semantics: some `new` ops zero the accumulator AND
   immediately add one encryption, so the baseline decrypt echoes the message, not zeros.
2. Add a known L-byte message t times; per coordinate v = (M - w*p) mod N with each step's noise
   < N*rmax + m_max, so the wrap count obeys 0 <= w <= ceil(t*noise_max/p_min) — a SMALL tight
   bound, keep it exact (loose Kmax only slows the filter).
3. Each observation says d := (v - M) mod N must equal (-k*c) mod N for some k <= Kmax, where
   c = p mod N. Per coordinate solve k*c = -d mod N by modular division (g = gcd(k,N) | d, then
   c = base mod N/g, g lifts); intersect over the L coordinates AND over t-steps. Unique c
   within a few steps; skip ambiguous N.
4. Repeat for enough N; CRT (non-coprime-safe) until lcm >= 2^128 > p's range, so the residue
   IS p; verify all flag ciphertexts decode to printable. Plaintext byte = (c_i mod p) mod 128.
5. p is fixed PER CONNECTION: a mid-run reconnect invalidates every collected residue — reset
   pairs + re-read the fresh ciphertext block on reconnect (see cryptohack-socket-challenges).

## Canonical references
[R13] Howgrave-Graham, "Approximate Integer Common Divisors", CaLC 2001, LNCS 2146. https://cr.yp.to/bib/2001/howgrave-graham.pdf
[R14] Cohn–Heninger, "Approximate common divisors via lattices", ePrint 2011/437. https://eprint.iacr.org/2011/437
Related: fhe-integers-agcd (flagship consumer); coppersmith-vanishing-sanity (same small-root philosophy).
