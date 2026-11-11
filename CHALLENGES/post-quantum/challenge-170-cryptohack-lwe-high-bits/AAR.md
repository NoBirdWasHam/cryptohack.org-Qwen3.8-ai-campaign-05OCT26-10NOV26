# AAR — lwe-high-bits (CryptoHack Post-Quantum/LWE, 15 pts)

Date: 2026-10-14 · Status: SOLVED (server-verified, flag `201`)

## Result
Flag `201` (bare integer) accepted.

## Attack (3 lines)
1. The challenge generator `lwe-high-bits.sage` contains `print("S = ", S, "\n")` —
   the **secret key is leaked** in `output.txt` (n=64, p=257, q=65537, Δ=255, eb=127).
2. Compute x = (b − A·S) mod q = (44007 − 58415) mod 65537 → centered **−14408**,
   the exact integer Δ·m + e.
3. Solve m·255 + e = −14408 (mod 65537) with m ∈ [0,257), |e| ≤ 127:
   two candidates — (m=200, e=127) via k=−1 and (m=201, e=−126) via k=+1.
   x/Δ = −56.5019… sits 127 vs 128 from the two adjacent Δ-multiples: a **boundary
   instance** where naive round(x/Δ) decryption returns 200. The true message
   (server-accepted) is **m = 201** (e = −126).

## Verification
- A·S mod 65537 = 58415; b − A·S = −44008 mod 65537 → centered −14408 (exact integer
  identity, no wraparound per the problem's parameter choice |Δ·m+e| < q/2… here the
  sum 51255−126=51129 wraps once: 51129−65537 = −14408 ✓).
- Both candidates re-checked: |127| ≤ 127 ✓, |−126| ≤ 127 ✓.
- Server: `submit_flag.py lwe-high-bits 201` → accepted (flag recorded in
  progress.json queue).

## Lessons
- Toy LWE challenge scripts on CryptoHack often leak S in the printed output —
  always check what the generator prints before building any lattice attack.
- When Δ·m + e is within the error bound of a q-wraparound boundary, naive
  round(x/Δ) can be off by one; enumerate all (m,e) with |e| ≤ floor((q/p)/2)
  across both k=0 and k=±1 branches and try each candidate.

## Evidence
- `_pq/lwe-high-bits_a83f7bfc0f6e3bfd1b962842feb5d91d.sage` (generator)
- `_pq/lwe-high-bits_output.txt` (S, A, b — S leaked)
- This folder: site.md, flag.txt


## Vulnerability (plain words)
The challenge's own generator prints the secret key S into output.txt, so there is nothing to learn from samples at all. What remains — and what the challenge is actually about — is *decoding*: the value you decrypt sits right on the boundary between two admissible messages, so the naive rounding rule can pick the wrong one.

## How the answer follows
1. With S leaked, recompute the decryption residue exactly: x = (b − A·S) mod q = (44007 − 58415) mod 65537, centered to **−14408** = Δ·m + e, where Δ = q/p = 65537/257 = 255 and |e| ≤ eb = 127.
2. In the high-bits encoding the message rides on the *high* bits of the residue: x ≈ Δ·m, so decryption is "divide by Δ and round". Here x/Δ = −56.5019… lands 127 from one Δ-multiple and 128 from the next — exactly at the edge of the noise budget, so rounding is a coin-flip.
3. Enumerate instead of rounding: solve m·255 + e ≡ −14408 (mod 65537) over m ∈ [0,257), |e| ≤ 127. Exactly two pairs survive: (m=200, e=+127) on the k=−1 branch and (m=201, e=−126) on the k=+1 branch (51255 − 126 = 51129 wraps once: 51129 − 65537 = −14408 ✓).
4. Naive round(x/Δ) = −57 → −57 mod 257 = 200; the server-accepted truth is the wraparound candidate **m = 201**.

## Limitations / attempts that failed
- The run logs record the boundary ambiguity and the two surviving candidates, but do **not** record that candidate 200 was submitted and rejected; the tie between the two in-bounds candidates was broken only by the server.
- No lattice/learning attack was attempted — the S leak made it moot; whether one was considered is not recorded.

## Sources
- Provided challenge files: generator `_pq/lwe-high-bits_a83f7bfc0f6e3bfd1b962842feb5d91d.sage` (its `print("S = ", S)` is the leak) and `_pq/lwe-high-bits_output.txt` (S, A, b).
- Course-recommended background: Hoffstein–Pipher–Silverman (LWE encoding/decoding ranges). No third-party writeups consulted.
