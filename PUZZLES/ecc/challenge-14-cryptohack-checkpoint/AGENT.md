---
record: agent-aar
puzzle: challenge-14-cryptohack-checkpoint
category: ecc
url: https://cryptohack.org/challenges/checkpoint/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/ecc/challenge-14-cryptohack-checkpoint/flag.txt"
flag_sha256: 7d1155e924fd2584349bbc7c747438505dca220fe268b4c52a7081f449d1a247
skills: []
human_twin: AAR.md
---

# AGENT — 120-cryptohack-checkpoint: Checkpoint (CryptoHack) — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Attack (invalid-curve oracle + sign search)" [OBSERVED text; evidence tag applies to its source, not each claim]
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
   `[flag — recorded in FLAGS/ecc/challenge-14-cryptohack-checkpoint/flag.txt]` + PKCS5 04*4.

## reusable-rules
1. Invalid-curve oracle over an x-only ladder leaks +/-s mod m PER CURVE. Budget the
   2^k sign search from the start; verify candidates with recovered-scalar*G == advertised pub.
2. Save RAW per-curve residues; merge only for reporting.
3. Build the x*G==P self-check into the collector — KDF-assumption-free.

## anti-patterns / limits
- 44-curve pool was more than needed; 16 coprime curves + self-check is the minimal core.
- Enumeration is pure-Python (~15 s/curve); a C/GP enumerator would cut collection to <1 min.

## artifacts [OBSERVED]
- code: ck_curvesearch.py, ck_part4.py, csearch.gp, ellloop.gp, ellt.gp, elltest.gp, one.gp, pp1.gp, quick.gp, quick2.gp, quick3.gp, quick4.gp, run.gp, search.gp, signsearch3.py, solve.py, t1.gp, t2.gp, t3.gp, tbisect.gp, tmini.gp, tmini2.gp, twfac.gp, two.gp
- data/logs: part4h.log, sign3.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
- **Platform:** CryptoHack (https://cryptohack.org/)
- **Category page (statement read here):** https://cryptohack.org/challenges/ecc/
- **Challenge:** "Checkpoint" (150 pts, slug `checkpoint`)
- **NOT consulted:** solutions page / writeups (no-cheat rule; one stray search mid-session
  was discarded un-used — the solve is derived from live-server observation only)
