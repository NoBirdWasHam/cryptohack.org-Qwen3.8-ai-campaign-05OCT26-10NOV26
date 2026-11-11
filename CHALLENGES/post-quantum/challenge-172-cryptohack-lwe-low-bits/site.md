# LWE Low Bits Message — CryptoHack / Post-Quantum (LWE) (20 pts)

slug: `lwe-low-bits` · category: post-quantum (server card: Lattices → LWE) · points: 20
Solved: 2026-10-14 · flag: `147` (bare integer, server-verified)

## Statement (verbatim from category page)
Now we're going to jump in and decrypt a message that's hidden in the low bits of a
toy LWE system. The noise is stored in the high bits. Parameters: vector space
dimension $n$, ciphertext modulus $q$, plaintext modulus $p$ (messages $m \in [0,p)$),
$q$, $p$ coprime. Key-gen: $S$ random in $\mathbb{Z}_q^n$. Encryption: $A$ random,
$e \in [-(q/p)/2, (q/p)/2]$, $b = \langle A,S\rangle + m + p\cdot e$. Decryption:
$x = b - \langle A,S\rangle$ centered modulo $q$ (in $(-q/2, q/2]$), $m = x \bmod p$.
Files: `lwe-low-bits.sage`, `output.txt`. (Contributed by irel.)

## Instance parameters (from files)
n = 64, p = 257, q = 0x10001 = 65537, error_bound = floor((q/p)/2) = 127.

## Answer
**147** — see AAR.md. S is leaked in the output; centered x = −881 = 147 + 257·(−4)
→ m = 147 (unique).
