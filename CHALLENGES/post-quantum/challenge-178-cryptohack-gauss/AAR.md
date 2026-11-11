# AAR — Gaussian Reduction (challenge-178-cryptohack-gauss)

2D lattice-reduction puzzle: two vectors v=(846835985, 9834798552), u=(87502093, 123094980).

## Attack
Gauss reduction to the optimal (shortest, most orthogonal) 2D basis; the flag is the **inner product of the two optimal basis vectors** (BARE integer answer-type).

## Result
**SOLVED** — `7410790865146821` (submitted 2026-10-13, live-verified). Files: `_pq/gauss.sage`.

_Backfill note (2026-10-14): this doc folder was created after the fact; all scripts/data referenced above live in `_pq/` and the flag was verified live on 2026-10-13._


## Vulnerability (plain words)
None — algorithm drill: Gauss's 2-D lattice reduction. Teaching point: finding a shortest lattice vector is trivial in dimension 2 (Euclid-style reduction), and the whole difficulty of lattice cryptography is that this loop stops working in high dimensions.

## How the answer follows
Start with the given pair v = (846835985, 9834798552), u = (87502093, 123094980). Repeat until stable: (a) swap so v is the longer vector; (b) replace v ← v − round(⟨v,u⟩/‖u‖²)·u — subtract the *integer* multiple of u that comes closest to cancelling v (the nearest-lattice-line step, the exact analogue of Euclid's algorithm trading subtraction for division). Each step strictly shortens the pair, and when no pair-reduction shortens anything, the basis is the optimal 2-D one: v is a shortest nonzero vector of the lattice and the pair is size-reduced (angle as close to orthogonal as any lattice basis allows).
The asked flag quantity is the **inner product of the two vectors of that optimal basis** — asking for the pairing rather than the vectors makes a suboptimal (still-short-looking but wrong) basis give a different value. The reduction loop ran in `_pq/gauss.sage`; answer **7410790865146821**, submitted 2026-10-13, live-verified.

## Limitations / attempts that failed
- Run logs record the method and the accepted value but not the intermediate reduction steps (only the sage script itself holds them); nothing else failed / recorded.

## Sources
- Challenge statement (given vectors + question, per site.md) and own script `_pq/gauss.sage`. Course-recommended background: Hoffstein–Pipher–Silverman (Gauss reduction). No writeups consulted.
