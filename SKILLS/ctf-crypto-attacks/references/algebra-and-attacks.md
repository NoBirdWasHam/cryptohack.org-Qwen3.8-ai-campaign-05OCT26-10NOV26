# Crypto CTF foundations — number theory, attacks, and the algebra behind them

Environment-independent reference. Maps each attack family to the algebraic property it
exploits. (Distilled from a standard crypto-CTF cheat sheet; verify anything load-bearing
against a primary source before trusting it in a solve.)

## I. Number theory foundations
- Modular arithmetic + extended Euclid (`xgcd`, or `pow(a,-1,n)` which also yields Bezout coeffs).
- Fermat: a^(p-1)=1 mod p; Euler: a^φ(n)=1 mod n. Order of an element divides group order (Lagrange).
- CRT: combine congruences — basis of broadcast attacks and multi-prime RSA.
- Legendre/Jacobi: (a|p)=a^((p-1)/2) mod p; Jacobi −1 certifies non-residue (used in Goldwasser, Rabin).
- DLP: basis of DH/ElGamal/ECC.

## II. RSA attack → condition map
| Attack | Condition exploited |
|---|---|
| e=3 no-padding / Hastad broadcast | m^e < n, or same m to ≥e recipients |
| Wiener | d < n^0.25 (continued fractions on e/n) |
| Common modulus | same n, gcd(e1,e2)=1, same m |
| Fermat factor | \|p−q\| small |
| Pollard p−1 | p−1 smooth |
| Coppersmith | small roots of poly mod factor (partial key/message) |
| Bleichenbacher | PKCS#1 v1.5 padding oracle |
| Shared prime | gcd(n1,n2) ≠ 1 |
| d-work / φ known | ed ≡ 1 mod λ(n); from φ(n) factor via x²−(n−φ+n−1)x+n |

## III. Discrete log / DH / ElGamal
- BSGS: O(√n) generic. Pohlig-Hellman: fast when group order is smooth (per prime-power + CRT).
- Index calculus: subexponential in F_p (not ECC).
- Small-subgroup confinement: force secret into small-order subgroup, leak mod each factor, CRT.
  Requires the target to accept unvalidated parameters; check p−1 factorization of YOUR chosen p.
- Key trick (dh_static2-style): PH works with any MULTIPLE of the order, not the exact order:
  gi=g^{N/pe}, hi=B^{N/pe} ⇒ b mod pe for each pe | smooth part of N.

## IV. Elliptic curves
- Group law; E(F_p) ≅ Z/n1 × Z/n2, n2 | n1, n2 | p−1; Hasse: |#E−(p+1)| ≤ 2√p.
- Singular curve (4a³+27b² ≡ 0): group collapses to (F_p,+) or F_p* → ECDLP trivial.
- Anomalous (#E = p): Smart/Satoh-Araki p-adic lift → additive DLP.
- Smooth #E: Pohlig-Hellman on the curve. Supersingular (t=0, #E=p+1): MOV/transfer via pairing.
- Invalid curve: send point off-curve → small subgroup of the twist.
- ECDSA nonce reuse: k reused ⇒ s1−s2 = k(x1−x2)… leaks key algebraically.

## V. Symmetric
- ECB: pattern + block-cut-and-paste. CBC: IV-bitflip; padding oracle (PKCS#7) full decrypt.
- CTR/GCM: nonce reuse ⇒ keystream XOR (CTR) or total forgery via H=S² recovery (GCM).
- XOR: self-inverse; OTP reuse ⇒ crib-drag.
- Meet-in-the-middle: double encryption 2^k not 2^2k.

## VI. Hashes & MACs
- Merkle–Damgård length extension (MD5/SHA-1/SHA-256 without HMAC): append data + recompute;
  needs len(secret)+msg known (hashpump pattern).
- Birthday bound 2^(n/2); HMAC's inner/outer padding defeats length extension.

## VII. PRNGs
- LCG: recover modulus/multiplier from consecutive outputs (differences lattice / standard 3-output trick).
- MT19937: 624 consecutive 32-bit outputs ⇒ full state (randcrack); tempered outputs invert per-word.
- Truncated/partial outputs: lattice or untwist with leaked low bits.

## VIII. Lattices
- LLL: polynomial-time short/reduced basis. Uses: Coppersmith, hidden number problem, partial
  keys, knapsack (low density), NTRU/LWE.
- Kannan embedding for CVP; Babai nearest-plane after LLL for small noise.
- Scaling balance matters: coordinate magnitudes must be comparable or the target isn't shortest.

## IX. Groups (the algebra)
- Axioms: closure, associativity, identity, inverse. Abelian ≈ everything in crypto.
- Lagrange: |H| divides |G|. Cauchy: prime p | |G| ⇒ element of order p.
  ⇒ Factoring |G| (or p−1, or #E) tells you WHICH subgroup attacks exist.
- Cyclic ⟨g⟩; order of g = least k with g^k=e; generator order = |G|.
- Cosets/normal/quotient G/H; homomorphism f(ab)=f(a)f(b); isomorphism = same structure
  (anomalous-curve attack is an isomorphism E(F_p) → (Z/p,+)).
- Cofactor: #E = h·n; h>1 composite ⇒ small-subgroup exposure.
- Key groups: (Z/n,+); (Z/n,Z)* order φ(n), cyclic iff n=1,2,4,p^k,2p^k; GF(q)* always cyclic
  order q−1; E(F_p) abelian, not always cyclic; RSA group ≅ product via CRT.

## X. Rings & fields
- Ring: (+,·), (R,+) abelian; integral domain: no zero divisors; field: every nonzero invertible.
- Zero divisors in Z/nZ exist iff n composite — why RSA's Z/nZ is not a field (and why gcd
  shortcuts sometimes factor n).
- Units R*; ideals → quotient rings; GF(p^k) = F_p[x]/(irreducible f) — ideal quotient.
- NTRU ring Z[x]/(x^N−1) = ideal lattices. AES = GF(2^8) with x^8+x^4+x^3+x+1.
- GF(q)* cyclic ⇒ DLP well-defined over finite fields.

## XI. Polynomial rings / extensions
- Irreducible = prime analogue; extension arithmetic = poly arithmetic mod f.
- F_{p^k} sqrt: x^((q+1)/4) needs q≡3 mod 4 — for q=p² (≡1 mod 4) use Tonelli-Shanks over
  the extension, and search non-residues in F_{q}, NOT F_p (every F_p element can be a
  residue in F_{p²} — infinite-loop trap).

## XII. Sage quick reference
```
ZZ QQ Zmod(n) GF(p) GF(p^k,'a') R.<x>=PolynomialRing(GF(p))
G=Zmod(n).unit_group(); a.multiplicative_order(); g.is_primitive_root()
gcd(a,b) xgcd(a,b) factor(p-1) is_prime(p)
E=EllipticCurve(GF(p),[a,b]); E.order() E.gens() P.order()
M=Matrix(ZZ,[[1,a],[0,n]]); M.LLL()
```
No local Sage: SageCell (sagecell.sagemath.org) speaks SockJS — POST /sockjs/kernel/info,
then wss execute; ~40 s CPU/cell, no state between cells (prepend setup), retry on kernel_dead.
