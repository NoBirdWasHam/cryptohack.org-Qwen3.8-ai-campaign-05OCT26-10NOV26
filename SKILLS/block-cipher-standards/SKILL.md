---
name: block-cipher-standards

description: Use for AES/Rijndael, differential, and mode-of-op misuse.
version: 1.0.0
author: GT
license: MIT
metadata:
  hermes:
    tags: [crypto, aes, ctf]
    related_skills: [gcm-padded-block-membership, ctf-padding-oracle, spn-fiber-coset-attack]
---

# Block cipher standards quick-facts (AES/GCM/differentials)

## When to Use
Challenge implements AES-adjacent primitives, asks spec trivia, or a mode misuse IS the attack.

## FIPS 197 (AES)
- Block 128 bits; keys 128/192/256 -> rounds 10/12/14. Byte state 4x4; rounds = SubBytes (AES S-box = affine
  over GF(2^8) composed with inversion), ShiftRows, MixColumns (mult by 03x^3+02x^2+02x+03 mod x^4+1 over
  GF(2^8), reduction poly 0x11b), AddRoundKey. Key schedule: RotWord/SubWord/Rcon per 4 words.
- The fixed S-box + GF structure is what 'S-box from scratch' challenges rebuild — when a challenge
  'replaces' MixColumns, invert its GF(2) matrix and algebraic attacks re-open (spn-fiber-coset-attack).

## Biham–Shamir differential cryptanalysis (J. Crypto 4(1), 1991)
- Characteristic = input-diff -> output-diff trail with probability; last-round trick peels the final round
  key by counting expected truncated-differential pairs.
- CTF scale: 4-6 round toy ciphers fall to programmatically built S-box DDTs — the max DDT entry IS the
  vulnerability statement; differential uniformity 2 = optimal (AES).

## Linear cryptanalysis (D16 residual, Biham–Shamir's dual — Matsui 1993 lineage)
- Linear characteristic: input mask · output mask held with prob p via piling-up lemma (round bias product
  form); best 4-round DES-style example in the original papers. Key-recovery: many known plaintexts ->
  majority vote on last-round key bits through the characteristic.
- AES defense numbers: differential uniformity 2 AND max linear bias 2^-6 for the S-box — a 6-round
  characteristic budget ≥ 2^-60ish is why classic LC stops below full AES; 'replaced S-box' challenges
  re-open it: compute the new S-box's distribution table (DDT AND linear structure table) programmatically.
- Distinguisher-mode thinking: if a characteristic gives p ≠ 1/2 by even 2^-20 over 6 rounds with 2^40 data,
  the challenge is asking for a distinguisher, not key recovery — check what the flag condition rewards.

## Modes as attack surface
- ECB: block-repetition oracle. CBC: padding oracles (skill ctf-padding-oracle). CTR/GCM nonce reuse:
  keystream XOR pair-read; GCM adds the GHASH polynomial forge (skill gcm-padded-block-membership; SP
  800-38D defines J0/GHASH/tag construction).

## Canonical references
[R24] FIPS 197. https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197.pdf
   NOTE (2026-11-02 citation check): original FIPS 197 (2001-11-26) was WITHDRAWN 2023-05-09 and superseded
   by FIPS 197-upd1, DOI 10.6028/NIST.FIPS.197-upd1 — editorial changes only, algorithm unchanged. Cite upd1.
[R25] SP 800-38D (GCM). https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
[R43] Daemen–Rijmen, The Design of Rijndael, Springer 2002.
[R44] Biham–Shamir, Differential Cryptanalysis of DES-like Cryptosystems, J. Crypto 4(1), 1991.
