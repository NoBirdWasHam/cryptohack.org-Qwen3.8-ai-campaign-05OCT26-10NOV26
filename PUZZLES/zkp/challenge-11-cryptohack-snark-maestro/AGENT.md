---
record: agent-aar
puzzle: challenge-240-cryptohack-snark-maestro
category: zkp
url: https://cryptohack.org/challenges/snark-maestro/
status: solved
date: 2026-10-23
flag_ref: "FLAGS/zkp/challenge-11-cryptohack-snark-maestro/flag.txt"
flag_sha256: 5a0724223700de16086107c804d2c3561aa58271b8931210c1b66a1d064870c3
skills: []
human_twin: AAR.md
---

# AGENT — 240-cryptohack-snark-maestro: Ticket Maestro (CryptoHack)
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "The setup (economics force the attack)" [OBSERVED text; evidence tag applies to its source, not each claim]
- Balance starts at 10. `BuyTicket` costs 2, `Redeem` of a fresh valid ticket pays +1,
  `BuyFlag` costs 20. Honest play: 10 − 5·2 + 5 = 5 < 20 → flag unaffordable.
- A ticket is a Groth16 proof (arkworks 0.3, BN254) that the prover knows a Poseidon
  preimage of the server `digest` (witness = secret, public input = digest).
- Ticket id = `blake2b(digest || serialized_proof)`; a `spent: HashSet` blocks
  re-redeeming the *identical* serialization.

## reusable-rules
- Groth16 proofs are malleable by construction; any system using the proof's
  serialization as a unique id (tickets, nullifiers) without re-randomization or
  canonicalization is double-spendable.
- Byte-exact roundtrip against a real artifact is the cheapest correctness oracle for
  reimplemented serialization formats; it caught the sign-convention bug for free.
- Pin exact crate versions from Cargo.toml (`ark-serialize =0.3.0`) and read the crate
  source instead of guessing — the compressed/uncompressed default changed between
  ark-serialize 0.3 and 0.4.

## anti-patterns / limits
- First live probe assumed uncompressed 256-byte proofs; the length assert caught it
  before any redeem was wasted (no BadTicket ever sent).
- A G2-generator sanity test initially failed due to swapped c0/c1 in my hardcoded
  generator — irrelevant to the attack (scalar mult never uses b), confirmed by
  re-testing with corrected coordinates.
- Did not attempt the irrelevant alternatives (extracting the Poseidon preimage or
  abusing circuit synthesis); malleability was sufficient and clearly intended.

## artifacts [OBSERVED]
- code: example.py, solve.py
- data/logs: flag_snark-maestro.txt, ticket0.json
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- Platform: CryptoHack, ZKP section (`snark-maestro`, 200 pts). The real challenge is
  the CTF-archive mirror `ticket_maestro-cryptohack2024` ("Connect at
  archive.cryptohack.org 26896"), whose card carries the provided files.
- Files downloaded from the archive card into this folder: `main.rs`, `maestro.rs`,
  `example.py`, `Cargo.toml`, `Dockerfile`.
- NOT consulted: `/challenges/*/solutions/` or `/solves/` pages, no third-party
  writeups (no-cheat rule).
