# AAR — Nativity (challenge-179-cryptohack-lwe-nativity)

LWE over **native integers** mod 2^16 (no field): pk = s*A + 2e (mod 2^16), A 512x64, 392 ciphertexts t = s*c (mod 2^16).

## Attack
Decryption computes `sk*c & 1` (parity) and `sk*c = msg + 2*sum(e_j y_j)` -> **the error vanishes mod 2**. Only `s mod 2` is needed: solve `t = s*A (mod 2)` over GF(2) (512x64 elimination) — no lattice at all; the 64 parity bits + per-ciphertext decryption yield the flag bytes.

## Result
**SOLVED** — `crypto{flavortext-flag-coprime-regev-yadda-yadda}` (submitted 2026-10-13, live-verified). Files: `_pq/nativity.py`, `_pq/public_key.txt`, `_pq/ciphertexts.txt`, `_pq/solve_nat.py` (working GF(2) solver).

_Backfill note (2026-10-14): this doc folder was created after the fact; all scripts/data referenced above live in `_pq/` and the flag was verified live on 2026-10-13._


## Vulnerability (plain words)
Regev built over the ring Z/2¹⁶ instead of a field. Two cracks follow from the modulus not being prime: (1) decryption itself computes ⟨sk, c⟩ mod 2, and since the error is introduced as 2·e it is *always even* — it vanishes under the very operation that reads the message, so only the parity bits of s carry information; (2) the public key pk = s·A + 2e (mod 2¹⁶) collapses the same way in public: pk ≡ s·A (mod 2), leaking linear equations in s mod 2 for free. Zero divisors of 2^k are the whole story ("native integers… yadda yadda").

## How the answer follows
1. Reduce the 512×64 public-key system mod 2: t_j ≡ ⟨s, A_j⟩ (mod 2) for all 512 rows. Over GF(2) the error term is identically zero, so this is a consistent 512-equation linear system in 64 unknowns; Gaussian elimination (any 64 independent rows suffice; the rest are consistency checks) yields **s mod 2** — and that is all decryption can ever use.
2. Decrypt each of the 392 ciphertexts with the parity vector: m = ⟨s mod 2, c⟩ & 1. Because sk·c = msg + 2·Σ(e_j y_j), the error sum is even, so the parity is exactly the message bit — no rounding, no noise window, exact answer.
3. Assemble flag bytes from the decrypted bits. No lattice, no noise estimation anywhere: the modulus mistake emptied the problem before any attack machinery was needed.
Result `crypto{flavortext-flag-coprime-regev-yadda-yadda}` (the "coprime" wording = the modulus-not-coprime-to-noise lesson), submitted 2026-10-13, live-verified.

## Limitations / attempts that failed
- Run logs do not record any aborted attempt to work over Z/2¹⁶ directly before switching to GF(2) (nor whether one was made); the GF(2) route is the recorded solve.

## Sources
- Server-provided `_pq/public_key.txt`, `_pq/ciphertexts.txt`; own solver `_pq/solve_nat.py`. No external writeup consulted.
