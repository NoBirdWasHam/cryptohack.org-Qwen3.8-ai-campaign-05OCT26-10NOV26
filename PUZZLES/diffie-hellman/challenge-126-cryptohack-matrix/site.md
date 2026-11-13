# CryptoHack — matrix (75 pts)

- **Platform:** CryptoHack (cryptohack.org), category: Diffie-Hellman
- **Challenge name:** matrix ("The Matrix")
- **Slug:** `matrix`
- **Points:** 75
- **Folder:** challenge-126-cryptohack-matrix
- **Account:** NoBirdWasHam
- **Status:** SOLVED 2026-10-15 (flag submitted, score_delta +75)

## Verbatim statement

> I must get out of here. I must get free, and in this mind is the key, my key!
>
> Challenge files: the_matrix.sage, flag.enc
>
> Challenge contributed by jschnei

## Files (downloaded, renamed `*.provided`)

- `the_matrix.provided` — https://cryptohack.org/static/challenges/the_matrix_92a1330e0fc370fbacf7f001ae2933ee.sage
- `flag.provided` — https://cryptohack.org/static/challenges/flag_403b981c77d39217c20390c1729b15f0.enc

### the_matrix.provided (verbatim)

```python
import random

P = 2
N = 50
E = 31337

FLAG = b'[flag — recorded in FLAGS/Symmetric Ciphers/challenge-48-cryptohack-beatboxer/flag.txt]'

def bytes_to_binary(s):
    bin_str = ''.join(format(b, '08b') for b in s)
    bits = [int(c) for c in bin_str]
    return bits

def generate_mat():
    while True:
        msg = bytes_to_binary(FLAG)
        msg += [random.randint(0, 1) for _ in range(N*N - len(msg))]

        rows = [msg[i::N] for i in range(N)]
        mat = Matrix(GF(2), rows)

        if mat.determinant() != 0 and mat.multiplicative_order() > 10^12:
            return mat

def load_matrix(fname):
    data = open(fname, 'r').read().strip()
    rows = [list(map(int, row)) for row in data.splitlines()]
    return Matrix(GF(P), rows)

def save_matrix(M, fname):
    open(fname, 'w').write('\n'.join(''.join(str(x) for x in row) for row in M))

mat = generate_mat()

ciphertext = mat^E
save_matrix(ciphertext, 'flag.enc')
```

### flag.provided

50 lines of 50 '0'/'1' chars (the matrix C = M^E over GF(2)).

## Notes

- Flag embedded in the first `len(FLAG)*8` = 272 bits of `msg`; the rest random.
- `rows = [msg[i::N] for i in range(N)]` ⇒ M[i][j] = msg[i + j·N] (columns of the
  row-major grid become the matrix rows — extraction must go column-first).
- C = M^31337 over GF(2); M ∈ GL(50,2), ord(M) > 10^12 (irrelevant to the attack).
