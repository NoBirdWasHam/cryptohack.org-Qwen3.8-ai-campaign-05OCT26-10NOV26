# Find the Lattice (`find`)

- **Points:** 100
- **Category:** post-quantum
- **Status:** SOLVED (live-verified 2026-10-14 via user API, +100: 7005 → 7105)
- **Solved:** 2026-10-14
- **URL:** https://cryptohack.org/challenges/post-quantum/find/

## Statement

> This challenge uses modular arithmetic to encrypt the flag. But hidden within the
> protocol is a 2-dimensional lattice. Break the flag using Gaussian reduction from
> the previous challenge!
>
> The source (provided) defines:
>
> ```python
> from Crypto.Util.number import *
> from secrets import randbelow
>
> # Generate the public and private keys
> def gen_key():
>     while True:
>         # Generate a 512-bit prime
>         q = getPrime(512)
>
>         # Generate a random f and g
>         f = random.randint(2, int(q**0.5 / 2**0.5))
>         g = random.randint(int(q**0.5 / 2), int(q**0.5 / 2**0.5))
>         if math.gcd(f, g) != 1:
>             continue
>
>         # Compute the public key
>         h = g * pow(f, -1, q) % q
>
>         return (q, h), (f, g)
>
> # Encrypts the message
> def encrypt(public, message):
>     q, h = public
>     m = int.from_bytes(message, byteorder='big', signed=False)
>
>     # Encrypt the message
>     while True:
>         # Generate a random r
>         r = random.randint(2, int(q**0.5 / 2**0.5))
>         e = (r * h + m) % q
>         assert m < q**0.5 / 2**0.5
>         return e
>
> # Decrypts the message
> def decrypt(private, e):
>     f, g = private
>     a = (f * e) % q
>     m = a * pow(f, -1, g) % g
>     return m
>
> public, private = gen_key()
> q, h = public
> f, g = private
>
> e = encrypt(public, FLAG)
>
> print("q:", q)
> print("h:", h)
> print("e:", e)
> ```
>
> Output (see `_pq/find_output.txt` / `find_output.txt`):
>
> ```
> q: 7638232120454925879231554234011842347641017888219021175304217358715878636183252433454896490677496516149889316745664606749499241420160898019203925115292257
> h: 2163268902194560093843693572170199707501787797497998463462129592239973581462651622978282637513865274199374452805292639586264791317439029535926401109074800
> e: 5605696495253720664142881956908624307570671858477482119657436163663663844731169035682344974286379049123733356009125671924280312532755241162267269123486523
> ```
>
> The flag is 27 bytes: `crypto{?????????????????????}`

## Key structure (from the source)

| Symbol | Meaning | Size bound |
|--------|---------|-----------|
| q      | 512-bit prime (public) | 512 bits |
| f      | private (public-key numerator inverse) | 2 ≤ f < √(q/2) ≈ 2^254.8 |
| g      | private | √(q/4) ≤ g < √(q/2) ≈ 2^255.3 |
| h      | public = g·f⁻¹ mod q | 512 bits |
| r      | random nonce | 2 ≤ r < √(q/2) |
| e      | ciphertext = (r·h + m) mod q | 512 bits |
| m      | flag as integer | 27 bytes = 216 bits |

Only `(q, h, e)` are given. The private key `(f, g)` is the target.
