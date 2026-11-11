# FaILProof Revenge (SekaiCTF) — ctf-archive card

- Site slug: `failproof_revenge-sekaictf202` (truncated slug on cryptohack.org itself)
- Category: ctf-archive; 35 solves; 0 solutions listed on site
- Listener: archive.cryptohack.org 36813
- Files: Dockerfile_eea0d49a6cd85e8f87beb91e457b582b,
  ctf_4fd3271f12db04f35e077cd790c61caf.xinetd,
  source_7c25f48adb461fb9ccc05d43163b7ab7.py
- Author: deuterium
- Service behaviour (fingerprinted live, matches provided source exactly): connects,
  prints two lines (secret hex, then list of 7 blocks x 256 ints) and closes. No oracle.

## Scheme (source.py)
- secret = urandom(16); pubkey A = 256 chained sha512 states (512-bit ints)
- happiness(x) = popcount(x)
- per block: m = urandom(24) || flag_seg(8) || urandom(32) -> 512-bit int
- c_j = popcount(A_j & m), j=0..255
- prints secret.hex() and enc

## Family
Sibling: FaILProof (SekaiCTF 2022) had NO random padding (64-bit blocks, 256 eqs) —
plain linear solve. Revenge adds 448 random bits per block: each equation carries
~log2(sqrt(256)*~) ≈ 4-9 bits, so system is information-theoretically unique
(~2^1100 constraint bits on 2^512 solutions) => lattice CVP per block (Unfairhamming
style, textbook: HPS-based lattice methods; no third-party writeup used).
