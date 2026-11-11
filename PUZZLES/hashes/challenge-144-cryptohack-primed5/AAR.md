# AAR — Challenge 144: PriMeD5

**Result:** SOLVED + API-VERIFIED 2026-10-20 — `crypto{MD5_5uck5_p4rt_tw0}` (+100; 9735→9835, 186→187).
**Date:** 2026-10-20 (UTC)

## Source
- Provided: `13392_provided.py` (full server source; listener port 13392).
- NOT consulted: solutions pages / writeups / third-party flags.

## Attack (two flaws composed)
1. `sign` signs `MD5(long_to_bytes(p))` for prime p only; `check` verifies the SAME digest for ANY p
   (no primality re-check) and then leaks `FLAG[:gcd(a,p)]`.
2. ⇒ need MD5 collision (M1,M2), 128 B, `p=int(M1)` prime, `p'=int(M2)` with divisor `a ≥ 24 = len(FLAG)`.
   Sign p, check (p', sig, a) → `FLAG[:a]` = full flag.

## Pipeline (reproducible)
- `md5fastcoll/` = Marc Stevens' hashclash core + `pairgen.cpp` (streams 256-B records M1||M2,
  self-checks collision; block diff = words 4/11/14 ±2^31/2^15 per block).
  Build: `g++ -O2 pairgen.cpp md5.cpp block0.cpp block1.cpp block1stevens{00,01,10,11}.cpp block1wang.cpp`
  + stub `void p5_check(void){}` (upstream defines it in unlinked main.cpp).
- `search.py` workers: accept iff M1[0]≠0 (long_to_bytes!), M1 odd, `isprime(int(M1))`,
  `find_factor(int(M2))` = 23-smooth part ≥24 else prime factor in [29,1e6]. Hit: 1091 pairs / 1144 s
  (4 workers), a=31.
- `exploit.py`: greeting is plaintext; JSON lines; `{"option":"sign","prime":p}` → `{"option":"check",
  "prime":p',"signature":...,"a":31}` → flag in msg.

## Bugs found en route (prior-session scaffolding was broken in 2 places)
- **CRLF corruption:** pairgen wrote binary pairs to stdout WITHOUT `_setmode(_fileno(stdout),_O_BINARY)`
  → Windows mangled every 0x0A → the old search primality-tested garbage forever. Symptom: pairs read
  fine but only ~8% collide. Fix: `_O_BINARY`; verify by hashing every record of a 20 s sample.
- **"Force a factor into the tail" is IMPOSSIBLE for fastcoll pairs:** M2−M1 min term 2^39, but
  empirically ZERO of bits 0..63 can be flipped in both messages without breaking the collision
  (even word 15 bits — the differential's conditions constrain absolute values, not just differences).
  Factor must be FOUND (trial division ~0.5 accept) or filtered INSIDE the generator
  (`primed5gen.cpp` does mod-27 filtering at generation; ~27× slower per record).
- Windows pipe + subprocess: read exactly 256 B with a read_exact loop; kill strays before relaunch.

## Learning points
- sign-prime/check-any is a classic "verification path must re-check ALL policy of the issuing path".
- `long_to_bytes` ⇒ reject collision messages with a leading 0x00 byte (int→bytes roundtrip differs).
- gcd oracle: `FLAG[:gcd(a,p')]` with a ≥ len(FLAG) prints the whole flag in one request.
- Expected acceptance ≈ P(odd)·P(prime 1024-bit)·P(small factor) ≈ 1/2·1/710·0.5 ≈ 1/2800;
  observed 1/1091 (factor-finding on M2 is luckier than the naive estimate — M2's last byte is
  shared with odd M1 but its middle bytes are unconstrained).

## What I did / did not do
- One flag submission; worked only from provided source + own code.

## Limitations
- None on verification (flag submitted, leaderboard-verified).

## Configuration
- Windows 11 git-bash; mingw64 g++ 16.1; venv python 3.12 (sympy); `submit_flag.py` cookie session.
- Dir: `~\Practice_runs\cryptohack_org\challenge-144-cryptohack-primed5`.

## Sources
Sources: challenge-provided materials only; self-derived per run logs.
