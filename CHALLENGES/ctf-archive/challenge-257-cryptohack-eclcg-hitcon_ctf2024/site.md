# ECLCG (HITCON CTF 2024) — CryptoHack ctf-archive card

- slug: `eclcg-hitcon_ctf2024`
- folder: `challenge-257-cryptohack-eclcg-hitcon_ctf2024`
- contributor: maple3142
- difficulty markers on card: 49 Solves · 0 Solutions
- statement: "LCG is fun, ECDSA is fun too, so why not combine them together?"
- files: chall.py, output.txt (downloaded live from cryptohack.org /static/challenges/,
  sha-named URLs taken from the card in cat_ctfarch.html; archive.cryptohack.org not needed)
- no listener (offline attack, flag = AES-CTR(str(d)) under sha256(str(d)))
- flag provenance: none obtained; no repo/web lookup of the flag (campaign hard rule).

## Instance data
- 17 signatures (r,s) on secp256k1 (q = 2^256-ish), fixed known messages (YouTube URLs).
- ct (52 B) + nonce (8 B) provided in output.txt.
- key = sha256(str(d)); need exact private key d.
