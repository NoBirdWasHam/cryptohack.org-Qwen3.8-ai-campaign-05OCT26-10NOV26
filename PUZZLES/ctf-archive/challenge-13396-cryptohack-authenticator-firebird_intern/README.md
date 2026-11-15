# AAR — authenticator (Firebird Internal CTF) (CryptoHack ctf-archive)  ·  `challenge-13396-cryptohack-authenticator-firebird_intern`
- **Category:** ctf-archive · **Solved:** 2026-10-28 · **Status:** solved
- **Challenge:** https://cryptohack.org/challenges/authenticator-firebird-intern/
- **Flag:** mirrored + checksummed in `FLAGS/INDEX.jsonl` (provenance + sha256)

**Method (lead from the AAR):** 62P6 (~35.4-bit) no-repeat password is exhaustible in the 10 s alarm with a custom OpenCL blake3 single-block kernel (~15.6 GH/s) + Lehmer unranking + 64-bit digest-word filter; CPU-verify, answer R2.

**Skills exercised:** hash-collision-md5-engineering
**Concepts:** [fiat-shamir-forgery](../../../TAGS/fiat-shamir-forgery.md), [number-theory](../../../TAGS/number-theory.md)
**Scripts here:** see artifacts_2026-11-14/

Full record: [AAR.md](AAR.md)
