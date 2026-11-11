# AAR — Sign in Please (HKCERT CTF 2020, CryptoHack archive #291)

**Solved:** YES — flag `hkcert20{d0_y0u_feel_s3cur3_wh3n_s19nin9_in?}`.
Listener printed it after `auth` (run2.log); submitted via submit_flag.py:
`ok:true`, "Flag submitted.", solved count 242→243, solved-list readback contains
"Sign in Please (HKCERT CTF)" (score_delta 0 = archive challenge, credited per brief).
Recovered password: `STimrwGWyGyy8gAk` (bf6 runs: 444s + 563s, bf4: 27s).

## The vuln (not RSA — permutation auth with a broken oracle)

`chall.py` implements a "secure" auth: password = base64(urandom(12)) (16 chars),
shared between a Server and a Client. Server `auth`: sends a random permutation
`pbox` of 0..19 and random 4-byte `salt`, demands
`sha256(permutate(password+salt, pbox))`. Client `spy` oracle: given ANY pbox/salt
prints `sha256(permutate(password+salt, pbox))`.

Two bugs in the spy guard `assert len(set(pbox)) == 20`:

1. **Negative indexing**: distinct *integers* ≠ distinct *positions*. `x` and `x-20`
   both index the same byte of the 20-byte `password+salt`, so one byte can be
   duplicated and other bytes excluded while `len(set(pbox))==20` still holds.
2. **No length cap**: pbox may contain >20 entries (duplicates allowed), so the
   hashed string can be any length ≥20.

Minimum unknowns per spy query: 20 distinct ints, each position has exactly 2
integer representatives → salt positions (we choose the salt) absorb 8, leaving
≥12 ints on password positions → ≥6 distinct password bytes in the hash. So each
query commits to exactly 6 base64 chars (64^6 = 2^36) — brute-forceable offline.

## Attack

- Q1: pbox `0,1,2,3,4,5,-20,-19,-18,-17,-16,-15,16,17,18,19,-4,-3,-2,-1`,
  salt `AAAA` → hash over `[c0..c5][c0..c5][AAAA][AAAA]` → brute force chars 0–5.
- Q2: same trick on positions 6–11 → chars 6–11.
- Q3: positions 12–15 plus already-known 0,1 → only 4 unknowns (64^4, trivial).
- `auth`: read server pbox/salt, compute the hash from the recovered password, get flag.
- 4 of the 10 allowed commands; brute force done between spy and auth on the same
  connection (server has no idle timeout observed).

## Key numbers

- Search: 2 × 64^6 = 1.37e11 sha256 (20-byte, single-block). Custom C scalar SHA-256
  (`bf.c`, gcc -O3 -march=native -fopenmp, 16 threads) ≈ 6e7 hash/s → minutes per query.
- C SHA-256 differentially tested against Python hashlib before use; planted-tuple
  tests recover the tuple; full local protocol simulation (chall.py Server/Client)
  passes end-to-end.

## Learning points

- `len(set(x)) == n` guards on index lists are broken by Python negative indices.
- A hash oracle over a permutable structure leaks per-position entropy: minimize
  covered positions via duplicate representatives, then brute force the commitment.
- 64^6 is the practical floor here (2 reps/position × 4 salt slots ⇒ ≥6 unknowns).

## Limitations

- MT19937 prediction of server `random.shuffle` was rejected early: only 10
  commands/connection, ~76 bits of randrange output per auth, password fresh per
  connection — infeasible.
- Brute force is the bottleneck (~10 min/query worst case); no MITM/structure
  shortcut exists for sha256 commitments.

## Sources
not recorded in run logs (pre-discipline solve)
