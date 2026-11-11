# CryptoHack archive card: failproof-sekaictf2022

- Card source: cat_ctfarch.html, div data-challenge="failproof-sekaictf2022"
- Solves at capture: 39
- Listener: archive.cryptohack.org 42351
- Files served from live site /static/challenges/:
  - Dockerfile_eea0d49a6cd85e8f87beb91e457b582b
  - ctf_4fd3271f12db04f35e077cd790c61caf.xinetd
  - source_208d9c71e130149c2d9c6edf27242d25.py  (1135 bytes, downloaded OK from live cryptohack.org)
- Sibling challenge failproof_revenge-sekaictf202 (port 36813, different source hash 7c25f48a...) — NOT touched.

## Local source analysis (source.py)
- secret = urandom(16); A = gen_pubkey(secret, sha256); prints secret.hex() then enc!!
- gen_pubkey: 128 values, 256-bit each (sha256 digest 32 bytes * 4), chained sha256 from hash(secret)
- happiness(x) = x - sum(x>>i) == popcount(x)  (binary digit sum identity)
- encrypt: 32-byte blocks; c_i = popcount(pubkey_i & block_int), 128 values per block
- => with secret printed, all pubkeys known; recover bits via integer linear system P·m = c, m binary (unique w.h.p. since 128 eqs x ~8 bits >> 256-bit block). ASCII constraint: byte MSB=0 => 224 effective unknowns.
