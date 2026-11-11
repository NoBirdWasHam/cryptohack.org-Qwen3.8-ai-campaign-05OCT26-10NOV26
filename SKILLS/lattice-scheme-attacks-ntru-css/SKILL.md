---
name: lattice-scheme-attacks-ntru-css
description: Use on NTRU or partial-key-exposure lattice CTFs.
---

# NTRU + partial-key-exposure lattice attacks

## NTRU (Hoffstein–Pipher–Silverman, ANTS 1998, LNCS 1423)
- Keys: small f,g (coeffs ~{-1,0,1}); public h = g*f^{-1} mod q in R = Z[x]/(x^n-1).
- Private-key recovery = SHORT vector (f, f*h - g-ish) in the 2n-dim NTRU lattice
  L = {(a,b) : a ≡ b*h mod q}, det q^n: LLL/BKZ on the standard 2n basis; CVP variant for decryption
  (Coppersmith–Goldwasser / Babai nearest-plane era). fpylll engines: ctf-lattices skill.
- CTF instances are dim-chosen-small: plain LLL usually returns (f, hf+r) outright — if not, re-check the
  embedding BEFORE brute-forcing BKZ harder.
- Inversion sanity: f invertible mod p AND mod q (invert mod p, Hensel/Newton-lift to q — see padic skill
  for lift hygiene).

## Partial key exposure + cold boot (Cheon–Stehlé, CRYPTO 2010, LNCS 6223)
- Setting: attacker holds PART of the secret (MSIS-with-partial-info; GPV/HFE cold-boot surviving bits).
- Attack = substitute known coordinates and solve the SHRUNKEN unknown-coordinate lattice (CVP target =
  public equation minus known part); same paper covers the RSA partial-hint Coppersmith case — see
  coppersmith-vanishing-sanity.

## Canonical references
[R17] HPS, "NTRU: A Ring-Based Public Key Cryptosystem", ANTS 1998, LNCS 1423. https://www.ntru.org/f/hps98.pdf
[R16] Cheon–Stehlé, CRYPTO 2010, LNCS 6223 (partial key exposure; cold-boot on GPV).
