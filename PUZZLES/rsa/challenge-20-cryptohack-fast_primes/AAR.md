# AAR — Fast Primes (fast_primes, 75 pts, RSA)

## Result
SOLVED 2026-10-17. Flag: `[flag — recorded in FLAGS/rsa/challenge-20-cryptohack-fast_primes/flag.txt]`
Submit JSON: `{"submitted": "[flag — recorded in FLAGS/rsa/challenge-20-cryptohack-fast_primes/flag.txt]", "before": {"score": 8365, "solved": 172}, "after": {"score": 8440, "solved": 173}, "score_delta": 75}`

## Attack
The generator is the classic **ROCA** (Return Of the Coppersmith Attack) "fast prime" form:
`p = k*M + (65537^a mod M)` with `M = primorial(40)` (product of the first 40 primes, 227
bits), `k ∈ [2^28, 2^29)`, `a ∈ [2^20, 2^62)`. Both primes have this shape, so
`N mod M = 65537^(a+b) mod M` — N lands in the 67-bit-order subgroup
⟨65537⟩ of (Z/MZ)*. That structure is what makes the modulus enumerable/attackable, but for
THIS instance the practical path was the public factorization: the challenge's static N was
already in **FactorDB** (status `FF`), so the factors come directly from the API.

- p = 51894141255108267693828471848483688186015845988173648228318286999011443419469 (255 bits)
- q = 77342270837753916396402614215980760127245056504361515489809293852222206596161 (256 bits)

Then `d = 65537^-1 mod (p-1)(q-1)` and PKCS1-OAEP decryption of `ciphertext.txt` yields the
flag.

## Verification
- Commands:
  - `curl -s "https://factordb.com/api?query=$(cat n.txt)" -o fdb2.json` → `{"status":"FF","factors":[[p,1],[q,1]]}`
  - local check (venv python): `isPrime(p) and isPrime(q) and p*q == N` → all True
  - OAEP decrypt: `FLAG: [flag — recorded in FLAGS/rsa/challenge-20-cryptohack-fast_primes/flag.txt]`
- Server-accepted: `score_delta: 75`.

## Lessons
- "Resisted years of review" = ROCA was public since 2017; the generator is the exact
  Infineon TPM form. When a generator uses `k*M + f(a) mod M` with M a primorial, check
  whether `N mod M` falls in a small prime-base subgroup before engineering NFS.
- Before engineering SNFS/Coppersmith for a static challenge N, query FactorDB — a 2616-solve
  challenge's modulus is very likely already public. (The prior session's FactorDB attempt
  failed only because the URL redirected — use `https://factordb.com/api?query=<N>`.)
- Prior session's PARI NFS attempt (`nfinit(N)`) died on a type error — SNFS in PARI wants
  the special form explicitly, not a bare nfinit.

## Evidence
- `fast_primes.py` (provided generator), `key.pem`, `ciphertext.txt` (provided)
- `n.txt`, `fdb2.json` (FactorDB response with factors)
- `flag.txt` — exact submitted flag
- `fact.gp`, `nfs.gp`, `nfs_out.txt`, `factor_out.txt` — prior session's failed NFS attempts

## Sources
Sources: challenge-provided files (fast_primes.py, key.pem, ciphertext.txt) + public factorization, disclosed verbatim from the AAR: "the challenge's static N was already in FactorDB (status FF), so the factors come directly from the API." Self-derived otherwise per run logs.
