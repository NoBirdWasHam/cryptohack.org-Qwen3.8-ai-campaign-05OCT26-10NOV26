# Site — Challenge 130: The Matrix Revolutions

- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category:** Diffie-Hellman (https://cryptohack.org/challenges/diffie-hellman/)
- **Name / points:** The Matrix Revolutions / 125 pts
- **Slug:** `matrix_revolutions` (folder `challenge-130-cryptohack-matrix_revolutions`)
- **Statement (verbatim):** "Everything that has a beginning has an end, Neo."
- **Provided files:** matrix_revolutions.zip → `matrix_revolutions.sage`, `generator.txt`,
  `alice.pub`, `bob.pub`, `flag.enc` (in `unzipped/`)
- **Status:** SOLVED + API-VERIFIED 2026-10-20 — flag `crypto{we_are_looking_for_the_keymaker_478415c4}` (score +125, solved 185→186)

## Protocol (from matrix_revolutions.sage)
150×150 matrix DH over GF(2): `A_pub = G^A`, `B_pub = G^B`, `shared = A_pub^B`,
key = SHA256(row-major bit string of shared)[:32], AES-256-CBC of the flag.
`charpoly(G) = f1·f2` with f1 = x^61+… (0x22acf905d0a8389f), f2 = x^89+… (0x2153c1dc23c09d789077799),
both irreducible, exponent 1 ⇒ F2[x]/charpoly ≅ GF(2^61)×GF(2^89), ord(G) = (2^61−1)(2^89−1)
(both Mersenne primes; x is a generator in each field).

## Attack
Krylov: express A_pub/B_pub as polynomials h(G) (deg<150); reduce h mod f1, f2 → targets
(`targets.json`). DLOG base x in GF(2^61) and GF(2^89) by index calculus (`ic6.c`), CRT the
logs → A, B mod ord(G); verify G^A==A_pub ∧ G^B==B_pub ∧ A_pub^B==B_pub^A; decrypt (`step3.py`).

See AAR.md for the full reproducible recipe + pitfalls.
