# From Private to Public Key LWE — CryptoHack / Post-Quantum (LWE) (25 pts)

slug: `lwe-private-public` · category: post-quantum (server card: Lattices → LWE) · points: 25
Solved: 2026-10-14 · flag: `1568` (bare integer, server-verified)

## Statement (verbatim from category page)
This can be turned into a public key cryptosystem by using the "additively
homomorphic" property of LWE. Given an encryption ⟨A,b⟩ of m, anyone can form an
encryption of m+m₂ by ⟨A, b+m₂⟩ (low-bit) or ⟨A, b+Δ·m₂⟩ (high-bit); adding two
LWE ciphertexts encrypts the sum. The owner releases many "encryptions of zero" as
the public key; Alice picks a random subset, sums them (encryption of zero), adds
her encoded message. Security requires the noise distribution to keep the final
error below the decryption threshold, and it must be hard to tell which samples
were summed — so the public key needs significantly more encryptions of zero than
the LWE dimension, scaling as O(n² log q) bits, making LWE public keys large.
**What is the size of a Kyber1024 public key in bytes?** (Contributed by irel.)

## Answer
**1568** — the NIST-standard Kyber1024 (ML-KEM-1024) public key size in bytes.
