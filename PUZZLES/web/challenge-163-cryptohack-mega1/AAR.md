# AAR — mega1 / Megalomaniac 1 (CryptoHack, web, 100 pts) — SOLVED

## RECONSTRUCTED AAR (post-hoc)
Reconstructed 2026-11-01 from surviving artifacts in this folder (13408.py challenge file, solve.py+solve.log, solve2.py+solve2.log, solve3.py+solve3.log, flag_mega1.txt) and the ledger (progress.json nn163: "solved via RSA-malleability search (solve3); site already credited (delta 0 on resubmit)", date 2026-10-21). No AAR existed at solve time; the HOW below traces to the scripts and logs named above.

## Flag
`crypto{M4lleaBl3_3nCRypt1on_g0n3_wr0nG_:'(}` — provenance: produced client-side by solve3.py `finish()` by AES-decrypting the server's `encrypted_flag` with the recovered factors (solve3.log line 7), written to flag_mega1.txt; matches the ledger flag field. Ledger notes record a resubmit scored delta 0 = already credited.

## Problem
Listener socket.cryptohack.org 13408. A fake client-registration/login flow: the server hands out `master_key_enc`, `share_key_pub=(n,e)` (RSA-2048) and `share_key_enc` = its own RSA **private key** (p,q,d,u) AES-encrypted. Login step 2 (Client_new_login.login_step2, 13408.py): server AES-decrypts `share_key_enc`, parses (p,q,d,u), then `SID = RSA_CRT_decrypt(SID_enc, p,q,d,u)`, strips the last 16 bytes and echoes SID. Flag is AES-ECB-encrypted with `SHA256(long_to_bytes(p)+long_to_bytes(q))`.

## Vulnerability / Attack
Three compounding flaws, all visible in the in-folder challenge file 13408.py:
1. **Raw RSA, no padding check:** the server RSA-decrypts an attacker-chosen ciphertext and returns the plaintext — textbook malleability (send `M^e mod n`, expect `M` back).
2. **AES-ECB block malleability of the key blob:** `share_key_enc` is ECB under the master key, so a 16-byte block can be XOR-flipped without knowing the key. solve3.py corrupts exactly the **u-field** block: `bad[35*16+j] ^= 0xFF` for j in 0..15 ("corrupt u-field block only").
3. **CRT recombination bug:** `RSA_CRT_decrypt` computes `t=(mq-mp)%q; h=(t*u)%q; m = h*p+mp` — the recombination coefficient is reduced mod **q** and the wrong residue is lifted. With intact u this still reconstructs M for every M (so the oracle is useless); with u corrupted, `h` is a fresh pseudorandom residue mod q, and the returned SID equals M (modulo the 16-byte truncation the server strips) **only when t = 0**, i.e. `M mod p == M mod q` — which for random-looking M holds essentially only when `M < min(p,q)` (both residues are then M itself).

Oracle predicate implemented in solve3.py `oracle(M)`: submit `SID_enc = hex(M^e mod n)`, tampered key blob, and check `SID == hex(M)` minus last 16 bytes. Sanity probes baked in: `oracle(12345) == True`, `oracle(2^1024-1) == False`. Binary search over [2^1023, 2^1024-1] → exactly 1024 bisection queries; boundary `hi` asserted to divide n (`assert s.n % qmin == 0`). Then `finish()`: for (p,q) in both orders of (hi, n/hi), key = SHA256(p‖q) as in the server, AES-ECB-decrypt `encrypted_flag`, accept the plaintext starting `crypto`.

Run record (solve3.log): n 2048 bits; 256q→770 bits left, 512q→514, 768q→258, 1024q→2; done 1025 queries in 361 s; FLAG printed.

## Iteration history (evidence of the debugging path)
- solve.log: first version died "ERROR at query 5" — the server's `bytes.fromhex` chokes when `"%x" % M` has odd length.
- solve2.log: three+ sessions, each dying after 9–38 queries with `{'error': 'An error occured during the login.'}` — session/login-state handling bug.
- solve3.py header records the fixes: "even-length hex fix for SID_enc (odd hex -> server bytes.fromhex ValueError)" + persistent session per attempt with up to 4 reconnects.

## Learning points
- An oracle that returns "decrypted == my value" is a **comparison oracle** for the secret's size even when the absolute value is randomized — binary-searchable bit by bit.
- Malleability stacks: ECB block flip (no integrity) + missing padding validation + CRT glue bug turned a login echo into a factorization oracle.
- Truncating hex of an integer (`"%x"`) must be parity-fixed before `bytes.fromhex` — an off-by-one bug killed two earlier runs.

## Limitations / honest notes
- The exact reason the truncated-equality predicate is True below min(p,q) and False above was re-derived during this reconstruction from the RSA_CRT_decrypt listing in 13408.py; the original run left only "RSA malleability search" in ledger notes. The empirical boundary check (`n % hi == 0`) is recorded in solve3.py.
- solve2.log's exact session-death trigger is not recorded, only its symptom.

## Source disclosure
No third-party writeup consulted. Reconstructed solely from this folder's artifacts + ledger.

## Files
13408.py (challenge artifact), solve.py/solve.log, solve2.py/solve2.log, solve3.py/solve3.log (final), flag_mega1.txt, maths.html/s2.html (fetched reference pages, not solutions).
