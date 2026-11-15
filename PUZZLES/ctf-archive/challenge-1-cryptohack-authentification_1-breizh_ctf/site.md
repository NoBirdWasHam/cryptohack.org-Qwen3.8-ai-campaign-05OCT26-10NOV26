# authentification_1-breizh_ctf

- Statement: "I secured my web application with AES-GCM implemented by the intern! Great idea, isn't it ?"
- Listener: archive.cryptohack.org port 61277 (raw HTTP via requests)
- Files: authentification-1.zip (Flask app: app.py, crypto.py, gcm/), template_authentification.py
- Contributed by skilo. 135 solves.
- Flow: /register (MAX_USERS=1, role=guest), /login -> cookie `auth` = ct.hex();tag.hex(), /admin shows flag if token role == super_admin.
- /reset-db: new MASTER_KEY + wipes users.

## Vulnerability
- crypto.py: static IV = 0^12 -> GCM nonce reuse (irrelevant alone: single key lifetime token).
- gcm/gcm.py: intern FORGOT `inc(J0)` before GCTR for encryption AND reuses E(J0) as tag mask.
  => tag = GHASH(C) XOR E(J0) but E(J0) = keystream block 0 = P[0:16] XOR C[0:16] (known plaintext:
     token JSON format is fully determined by chosen username).
  => GHASH_H(buf) known; recover H (GHASH poly key) as root of a low-degree poly over GF(2^128),
     then forge tag for any ct' = P' XOR ks (ks known for all bytes of the captured plaintext).
