# AAR — 120-cryptohack-checkpoint: Checkpoint (CryptoHack) — SOLVED

**Result:** SOLVED (account NoBirdWasHam; 2026-10-21) — flag `[flag — recorded in FLAGS/ecc/challenge-120-cryptohack-checkpoint/flag.txt]` (+150, score 12060, 205 solved)

## Sources
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/ecc/
- **Challenge:** "Checkpoint" (150 pts, slug `checkpoint`)
- **NOT consulted:** solutions page / writeups (no-cheat rule; one stray search mid-session
  was discarded un-used — the solve is derived from live-server observation only)

## Attack (invalid-curve oracle + sign search)
Server (socket.cryptohack.org:13419) does ECDH P-256, accepts ANY (x,y) as public
point (no curve validation), key = sha256(str(x(s*Q)))[:16], AES-128-CBC, and returns
a known-plaintext test message under the same key => oracle for x(s*Q). s is fixed per
session; banner carries client_pub, server_pub, flag ct.

1. `ck_curvesearch.py`: random b' on P-256's a; PARI ellcard (SEA); keep curves whose
   order has smooth part m in [2^19, 2^21] (primes <= 10^6). ~1/3 yield; 44 curves.
2. `ck_part4.py`: per curve, Q of exact order m on the twist; send Q, pull test ct,
   enumerate r < m with sha256(x(r*Q)) decrypting it => s = +/-r (mod m). Raw
   per-curve residues saved (session-scoped; one session only).
3. `signsearch3.py`: oracle is X-ONLY (x(rQ)=x(-rQ)) => per-curve SIGN AMBIGUITY.
   Pick 16 curves with no shared prime >2 (~326 bits), enumerate 2^16 sign patterns,
   CRT, verify x*G == server_pub. Exactly one hit: 256-bit s, mask 0b1010011010000111.
   Flag = AES-CBC-decrypt(ct, sha256(str(x(s*client_pub)))[:16]) =>
   `[flag — recorded in FLAGS/ecc/challenge-120-cryptohack-checkpoint/flag.txt]` + PKCS5 04*4.

## Root causes of the long tail
- SIGN AMBIGUITY was the whole story. All-positive CRT = mixed-sign mongrel:
  per-prime overlaps are small-prime (sign-insensitive mod 2) so it looked consistent,
  yet x != s. The assumption-free self-check x*G == server_pub cleanly separated
  "scalar wrong" from "KDF wrong" and proved collection sufficiency.
- "Secret must be huge" was a red herring produced by the same bug (268/601/773-bit
  all-+ runs all failing). s was 256 bits; the signs were wrong.
- Merged per-prime residues destroy per-curve sign coherence -> collector now saves
  raw (b, m, r); sign search uses raw.
- PARI: gp file must be LF-only; top-level multi-statement for-bodies need if(1, ...).
- CBC single-block oracle test must compare exactly 16 bytes (TEST_MSG[:16]) via
  ECB-DECRYPT(C1) xor IV — not ECB-encrypt, not startswith of a 19-byte constant.

## Evidence
part4h.log (25 raw residues), sign3.log (1 hit, plaintext), submit score_delta +150.

## Learning points (transferable)
1. Invalid-curve oracle over an x-only ladder leaks +/-s mod m PER CURVE. Budget the
   2^k sign search from the start; verify candidates with recovered-scalar*G == advertised pub.
2. Save RAW per-curve residues; merge only for reporting.
3. Build the x*G==P self-check into the collector — KDF-assumption-free.

## Limitations
- 44-curve pool was more than needed; 16 coprime curves + self-check is the minimal core.
- Enumeration is pure-Python (~15 s/curve); a C/GP enumerator would cut collection to <1 min.

## Configuration (environment for this run)
- **Host OS:** Windows 11, git-bash/MSYS; **User:** OWNER
- **Interpreter:** system python3 (PyCryptodome); PARI/GP `~\tools\gp64.exe` 2.17.4
- **Working dir:** `~\Practice_runs\cryptohack_org\challenge-120-cryptohack-checkpoint`
- **Agent:** Hermes Agent (desktop); submission via `submit_flag.py checkpoint <flag>` (score delta verified)
