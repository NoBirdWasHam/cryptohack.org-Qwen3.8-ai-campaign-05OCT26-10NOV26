# AAR — d-phi-enc (HackTM CTF 2023)

## Vulnerability
RSA with e=3 leaks `enc_phi = phi^3 mod n` and `enc_d = d^3 mod n`. Since
`getStrongPrime(1024, e=3)` guarantees gcd(3, phi)=1, the cube map is a
bijection mod p and mod q (no nontrivial cube roots of unity in either
field). That makes phi the *unique* common root mod n of two small-degree
polynomials, which can be found without factoring first.

## Attack
From `3d = 1 + k·phi` with k ∈ {1,2} (d < phi ⇒ k < e = 3):
- `g(x)  = x^3 − enc_phi` vanishes at phi (bijectivity ⇒ unique root mod n).
- `f_k(x) = (kx+1)^3 − 27·enc_d` vanishes at phi over Z (since 27d³=(kφ+1)³),
  and again bijectivity ⇒ phi is its unique root mod n.

Reduce f_k using x³ ≡ enc_phi to the quadratic
`q2(x) = 3k²x² + 3kx + (1 + k³·enc_phi − 27·enc_d) mod n`,
then run Euclidean GCD of q2 and g over Z/n[x] (all pivots checked
invertible; a non-invertible pivot would itself leak a factor). For the
true k the gcd is `x − phi`. Here **k = 2**.

Then: `p+q = n − phi + 1`, `disc = (p+q)² − 4n` perfect square ⇒ factor;
verify `(p−1)(q−1) == phi` and `3d − 1 == k·phi`; decrypt with d.

## Key numbers
- 2048-bit n; recovered phi exactly, factorization verified; k=2.
- Flag: `HackTM{Have you warmed up? ...}` — full string in
  flag_d-phi-enc-hacktm_ctf2023.txt.

## Verification / provenance
- Flag derived end-to-end by this script; no writeups, no repo, no websearch.
- Pipeline fuzzed on 6 self-generated ground-truth instances (small primes,
  gcd(3,phi)=1) — recovered phi exactly in all 6 before touching live data.
- Live checks: pow(phi,3,n)==enc_phi, p·q==n, (p−1)(q−1)==phi, decrypted
  bytes == 255-char ASCII flag; submit ok:true, solved 284→285
  (score_delta 0 expected for archive challenges).

## Limitations
- Nothing failed. Only note: initial `poly_mod` had an off-length indexing
  bug for deg(a)>deg(b) caught by padding fix before any live run.
- Generalization (the flag itself taunts this): for e=65537 the same trick
  needs a common-root gcd between x^e−enc_phi and (ex−...)... actually a
  degree-e gcd — still polynomial-time, but k ranges over 1..e−1 so you'd
  search ~65537 candidates; enc_d may not even be needed.

## Files
solve.py (runnable, writes flag file), chall.py, output.txt, statement.txt,
site.md, flag_d-phi-enc-hacktm_ctf2023.txt.

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
