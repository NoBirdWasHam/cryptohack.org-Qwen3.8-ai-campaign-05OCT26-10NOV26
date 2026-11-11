# LWE High Bits Message — CryptoHack / Post-Quantum (LWE) (15 pts)

slug: `lwe-high-bits` · category: post-quantum (server card: Lattices → LWE) · points: 15
Solved: 2026-10-14 · flag: `201` (bare integer, server-verified)

## Statement (verbatim from category page)
Now we're going to jump in and decrypt a message that's hidden in the high bits of a
toy LWE system. Parameters: vector space dimension $n$, ciphertext modulus $q$,
plaintext modulus $p$ (can only encrypt messages $m \in [0,p)$), scaling factor
$\Delta = \text{round}(q/p)$. Key-gen: $S$ random in $\mathbb{Z}_q^n$. Ciphertext
$(A, b)$ with $A$ random, $e \in [-\Delta/2, \Delta/2]$, $b = \langle A,S\rangle +
\Delta m + e$. Decryption: $x = b - \langle A,S\rangle \bmod q$ interpreted as an
integer; $m = \text{round}(x/\Delta)$. In this system, after the mask is removed the
equation $\Delta m + e$ holds over the integers (no modular wraparound due to $q$),
so removing $e$ is integer-division rounding. Files: `lwe-high-bits.sage`,
`output.txt`. (Contributed by irel.)

## Instance parameters (from files)
n = 64, p = 257, q = 0x10001 = 65537, Δ = round(65537/257) = 255, error_bound = 127.

## Answer
**201** — see AAR.md. The challenge script *prints the secret S* in `output.txt`
(a bug); then the boundary-ambiguous decode yields m = 201 (e = −126).
