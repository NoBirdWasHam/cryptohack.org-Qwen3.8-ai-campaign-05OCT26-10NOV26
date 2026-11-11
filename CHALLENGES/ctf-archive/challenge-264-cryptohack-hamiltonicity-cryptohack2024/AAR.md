# AAR — 264-cryptohack-hamiltonicity-cryptohack2024: Hamiltonicity (CryptoHack2024, CTF-archive mirror)

**Result:** SOLVED (2026-10-25, account NoBirdWasHam)
**Flag:** `crypto{not_hashing_entire_statement_is_bad}`
**Listener:** archive.cryptohack.org 14635 (port taken from the ctf-archive category card in `cat_ctfarch.html`; archive.cryptohack.org site pages themselves are not used)

## Source
- Statement + file links extracted from the `<li data-challenge="hamiltonicity-cryptohack2024">` card of the scraped ctf-archive category page (saved to `statement.txt`).
- Provided files downloaded from `/static/challenges/`: `chal.py`, `example.py`, `hamiltonicity.py`.
- **NOT consulted:** any /solutions/, /solves/, or third-party writeups.

## Build verification (before grinding)
`diff` against the already-solved main-site twin `challenge-234-cryptohack-sigma-hamiltonicity/`:
`chal.py`, `hamiltonicity.py`, `example.py` are **byte-identical** (numrounds = 128, FS bit = `sha256(str(comm_params) || FS_state || str(A))[-1] & 1`). The archive card even points at the same host:port (14635) the #1 solver used — same listener, same flag.

## The vulnerability
Per-round Fiat–Shamir challenge bit depends **only on the prover's commitment matrix A** (the graph openings / permutation are not hashed). Pedersen commitments are re-randomizable: `c·h2^r'` opens to the same message with randomness `r+r'`. So the prover can re-randomize commitments until the FS bit is 0, then always answer the "reveal permutation + all openings" branch — trivially satisfiable for a permuted copy of the public G. Soundness 1/2 per round collapses to 1: the prover picks the challenge.

## The attack
Run the proven #1 solver (`solve.py`, copied with only the flag filename changed): commit to a random permutation of the 5-vertex G, grind fresh Pedersen randomness until `hash_committed_graph(A, state)[-1] & 1 == 0`, send `{A, z=[perm, openings]}`; repeat 128 rounds.

## Key numbers
- 128/128 rounds accepted; total grind attempts 278 (≈2.17 commits/round, consistent with p=1/2 per try).
- One connection, ~seconds. Flag printed after round 127.

## Submission & verification
`python3 submit_flag.py hamiltonicity-cryptohack2024 "crypto{...}"` → `ok:true`, solved count 240→241, `score_delta: 0` (archive entries credit 0 points). Readback of `/api/user/NoBirdWasHam/` solved list contains **"Hamiltonicity (CryptoHack)"** — the archive entry — confirming the solve.

## Learning points
- Archive "mirror" challenges can be byte-identical re-hosts of main-site challenges: diff the provided files against solved twins **before** re-deriving anything; the port lives in the ctf-archive card HTML, not on archive.cryptohack.org pages.
- The solver's flag scraper missed the save because the final `f.read()` tokens were bytes-repr (`b'crypto{...}'`); the printed output was still authoritative. Match `crypto{` anywhere in the token, not `startswith`.

## Limitations
- No independent re-implementation of the protocol was written for this twin; correctness rests on the byte-identical diff + live 128/128 accept + solved-list readback.
- score_delta was 0 (archive credit), so the solved-list readback was the sole credit signal, as anticipated in the brief.

## Files
- `solve.py` (runnable; HOST/PORT archive.cryptohack.org:14635), `chal.py`, `example.py`, `hamiltonicity.py`, `statement.txt`, `flag_hamiltonicity-cryptohack2024.txt`, this AAR.

## Vulnerability (plain words)
The interactive Hamiltonicity proof derives its per-round Fiat-Shamir challenge bit from a hash of the prover's commitment matrix A ONLY -- the graph openings / permutation are not hashed -- while the Pedersen commitments are re-randomizable (c*h2^r' opens to the same message with randomness r+r'). The prover therefore commits to a permuted copy of the public graph, re-randomizes until the FS bit is 0, and always answers the 'reveal permutation + all openings' branch, which is trivially satisfiable. Soundness 1/2 per round collapses to 1: the prover picks the challenge.

## How the answer follows
1. Build verification BEFORE grinding: chal.py/hamiltonicity.py/example.py are byte-identical to the already-solved main-site twin challenge-234-cryptohack-sigma-hamiltonicity (numrounds=128; FS bit = sha256(str(comm_params) || FS_state || str(A))[-1] & 1); the ctf-archive card gives the same host:port (archive.cryptohack.org:14635) the #1 solver used -- same listener, same flag.
2. Attack (solve.py): commit to a random permutation of the 5-vertex G, grind fresh Pedersen randomness until hash_committed_graph(A, state)[-1] & 1 == 0, send {A, z=[perm, openings]}; repeat 128 rounds.
3. Observed: 128/128 rounds accepted; 278 total grind attempts (~2.17 commits/round, consistent with p=1/2 per try); one connection, seconds; flag crypto{not_hashing_entire_statement_is_bad} printed after round 127; submit ok:true, solved 240->241, score_delta 0 (archive credit); /api/user readback contains 'Hamiltonicity (CryptoHack)'.

## Limitations / attempts that failed
- No independent re-implementation of the protocol was written for this twin: correctness rests on the byte-identical diff + live 128/128 accept + solved-list readback.
- score_delta was 0 (archive credit), so the solved-list readback was the sole credit signal, as anticipated in the brief.
- The flag scraper initially missed the save because final f.read() tokens were bytes-repr (b'crypto{...}'); the printed output was still authoritative -- match 'crypto{' anywhere in the token, not startswith.

## Sources
ctf-archive category card (statement + port, saved statement.txt), /static/challenges/ files, byte-diff against the solved twin folder #234, own solve.py run. AAR states: NOT consulted any /solutions/, /solves/, or third-party writeups.
