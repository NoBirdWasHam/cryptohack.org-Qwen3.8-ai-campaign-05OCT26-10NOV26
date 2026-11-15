# AAR — Noise Free (challenge-175-cryptohack-lwe-lsb-regev)

Noise-free Regev LWE (socket 13411). S is fixed per server process; b = A*S (mod q) with NO noise (statement: "How well can you learn if you don't have to deal with errors?").

## Attack
64 zero-encryptions -> 64x64 invertible system over GF(65537) (q prime): Gauss-Jordan recovers S exactly; then each flag char: `m = (b - A*S) mod q` (plaintext is a byte, so the mod-q value IS the byte). All chars verified by re-encryption identity.

## Result
**SOLVED** — `[flag — recorded in FLAGS/post-quantum/challenge-13-cryptohack-lwe-lsb-regev/flag.txt]}` (submitted 2026-10-13, live-verified). Files: `_pq/solve_13411.py`, `_pq/13411.py`.

_Backfill note (2026-10-14): this doc folder was created after the fact; all scripts/data referenced above live in `_pq/` and the flag was verified live on 2026-10-13._


## Vulnerability (plain words)
Regev encryption with the noise switched off. Everything hard about b = A·s + e comes from e; with e = 0 every sample is an exact linear equation in the secret. The server also keeps the same S for the whole connection, so samples accumulate into a full linear system instead of resetting.

## How the answer follows
1. Ask the server (socket 13411) for 64 encryptions of zero → 64 equations b_i = ⟨A_i, s⟩ (mod 65537) in 64 unknowns.
2. q = 65537 is prime, so every nonzero pivot is invertible and Gauss–Jordan over GF(65537) runs like ordinary [flag — recorded in FLAGS/post-quantum/challenge-9-cryptohack-lwe-intro/flag.txt]; the 64×64 sample matrix came out invertible, giving **s exactly** — no error term means no approximation, no failure probability beyond matrix singularity (~1/q).
3. Decrypt: for each real ciphertext, m = (b − A·s) mod q. With zero noise the residue *is* the plaintext byte directly (no centered rounding window), and every character was confirmed by re-encrypting it and checking the identity.
Result: `[flag — recorded in FLAGS/post-quantum/challenge-13-cryptohack-lwe-lsb-regev/flag.txt]}` — the flag name is the lesson. Submitted 2026-10-13, live-verified.

## Limitations / attempts that failed
- Run logs do not record how many zero-encryption requests were exchanged before the system was invertible (first-try vs. retry not recorded), nor the exact request count beyond the 64 used.
- Backfill note already in file: folder created after the fact; scripts live in `_pq/`.

## Sources
- Live server interaction only (a.cryptohack.org socket 13411). Solvers: `_pq/13411.py`, `_pq/solve_13411.py`. No external reference or writeup used.
