# Image Point Arithmetic (`c_group_homomorphism`)

- **Points:** 30
- **Category:** isogenies
- **Status:** SOLVED (live-verified 2026-10-13 via user API)
- **Solved:** None
- **URL:** https://cryptohack.org/challenges/isogenies/c_group_homomorphism/

## Statement (from challenge_meta.json)
--> As mentioned in the introduction, an isogeny is not only a rational map between curves, but also a map which preserves the group structure on these curves. This means that even if the isogeny $\phi : E \to E'$ is unknown, given $\phi(P)$ and $\phi(Q)$ one can determine the result of $\phi(P + Q)$. Something to think about: imagine you had access to an oracle which evaluated points under the action of an isogeny $\phi : E \to E'$. Could you use this to determine the kernel of the secret isogeny? To solve this challenge, compute the $x$-coordinate of the point $\phi(P + Q)$ given the following data, where $\phi : E \to E'$ is an isogeny between elliptic curves in the short Weierstrass model: $\phi(P) = (48622, 27709), \quad \phi(Q) = (9460, 13819), \quad p = 63079$ Resources: &nbsp; - Isogenies, Lecture Notes, Andrew Sutherland -->
