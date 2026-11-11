# verilicious-cyber_apocalypse (CryptoHack archive / ctf-archive mirror)

- Category card: ctf_archive (Cyber Apocalypse 2025), 60 solves, author r4sti.
- No live listener: offline challenge, files only.
- Files: output.txt (enc_flag hex + R list), pubkey.pem (RSA 1024, e=65537), source.py.

## Key facts
- PyCryptodome PKCS1_v1_5.decrypt(c, sentinel): returns sentinel iff PKCS1 v1.5
  decode FAILS; else returns session-key bytes. So `verify` = PKCS1 padding
  VALIDITY oracle on (r*m mod n).
- assert passes for all r in R => for each of the 78 r: r*m mod n decodes as
  valid PKCS1v15, in particular r*m mod n in [0x02 * 2^1008, 0x03 * 2^1008).
- interval width 2^1008, n ~ 2^1023.5 => ~15 bits info per multiplier;
  78 * 15 = ~1170 > 1024 => m (padded flag) uniquely determined.
- Attack = CVP in the 78-dim lattice L = span{(r_i)} + n*Z^78, target =
  (c,...,c), c = 2.5*2^1008 (interval center). Error coord < 2^1007, norm
  ~ 2^1009 << Gaussian radius ~ n^(77/78)*sqrt(78/2pi e) ~ 2^1012.
- Then m = v_i * r_i^{-1} mod n; verify pow(m,e,n) == enc_flag; strip padding.
