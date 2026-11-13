---
record: agent-aar
puzzle: challenge-102-cryptohack-fast_primes
category: rsa
url: https://cryptohack.org/challenges/fast_primes/
status: solved
date: 2026-10-17
flag_ref: "FLAGS/rsa/challenge-102-cryptohack-fast_primes/flag.txt"
flag_sha256: 29d2ebd2504272d1ce21fd977e0a17462f5d61e2bbe381a1a51ca470c754b053
skills: []
human_twin: AAR.md
---

# AGENT — Fast Primes (fast_primes, 75 pts, RSA)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
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

## reusable-rules
- none recorded [NOT OBSERVED] — derive from procedure above

## anti-patterns / limits
- none recorded [NOT OBSERVED]

## artifacts [OBSERVED]
- code: fact.gp, factor.gp, fast_primes.py, nfs.gp
- data/logs: ciphertext.txt, factor_out.txt, fdb2.json, nfs_out.txt
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
Sources: challenge-provided files (fast_primes.py, key.pem, ciphertext.txt) + public factorization, disclosed verbatim from the AAR: "the challenge's static N was already in FactorDB (status FF), so the factors come directly from the API." Self-derived otherwise per run logs.
