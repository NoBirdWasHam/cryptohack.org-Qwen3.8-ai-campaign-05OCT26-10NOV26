# Greatest Common Multiple — CryptoHack CTF Archive

- Slug: `greatest_common_multiple-code` (CODEGATE CTF, contributed by soon_haari)
- Category page card: `cat_ctfarch.html`, `data-challenge="greatest_common_multiple-code"`
- Service: `archive.cryptohack.org 2762`
- File: `/static/challenges/chall_535d696b1826d03d5cb011ff9e7037f8.py` → saved as `chall.py`
- Live behavior confirmed identical to chall.py:
  - Banner → PoW: `md5(str(n).encode() + b'<20-byte salt>').hexdigest() == <hash>` ("Input the decimal result of n"), salt is per-connection.
  - Then `tag` / `u1` / `u2` command loop; unknown commands ignored; empty line exits loop → final prompt `tag: `; wrong answer = silent connection close, correct answer prints flag.
- Server randomness per-connection: PoW salt, key, nonce, s0, s1 all fresh (verified: salts differ, tags differ across connections).

## Flag submission
`python3 submit_flag.py greatest_common_multiple-code "<flag>"` from workspace root.
Not submitted — no flag obtained this run (see AAR.md).
