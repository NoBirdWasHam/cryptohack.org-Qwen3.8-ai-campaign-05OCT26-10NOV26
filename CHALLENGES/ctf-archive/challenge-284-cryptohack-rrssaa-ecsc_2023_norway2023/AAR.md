# AAR — RRSSAA (ECSC 2023 Norway) — challenge-284

## Result
SOLVED. Flag self-derived from provided output.txt and math only; verified two ways:
`pow(m,e,N) == c` (full ciphertext consistency) and `len(flag) == 128`. Site accepted
(ok:true, solved count 275→276; archive challenges carry 0 points, score_delta 0).

## Vulnerability
N = product of 126 RSA-style primes, where the i-th prime comes from a fresh
`random.Random()` seeded with `secrets.randbelow(2**i)`, i = 2..127, drawing
`_randbelow(2**256) | 1` until prime. e = 65537, flag = 128 bytes.
Two flaws stack:
1. For small i the seed space is tiny (seed < 2^i) → those primes are reproducible by
   re-seeding MT19937 and replaying the draw loop.
2. The flag (1024 bits) is far smaller than N (~32k bits), so you don't need the full
   factorization: ~5 prime factors with product P > 2^1024 suffice. Since P | N,
   m^e ≡ c (mod P), gcd(e, φ(P)) = 1, and m < P, RSA-decrypt mod P gives m exactly.

## Attack
Single scan of seeds s in [0, 2^14): for each s, replicate `r.seed(s)` + rejection loop
→ candidate p; keep p if N % p == 0. Provably recovers every factor with index i ≤ 14
(seed < 2^i ≤ 2^14). Found 15 distinct primes; chose largest 5 (product > 2^1024, each
p−1 coprime to e), d = e^{-1} mod φ(P), m = c^d mod P → flag.

Flag format: ECSC{...}.

## Key numbers
- Scan: 2^14 seeds ≈ 3 min, pure Python + PyCryptodome isPrime.
- Primes found: 15 distinct (indices i ≤ 14 guaranteed + lucky larger-i hits,
  e.g. seed 13937 for some i ≥ 14).
- Subset used: 5×256-bit primes → P ≈ 2^1280 > m.

## Pitfalls / learning points
- Brute-forcing per-index (seed < 2^i, break on first N % p == 0) fails: seed 0's prime
  divides N and masks every index's real seed. Fix = one global seed scan, no break.
- Partial factorization + partial CRT works whenever message ≪ modulus — check message
  size before attempting full factorization.

## Limitations
- Nothing failed mathematically; first two script iterations were the per-index break
  bug and an insufficient-subset assert, both fixed above.
- No listener involved; no interaction-side evidence needed.

## Files
- RRSSAA.py, output.txt (provided), card.html, statement.txt, site.md
- solve.py (final, runnable), solve2 run log: run2.log
- flag_rrssaa-ecsc_2023_norway2023.txt

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
