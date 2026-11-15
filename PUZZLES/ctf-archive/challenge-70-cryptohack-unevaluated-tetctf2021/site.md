# Unevaluated (TETCTF) — cryptohack.org ctf-archive card (slug `unevaluated-tetctf2021`)

- Name: Unevaluated (TETCTF), category ctf-archive (stage ctf-archive-2021), 58 solves, 0 pts (archive).
- Author on site: NDH.
- Statement: "We’re about to launch a new public key cryptosystem, but its security has not
  been carefully reviewed yet. Can you help us?"
- Files (fetched from the category page card, saved in this folder):
  - source.py  → /static/challenges/source_4a20f1684459efaa7ef72c59213e4bf9.py
  - output.txt → /static/challenges/output_aff14c5baa7956b629737a9c2ef0cd01.txt
- No network listener (offline instance; flag = AES-ECB(key=k) of padded flag, recover k from DLP).
- Submit: `python3 submit_flag.py unevaluated-tetctf2021 'flag{...}'` from workspace root.

## Cryptosystem summary (from source.py)
Complex Diffie-Hellman in the unit group of Z[i]/(p^2):
p = 128-bit prime, p≡3 mod 4; branch p≡11 (mod 12): q=(p-1)/2, r=(p+1)/12, both prime
(instance here: p%3==2). n=p^2, order=p*q*r. g = h^24 chosen with exact order p*q*r.
pub = g^k mod p^2 with k = int.from_bytes(urandom(32)). ciphertext = AES-256-ECB(k).encrypt(flag).
