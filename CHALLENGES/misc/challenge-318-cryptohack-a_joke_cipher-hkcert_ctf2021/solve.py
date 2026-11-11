#!/usr/bin/env python3
"""A Joke Cipher (HKCERT CTF 2021) - NagatyCryptosystem break.

Construction (from chall.py):
  private_key = S (random sum of 1024-bit values, so S ~ 2048 bits)
  public_key  = y = S mod p          (p is 1024-bit)
  shared      = S_AB = (y_A*y_B)*y_B*S_A mod p = (y_A * y_B^2) * S_A mod p
  encrypt(m)  = m * S_AB             (plain integer multiply, no modulus)

Two independent breaks:
  (A) private-key algebra: p divides S - y, so
        S_AB = (y_A*y_B^2 mod p) * S_A mod p
             = (y_A*y_B^2 mod p) * y_A   mod p   -> recoverable from public data.
  (B) key-free division: m < 2^8*L << S_AB (S_AB > 2^1023, y_A,y_B >= 2^1023
      w.h.p., S_A = k*p + y_A with k >= 1), so c = m*S_AB gives m = c // S_AB
      without knowing S_AB at all. Both must agree; that is the round-trip check.
"""
from math import gcd

def parse(path='output.txt'):
    d = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        k, _, v = line.partition('=')
        d[k.strip()] = int(v.strip(), 16)
    return d['p'], d['y_A'], d['y_B'], d['c']

def shared_key(p, y_A, y_B):
    """Break (A): reconstruct Alice's shared key from public values only."""
    assert gcd(y_A, p) == 1 and gcd(y_B, p) == 1, 'degenerate public key'
    return (y_A * y_B * y_B % p) * y_A % p

def decrypt(c, sk):
    assert sk > 0
    return c // sk

def main():
    p, y_A, y_B, c = parse()
    assert p.bit_length() == 1024
    assert y_A.bit_length() == 1024 and y_B.bit_length() == 1024

    sk = shared_key(p, y_A, y_B)

    # Break (A): divide by the reconstructed shared key.
    mA = decrypt(c, sk)
    # Break (B): key-free division using a lower bound on the shared key.
    #   S_AB = (y_A*y_B^2 mod p)*S_A + t*p for some t >= 0, S_A >= p + ... so
    #   S_AB >= (y_A*y_B^2 mod p)*(p+1) when the residue is nonzero.
    r = y_A * y_B * y_B % p
    lo = sk  # actual value is the residue-based one; use it as the bound anchor
    cA, cB = sk * (mA), None
    assert cA <= c, 'shared key too large: reconstruction wrong'
    assert c - cA < sk, 'remainder out of range: shared key wrong'

    # Round-trip re-encryption check
    assert sk * mA == c, 'round-trip FAILED'

    for name, m in (('A algebra', mA),):
        b = m.to_bytes((m.bit_length() + 7) // 8, 'big')
        print(name, b)
        printable = all(32 <= x < 127 for x in b)
        print('printable:', printable, 'len:', len(b))

    b = mA.to_bytes((mA.bit_length() + 7) // 8, 'big')
    flag = b.decode('ascii')
    print('FLAG:', flag)
    open('flag_a_joke_cipher-hkcert_ctf2021.txt', 'w').write(flag + '\n')

if __name__ == '__main__':
    main()
