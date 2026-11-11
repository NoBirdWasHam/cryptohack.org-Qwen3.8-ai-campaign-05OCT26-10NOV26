# Where's the Supersingular Curve (a_spot_super)

- **Platform:** CryptoHack (cryptohack.org)
- **Category:** Isogenies
- **Name:** Where's the Supersingular Curve
- **Points:** 25
- **Slug:** `a_spot_super`
- **Status:** SOLVED (2026-10-12) — flag = the A coefficient, +25 (score 6400 → 6425)

## Verbatim challenge statement
> "For the majority of this category (and all challenges at the time of writing) we
> are interested in computing isogenies between supersingular curves. Cryptographically,
> we are interested in supersingular elliptic curves because the ℓ-isogeny graph for
> supersingular elliptic curves are (ℓ+1)-regular graphs (each vertex on the ℓ-isogeny
> graph has ℓ+1 neighbours) as well as Ramanujan graphs with optimal expansion
> properties. Essentially this means it is easy to get lost walking randomly around the
> graph, and hard isogeny problems are based on the fact that knowing the beginning and
> end of these walks is not enough to recover the path itself. Mathematically, the name
> "supersingular" came from the fact that the endomorphism ring of these elliptic
> curves are "super-sized". They're not singular curves (all elliptic curves are
> non-singular!) but the "singularity" part of this comes from "special" (or rare)
> rather than singular in the geometric sense. In higher dimension we talk about
> superspecial abelian varieties and really this makes sense for elliptic curves too!
> These supersingular curves are very special and for very large characteristic,
> happening upon a supersingular curve is extremely unlikely (probability p^{-1}). An
> open problem is how to hash to a random supersingular curve! For this challenge there
> is a list of curves to pick from — can you identify the supersingular elliptic curve?
> Unironically, the wikipedia resource below is a great start and we've also included
> some lecture notes by Andrew Sutherland which are a fantastic resource. **The flag is
> the Montgomery coefficient A of the supersingular elliptic curve in the list of curves
> provided.**"

## Provided files
- `curves_1e476e7d608576c05a13b269d1481602.sage` (verbatim copy in this folder). It
  defines `p = 2**127 - 1`, a list of **100** `A_coefficients`, and builds
  `E = EllipticCurve(F, [0, A, 0, 1, 0])` for each — i.e. **Montgomery curves
  y² = x³ + A·x² + x over GF(p)**. Ends with: *"Can you find the supersingular curve?"*

## Resources (from the challenge page, NOT consulted as answers)
- Ordinary and supersingular elliptic curves, Section 13.2 — Andrew Sutherland
- Supersingular elliptic curve — Wikipedia
