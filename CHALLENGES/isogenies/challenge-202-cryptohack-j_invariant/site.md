# The j-invariant (`j_invariant`)

- **Points:** 20
- **Category:** isogenies
- **Status:** SOLVED (live-verified 2026-10-13 via user API)
- **Solved:** None
- **URL:** https://cryptohack.org/challenges/isogenies/j_invariant/

## Statement (from challenge_meta.json)
--> Much like in modular arithmetic, where many computations are only equal up to an equivalence modulo N, in isogeny based-cryptography, many computations are only equal up to isomorphism. For two participants in a protocol, it's not enough to compare curve equations but instead they check whether two curves are isomorphic. One way of determining whether two curves are isomorphic is by comparing an invariant of the curve. For elliptic curves we use the "j-invariant", denoted $j(E)$, which is what we will be computing for this challenge. There is a subtle point here. If two curves are isomorphic, they have the same j-invariant, but if two curves have the same j-invariant they may not be isomorphic over the base field, but instead over some extension. An example of this is two curves related by a quadratic twist. The curves will have the same j-invariant but are only isomorphic over a quadratic extension. To grab the flag for this challenge, compute $j(E)$ of the supersingular curve: $E : y^2 = x^3 + 145 x + 49 \mod 163$ Resources: &nbsp; - Ordinary and supersingular elliptic curves, Section 13.2, Andrew Sutherland -->
