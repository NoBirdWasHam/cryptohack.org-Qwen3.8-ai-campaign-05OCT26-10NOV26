# AAR — 299-cryptohack-ticket_maestro-cryptohack2024: Ticket Maestro (archive twin)

**Result:** SOLVED — flag `[flag — recorded in FLAGS/ctf-archive/challenge-20-cryptohack-ticket_maestro-cryptohack2024/flag.txt]`
**Submitted:** `submit_flag.py ticket_maestro-cryptohack2024` → ok:true, solved count 239→240; user-API readback shows "Ticket Maestro (CryptoHack)" newly in solved list. score_delta 0 (archive twin credits solved-list only; correct flag already credited per brief).
**Account:** NoBirdWasHam

## Relationship to challenge-240
This is the CTF-archive twin of `snark-maestro` (solved 2026-10-23 in
`challenge-240-cryptohack-snark-maestro/`). The archive card in the ctf-archive
category page confirms it is a "Mirror of Challenge for the ZKP Section" with the
**same listener: archive.cryptohack.org 26896** and the same provided files
(Cargo.toml, Dockerfile, example.py, maestro.rs, main.rs). Same flag, separate
site entry.

## The vuln (unchanged)
Groth16 (arkworks 0.3, BN254) proof malleability: the verifier checks only
e(A,B) = e(α,β)·e(L,δ)·e(C,γ), so (rA, r⁻¹B, C) verifies for any r ≠ 0. Ticket id =
blake2b(digest || serialized proof), so a fresh r gives a fresh unspent ticket id.
Econ: start 10, BuyTicket −2, Redeem +1, BuyFlag −20 → buy 1 ticket, redeem it,
forge 11 re-randomized redeems to reach 20, BuyFlag.

## Attack run (this session)
Ran `solve.py` (copied from challenge-240, only the flag filename changed) against
archive.cryptohack.org:26896: BuyTicket → Redeem original → 11 forged redeems
(balance 9→20) → BuyFlag. All 11 forges accepted first try.

## Key implementation notes (from the original solve, reused verbatim)
- Proofs are 128 B ark-serialize **0.3.0 compressed** (G1: x LE + SWFlags in top 2
  bits of last byte; G2: c0‖c1 with flags on last byte of c1).
- y-recovery: keep sqrt(x³+b) iff `(y < −y) XOR positive`; Fq2 ordering compares
  **(c1, c0)** lexicographically (ark-ff 0.3.0); Fq2 sqrt via complex method
  (eprint 2012/685 Alg. 8). Byte-exact roundtrip against a live ticket was the
  correctness oracle.
- Pure-Python affine double-and-add; group law never uses curve b, so no pairing
  library needed.

## Limitations
- No independent re-derivation of the serialization format was done here; the
  proven challenge-240 solver was reused (same server, same files).
- score_delta was 0; credit verified via solved-list growth + readback instead.

## Artifacts
- `solve.py` — full attack (pure stdlib).
- `flag_ticket_maestro-cryptohack2024.txt` — the flag.
- `statement.txt` — card text extracted from cat_ctfarch.html.

## Sources
No external sources; archive twin of challenge-240 whose own solve notes were reused internally. Disclosure wording preserved verbatim:
> ## Key implementation notes (from the original solve, reused verbatim)
> This is the CTF-archive twin of `snark-maestro` (solved 2026-10-23 in
