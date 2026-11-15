# AAR — fischlins_transformation (CSC Belgium) (CryptoHack ctf-archive)  ·  `challenge-260-cryptohack-fischlins_transformation-cryp`
- **Category:** ctf-archive · **Solved:** 2026-10-25 (own derivation 2026-11-14 audit run) · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/fischlins-transformation-cryp/
- **Flag:** mirrored + checksummed in `FLAGS/INDEX.jsonl` (provenance + sha256)

**Method (lead from the AAR):** b=0 replay of the prover's Fischlin-OR search path: recompute z0' for every e'<=e_cur and check the 506-bit RO window — exact reproduction = b=0 (posterior (63/64)^(e_cur+1)), any deviation = certain b=1. 64/64 rounds.

**Skills exercised:** zkp-fiat-shamir-ctf
**Concepts:** [fiat-shamir-forgery](../../../TAGS/fiat-shamir-forgery.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** see artifacts_2026-11-14/

Full record: [AAR.md](AAR.md)
