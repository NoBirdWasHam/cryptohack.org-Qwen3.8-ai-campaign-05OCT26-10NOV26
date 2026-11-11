# AAR — lwe-low-bits (CryptoHack Post-Quantum/LWE, 20 pts)

Date: 2026-10-14 · Status: SOLVED (server-verified, flag `147`)

## Result
Flag `147` (bare integer) accepted.

## Attack (3 lines)
1. Same leak as high-bits: the generator prints **S** in `output.txt`
   (n=64, p=257, q=65537, eb=127).
2. x = (b − A·S) mod q, centered → **−881** = m + 257·e, |e| ≤ 127.
3. e = (−881 − 147)/257 = −4 is the unique in-bounds solution → **m = 147**.

## Verification
- A·S mod 65537 computed from the 64×64 dot product; b = 11507; centered x = −881.
- m = x mod 257 = 147; check e = (x − m)/257 = −4 ∈ [−127, 127] ✓.
- Uniqueness: x + 257·e with e ∈ [−127,127] spans [−33624, 31856]; only e = −4 gives
  m in [0, 257) (e = −3 would need m = 147−257 < 0; e = −4 is the only lattice point
  with m ∈ [0,257)).
- Server: `submit_flag.py lwe-low-bits 147` → accepted.

## Lessons
- Low-bits variant is cleaner than high-bits: m = x mod p is directly unique when
  |e| < p/2… (here |e| ≤ 127 < 128 = p/2, so uniqueness holds).
- Reuse: identical S-leak pattern to lwe-high-bits.

## Evidence
- `_pq/lwe-low-bits_a2c45284086e181a601486fe22f873ff.sage` (generator)
- `_pq/lwe-low-bits_output.txt` (S, A, b — S leaked)
- This folder: site.md, flag.txt


## Vulnerability (plain words)
Identical to lwe-high-bits: the generator prints the secret key S in the provided output.txt, so no learning problem survives. The residual puzzle is just decoding the residue into (message, error) under the noise bound.

## How the answer follows
1. Same leak, same parameters (n=64, p=257, q=65537, eb=127). Recompute the decryption residue with the known S: x = (b − A·S) mod 65537, centered → **−881**.
2. The low-bits encoding puts the message in the *low* base-p digit: x = m + p·e with m ∈ [0,257), |e| ≤ 127. So m = x mod 257 = (−881) mod 257 = **147**, and the implied error is e = (x − m)/257 = (−881 − 147)/257 = **−4**, which satisfies |−4| ≤ 127 ✓.
3. Why the low digit is trustworthy here: the error must be tiny compared to p (|e| ≤ 127 < 128 ≈ p/2), so e·257 is a multiple of p and contributes nothing to x mod p — the residue's low digit *is* the message, and the representation is unique (only e = −4 puts m in [0,257)). Clean contrast with high-bits, where the same check sat on a rounding boundary.

## Limitations / attempts that failed
- Nothing failed; direct computation, recorded in one pass. The S leak removed the learning task — no lattice or sample-combination attack was attempted (nor needed).

## Sources
- Provided challenge files: `_pq/lwe-low-bits_a2c45284086e181a601486fe22f873ff.sage` (generator, prints S) and `_pq/lwe-low-bits_output.txt` (S, A, b).
- Course-recommended background: Hoffstein–Pipher–Silverman. No third-party writeups consulted.
