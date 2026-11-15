# Minimal SHA-256 Merkle-Damgard compression function + length-extension helpers.
# Validated against hashlib by test_compress() below.
import hashlib, struct

K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]
H0 = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]

def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

def compress(h, block):
    """h: 8 ints state; block: exactly 64 bytes. Returns new 8-int state."""
    assert len(block) == 64
    w = list(struct.unpack('>16I', block))
    for i in range(16, 64):
        s0 = _rotr(w[i-15], 7) ^ _rotr(w[i-15], 18) ^ (w[i-15] >> 3)
        s1 = _rotr(w[i-2], 17) ^ _rotr(w[i-2], 19) ^ (w[i-2] >> 10)
        w.append((w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF)
    a, b, c, d, e, f, g, hh = h
    for i in range(64):
        S1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
        ch = (e & f) ^ ((~e & 0xFFFFFFFF) & g)
        t1 = (hh + S1 + ch + K[i] + w[i]) & 0xFFFFFFFF
        S0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
        maj = (a & b) ^ (a & c) ^ (b & c)
        t2 = (S0 + maj) & 0xFFFFFFFF
        hh, g, f, e = g, f, e, (d + t1) & 0xFFFFFFFF
        d, c, b, a = c, b, a, (t1 + t2) & 0xFFFFFFFF
    return [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, hh])]

def md_pad(msg):
    n = len(msg)
    bits = n * 8
    msg += b'\x80'
    while len(msg) % 64 != 56:
        msg += b'\x00'
    return msg + struct.pack('>Q', bits)

def state_from_hex(hexstr):
    return list(struct.unpack('>8I', bytes.fromhex(hexstr)))

def state_to_hex(st):
    return struct.pack('>8I', *st).hex()

def extend_hex(st, data):
    """digest of a 1-block continuation (len(data)==64) from state st, as hex."""
    return state_to_hex(compress(st, data))

def test_compress():
    import os, random
    ok = True
    for L in (0, 1, 21, 55, 56, 63, 64, 65, 66, 119, 120, 127, 128, 130):
        m = os.urandom(L)
        pad = md_pad(m)
        st = H0
        for i in range(0, len(pad), 64):
            st = compress(st, pad[i:i+64])
        got = state_to_hex(st)
        exp = hashlib.sha256(m).hexdigest()
        if got != exp:
            ok = False
            print(f'FAIL L={L}: {got} != {exp}')
    # length-extension property check
    m = os.urandom(21)
    st = state_from_hex(hashlib.sha256(m).hexdigest())
    pad_L = b'\x80' + b'\x00' * 34 + struct.pack('>Q', 168)   # padding of the 21-byte msg
    tail = b'\xAA' + b'\x80' + b'\x00' * 54 + struct.pack('>Q', (21 + len(pad_L) + 1) * 8)
    ext = state_to_hex(compress(st, tail))
    exp = hashlib.sha256(m + pad_L + b'\xAA').hexdigest()
    if ext != exp:
        ok = False
        print('FAIL extension:', ext, exp)
    print('compress test:', 'OK' if ok else 'FAILED')
    return ok

if __name__ == '__main__':
    test_compress()
