# AAR — 240-cryptohack-snark-maestro: Ticket Maestro (CryptoHack)

**Result:** SOLVED — flag `crypto{m4ll34b1l1ty_fl4w_0r_r3r4nd0m1s4t10n_f34tur3?}`
**Submitted:** ok:true, score_delta +200 (14775 → 14975), 2026-10-23
**Account:** NoBirdWasHam

## Source
- Platform: CryptoHack, ZKP section (`snark-maestro`, 200 pts). The real challenge is
  the CTF-archive mirror `ticket_maestro-cryptohack2024` ("Connect at
  archive.cryptohack.org 26896"), whose card carries the provided files.
- Files downloaded from the archive card into this folder: `main.rs`, `maestro.rs`,
  `example.py`, `Cargo.toml`, `Dockerfile`.
- NOT consulted: `/challenges/*/solutions/` or `/solves/` pages, no third-party
  writeups (no-cheat rule).

## The setup (economics force the attack)
- Balance starts at 10. `BuyTicket` costs 2, `Redeem` of a fresh valid ticket pays +1,
  `BuyFlag` costs 20. Honest play: 10 − 5·2 + 5 = 5 < 20 → flag unaffordable.
- A ticket is a Groth16 proof (arkworks 0.3, BN254) that the prover knows a Poseidon
  preimage of the server `digest` (witness = secret, public input = digest).
- Ticket id = `blake2b(digest || serialized_proof)`; a `spent: HashSet` blocks
  re-redeeming the *identical* serialization.

## The vuln: Groth16 proof malleability
The verifier (`ark_groth16::Groth16::verify`) checks only the single pairing product

    e(A, B) == e(alpha,beta) · e(L, delta) · e(C, gamma)

A appears only inside e(A,B), and B likewise. So for any r ∈ F_r*:

    (A', B', C') = (r·A, r⁻¹·B, C)   ⇒   e(A',B') = e(A,B)

is a valid proof of the *same* statement (same public input = digest), yet its
compressed serialization differs → different Blake2b id → `spent.insert` succeeds → +1.
No trapdoor, no Poseidon preimage, no DLOG needed. This is the classic Groth16 proof
malleability (noted in Groth16 itself); real systems mitigate by re-randomizing at
issue time, hashing proofs into the statement, or binding ids to the witness.

## Attack
1. `BuyTicket` once (balance 10→8), `Redeem` it (→9).
2. For 11 fresh random r: parse the bought proof, A' = r·A on G1, B' = r⁻¹·B on G2
   (pure-Python affine double-and-add; the group law never uses the curve b, so no
   pairing/twist library is needed), keep C, re-serialize, `Redeem` → +1 each.
   Balance 9→20.
3. `BuyFlag` → flag.

## Key implementation detail (where the time went)
- Proofs are 128 bytes = ark-serialize **0.3.0 compressed** format (not the 256-byte
  uncompressed format first assumed): G1 = x (32 B LE) with SWFlags in the top 2 bits
  of the last byte (bit7 = "y > −y", bit6 = infinity); G2 = x.c0 ‖ x.c1 with flags on
  the last byte of c1.
- y-recovery mirrors `get_point_from_x`: keep sqrt(x³+b) iff `(y < −y) XOR positive`.
  I initially inverted that XOR and got flag-bit mismatches on roundtrip — caught by a
  byte-exact roundtrip test against a real ticket before any forge was attempted.
- Fq2 ordering in ark-ff 0.3.0 compares **(c1, c0) lexicographically** (not c0-first) —
  this decides the G2 sign flag. Fq2 sqrt = the "complex method" (eprint 2012/685,
  Alg. 8), copied from `quadratic_extension.rs`.
- Verified parse→serialize byte-identical to a live ticket, then forged.

## Learning points
- Groth16 proofs are malleable by construction; any system using the proof's
  serialization as a unique id (tickets, nullifiers) without re-randomization or
  canonicalization is double-spendable.
- Byte-exact roundtrip against a real artifact is the cheapest correctness oracle for
  reimplemented serialization formats; it caught the sign-convention bug for free.
- Pin exact crate versions from Cargo.toml (`ark-serialize =0.3.0`) and read the crate
  source instead of guessing — the compressed/uncompressed default changed between
  ark-serialize 0.3 and 0.4.

## Limitations
- First live probe assumed uncompressed 256-byte proofs; the length assert caught it
  before any redeem was wasted (no BadTicket ever sent).
- A G2-generator sanity test initially failed due to swapped c0/c1 in my hardcoded
  generator — irrelevant to the attack (scalar mult never uses b), confirmed by
  re-testing with corrected coordinates.
- Did not attempt the irrelevant alternatives (extracting the Poseidon preimage or
  abusing circuit synthesis); malleability was sufficient and clearly intended.

## Artifacts
- `solve.py` — full attack (pure stdlib; no py_ecc needed).
- `flag_snark-maestro.txt` — the flag.
- `main.rs`, `maestro.rs`, `example.py`, `Cargo.toml`, `Dockerfile` — provided files.
- `ticket0.json` — a live ticket used for roundtrip validation.

## Configuration (environment for this run)
- Host OS: Windows 11, shell = git-bash/MSYS; user OWNER
- Interpreter: plain `python3` (stdlib only for the attack)
- Working dir: `~\Practice_runs\cryptohack_org\challenge-240-cryptohack-snark-maestro`
- Submission: `python3 submit_flag.py snark-maestro "<flag>"` → ok:true, +200
- Network: archive.cryptohack.org:26896 (JSON-line protocol) / cryptohack.org HTTPS

## Sources
Provided materials only: challenge statement/card, files provided with the challenge, and direct interaction with the challenge service. The AAR records no third-party solutions/writeups or answer artifacts consulted (no-cheat rule); derivation self-derived.
