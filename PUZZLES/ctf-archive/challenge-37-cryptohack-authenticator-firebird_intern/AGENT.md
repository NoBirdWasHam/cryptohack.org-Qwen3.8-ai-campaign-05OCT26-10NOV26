---
record: agent-aar
puzzle: challenge-37-cryptohack-authenticator-firebird_intern
category: ctf-archive
url: https://cryptohack.org/challenges/authenticator/
status: solved
date: 2026-10-28
flag_ref: "FLAGS/ctf-archive/challenge-37-cryptohack-authenticator-firebird_intern/flag.txt"
flag_sha256: sha256:61626142036e9b9d51d9a87d5fad1cb02b1ceaa72cb5d7ab403733b38cd310eb
skills: [hash-collision-md5-engineering]
human_twin: AAR.md
---

# AGENT — authenticator (CryptoHack ctf-archive, Firebird Internal CTF)
Machine twin of AAR.md.

## System [OBSERVED]
- blake3 mutual-auth handshake; 6-char password from [0-9a-zA-Z] WITHOUT repetition -> 62P6 = 44,261,653,680 ~ 35.4-bit space, fresh per connection.
- R1 = blake3(P || "HANDSHAKE_FROM_SERVER" || C1) printed for our C1; must answer R2 = blake3(P || "HANDSHAKE_FROM_CLIENT" || C2). signal.alarm(10) whole session.

## Attack [OBSERVED, self-derived]
1. Custom OpenCL blake3 single-block kernel (inputs <= 64 B: one compression, t=43, flags=11 = CHUNK_START|CHUNK_END|ROOT, 7 rounds), one candidate per work-item.
2. Space split x (first 3 chars, host-precomputed sorted-triple LUT) x y (last 3 via Lehmer unranking, branch-free threshold p = i + #{m: s_m - m <= i}).
3. 64-bit filter on first two digest words -> at most one candidate; CPU verify with official blake3.
4. Chunked launches (4096 y-rows) + host poll -> early exit. ~15.6 Ghash/s; live solve P found at 3.38 s of a 10 s alarm.

## Pitfalls [OBSERVED]
- Protocol-level bypasses proven dead ends (R1 replay refused; no session looping; alarm real; password fresh per connection).
- Kernel cost 4 wasted iterations: 16 rounds/flags=5 misremember + unsorted x-table. Nail via official reference impl + single-block sweep vs official library.

## Verify
b3v3.cl kernel + host scripts under artifacts_2026-11-14/; CPU-check any recovered P with official blake3 against the recorded R1/R2.
