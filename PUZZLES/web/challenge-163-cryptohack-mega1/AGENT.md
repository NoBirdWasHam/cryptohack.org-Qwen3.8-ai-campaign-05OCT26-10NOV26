---
record: agent-aar
puzzle: challenge-163-cryptohack-mega1
category: web
url: https://cryptohack.org/challenges/mega1/
status: solved
date: 2026-10-21
flag_ref: "FLAGS/web/challenge-163-cryptohack-mega1/flag.txt"
flag_sha256: 9544fce93caa1022d87e4f9282d49f180573cf31beb116c1ee5e8d4f3c6a4df6
skills: []
human_twin: AAR.md
---

# AGENT — mega1 / Megalomaniac 1 (CryptoHack, web, 100 pts) — SOLVED
Machine-optimized twin of the human AAR in this directory (mechanically regenerated from it; carries no extra facts).
Epistemic tags: OBSERVED = artifact/evidence present in this dir · NOT OBSERVED = not recorded anywhere in the corpus.

## procedure — extracted from AAR section "Vulnerability / Attack" [OBSERVED text; evidence tag applies to its source, not each claim]
Three compounding flaws, all visible in the in-folder challenge file 13408.py:
1. **Raw RSA, no padding check:** the server RSA-decrypts an attacker-chosen ciphertext and returns the plaintext — textbook malleability (send `M^e mod n`, expect `M` back).
2. **AES-ECB block malleability of the key blob:** `share_key_enc` is ECB under the master key, so a 16-byte block can be XOR-flipped without knowing the key. solve3.py corrupts exactly the **u-field** block: `bad[35*16+j] ^= 0xFF` for j in 0..15 ("corrupt u-field block only").
3. **CRT recombination bug:** `RSA_CRT_decrypt` computes `t=(mq-mp)%q; h=(t*u)%q; m = h*p+mp` — the recombination coefficient is reduced mod **q** and the wrong residue is lifted. With intact u this still reconstructs M for every M (so the oracle is useless); with u corrupted, `h` is a fresh pseudorandom residue mod q, and the returned SID equals M (modulo the 16-byte truncation the server strips) **only when t = 0**, i.e. `M mod p == M mod q` — which for random-looking M holds essentially only when `M < min(p,q)` (both residues are then M itself).

Oracle predicate implemented in solve3.py `oracle(M)`: submit `SID_enc = hex(M^e mod n)`, tampered key blob, and check `SID == hex(M)` minus last 16 bytes. Sanity probes baked in: `oracle(12345) == True`, `oracle(2^1024-1) == False`. Binary search over [2^1023, 2^1024-1] → exactly 1024 bisection queries; boundary `hi` asserted to divide n (`assert s.n % qmin == 0`). Then `finish()`: for (p,q) in both orders of (hi, n/hi), key = SHA256(p‖q) as in the server, AES-ECB-decrypt `encrypted_flag`, accept the plaintext starting `crypto`.

Run record (solve3.log): n 2048 bits; 256q→770 bits left, 512q→514, 768q→258, 1024q→2; done 1025 queries in 361 s; FLAG printed.

## reusable-rules
- An oracle that returns "decrypted == my value" is a **comparison oracle** for the secret's size even when the absolute value is randomized — binary-searchable bit by bit.
- Malleability stacks: ECB block flip (no integrity) + missing padding validation + CRT glue bug turned a login echo into a factorization oracle.
- Truncating hex of an integer (`"%x"`) must be parity-fixed before `bytes.fromhex` — an off-by-one bug killed two earlier runs.

## anti-patterns / limits
- The exact reason the truncated-equality predicate is True below min(p,q) and False above was re-derived during this reconstruction from the RSA_CRT_decrypt listing in 13408.py; the original run left only "RSA malleability search" in ledger notes. The empirical boundary check (`n % hi == 0`) is recorded in solve3.py.
- solve2.log's exact session-death trigger is not recorded, only its symptom.

## artifacts [OBSERVED]
- code: 13408.py, solve.py, solve2.py, solve3.py
- data/logs: flag_mega1.txt, solve.log, solve2.log, solve3.log
- flag value: never in this file; sha256 against `FLAGS/INDEX.jsonl`

## references
No third-party writeup consulted. Reconstructed solely from this folder's artifacts + ledger.
