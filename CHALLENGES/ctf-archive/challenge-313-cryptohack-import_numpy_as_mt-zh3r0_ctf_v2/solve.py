#!/usr/bin/env python3
# import numpy as MT (Zh3r0 CTF V2) -- archive.cryptohack.org 7265
# numpy legacy RandomState seeded with a 32-bit int -> init_genrand: A[0]=seed,
# and the generator TWISTS before its first output. random.bytes(16) = 4 uint32
# words little-endian per word, so iv = temper(T[0..3]) post-twist. Every
# post-twist word is a pure function of the 32-bit seed -> 2^32 brute force.
# pad() runs ONCE before the loop; output = iv2||AES-CBC2(iv1||AES-CBC1(pad(flag))).
import os, re, sys, socket, subprocess
import numpy as np
from Crypto.Cipher import AES

M32 = 0xffffffff
def inv_rshift_xor(y, s):
    x = y; m = s
    while m < 32:
        x ^= y >> m; m *= 2
    return x & M32
def inv_lshift_xor(y, s, mask):
    x = [(y >> i) & 1 for i in range(32)]
    for i in range(s, 32):
        if (mask >> i) & 1:
            x[i] ^= x[i - s]
    return sum(x[i] << i for i in range(32)) & M32
def untemper(y):
    x = inv_rshift_xor(y, 18)
    x = inv_lshift_xor(x, 15, 0xefc60000)
    x = inv_lshift_xor(x, 7, 0x9d2c5680)
    return inv_rshift_xor(x, 11)

def seed_from_iv(iv16):
    """numpy RandomState(seed) twists BEFORE the first output, so word_i =
    temper(T[i]), T[i] = A[(i+397)%624] ^ f((A[i]&U)|(A[i+1]&L)), A[0]=seed.
    Every A[i] is a pure function of the 32-bit seed -> brute force 2^32
    against the 4 untempered iv words (mtbrute.exe, ~100 s)."""
    words = [int.from_bytes(iv16[i*4:i*4+4], 'little') for i in range(4)]
    X = [untemper(w) for w in words]
    cmd = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "mtbrute.exe")] + \
          [format(x, 'x') for x in X] + ['0', '4294967296']
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    m = re.search(r'FOUND (\d+)', out)
    if not m:
        raise RuntimeError("seed not found: " + out[:200])
    return int(m.group(1))

def gen_ivkey(seed):
    rs = np.random.RandomState(seed)
    iv = rs.bytes(16); key = rs.bytes(16)
    return iv, key

def unpad(b):
    n = b[-1]
    assert 1 <= n <= 16 and b[-n:] == bytes([n])*n, "bad padding"
    return b[:-n]

def unwrap(hexstr):
    data = bytes.fromhex(hexstr.strip())
    iv2 = data[:16]; ct2 = data[16:]
    s2 = seed_from_iv(iv2)
    iv2b, key2 = gen_ivkey(s2)
    assert iv2b == iv2, "round2 seed check failed"
    # NOTE: pad() is applied ONCE before the loop; round 2 encrypts iv1||ct1
    # unpadded, so do NOT unpad here.
    inner = AES.new(key2, iv=iv2, mode=AES.MODE_CBC).decrypt(ct2)
    iv1 = inner[:16]; ct1 = inner[16:]
    s1 = seed_from_iv(iv1)
    iv1b, key1 = gen_ivkey(s1)
    assert iv1b == iv1, "round1 seed check failed"
    flag = unpad(AES.new(key1, iv=iv1, mode=AES.MODE_CBC).decrypt(ct1))
    return flag, s1, s2

def selftest():
    import os
    from Crypto.Util.Padding import pad
    flag = b"crypto{test_flag_selftest}"
    f = pad(flag, 16)
    for _ in range(2):
        s = int.from_bytes(os.urandom(4), 'big')
        iv, key = gen_ivkey(s)
        f = iv + AES.new(key, iv=iv, mode=AES.MODE_CBC).encrypt(f)
    out, s1, s2 = unwrap(f.hex())
    assert out == flag, (out, flag)
    print("selftest OK, recovered seeds", s1, s2)

if __name__ == "__main__":
    selftest()
    if "--live" in sys.argv:
        s = socket.create_connection(("archive.cryptohack.org", 7265), timeout=30)
        s.sendall(b"\n")
        buf = b""
        s.settimeout(30)
        try:
            while True:
                d = s.recv(4096)
                if not d: break
                buf += d
                if b"crypto{" in buf or len(buf) > 2000: break
        except socket.timeout:
            pass
        s.close()
        print("RAW:", buf[:400])
        import re
        m = re.search(rb"[0-9a-f]{64,}", buf)
        if not m:
            print("no ciphertext found"); sys.exit(1)
        flag, s1, s2 = unwrap(m.group(0).decode())
        print("seed1 =", s1, "seed2 =", s2)
        print("FLAG:", flag.decode(errors="replace"))
