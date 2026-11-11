#!/usr/bin/env python3
"""ed25519_magic (ICC Athens) solver.

Vuln: ed25519 1.5 C ext (supercop-ref) crypto_sign_open:
  - sc25519_from32bytes barrett-reduces S mod L  -> S' = S + L verifies, different bytes
  - ge25519_unpackneg_vartime: no subgroup / identity / canonical checks
  - no S < L check, no sm[63]&224 check
Level 1: forge sig' = R || LE32(s+L) on b"CryptoHack".
Level 2: vk = identity point (01||0*31), sig = identity R || 32 zero bytes:
  check is pack(0*B - h*O) == R  ->  pack(O) == 01||0*31  ->  True for ANY msg.
"""
import base64, hashlib, socket, sys

p  = 2**255 - 19
L  = 2**252 + 27742317777372353535851937790883648493
d  = -121665 * pow(121666, p-2, p) % p
Gy = 4 * pow(5, p-2, p) % p

def xrecover(y):
    xx = (y*y-1) * pow(d*y*y+1, p-2, p)
    x = pow(xx, (p+3)//8, p)
    if (x*x - xx) % p != 0:
        x = x * pow(2, (p-1)//4, p) % p
    if x % 2 != 0: x = p - x
    return x % p

def G():
    return (xrecover(Gy), Gy, 1)

def padd(P, Q):  # affine, twisted Edwards a=-1
    if P is None: return Q
    if Q is None: return P
    x1,y1 = P[0],P[1]; x2,y2 = Q[0],Q[1]
    t = d*x1*x2 % p * y1 % p * y2 % p
    x3 = (x1*y2 + x2*y1) % p * pow((1 + t) % p, p-2, p) % p
    y3 = (y1*y2 + x1*x2) % p * pow((1 - t) % p, p-2, p) % p
    return (x3, y3, 1)

def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = padd(P, P); k >>= 1
    return R

def neg(P):
    return None if P is None else ((-P[0]) % p, P[1], 1)

def decodepoint_nocheck(b):
    y = int.from_bytes(b[:31], 'little') | ((b[31] & 127) << 248)
    sign = b[31] >> 7
    x2 = (y*y - 1) * pow(d*y*y + 1, p-2, p) % p
    if x2 == 0:
        x = 0
    else:
        x = pow(x2, (p+3)//8, p)
        if (x*x - x2) % p != 0:
            x = x * pow(2, (p-1)//4, p) % p
        if (x % 2) != (1 - sign):   # C: parity != 1-par -> negate
            x = p - x
    return (x % p, y, 1)

def encodepoint(P):
    if P is None: y, x = 1, 0
    else:
        zi = pow(P[2], p-2, p)
        x = P[0]*zi % p; y = P[1]*zi % p
    b = y.to_bytes(32,'little')
    return b[:31] + bytes([b[31] | ((x & 1) << 7)])

def verify_lax(pk, sig, msg):
    """emulate crypto_sign_open of ed25519-supercop-ref exactly"""
    A = decodepoint_nocheck(pk)
    h = int.from_bytes(hashlib.sha512(sig[:32] + pk + msg).digest(), 'little') % L
    s = int.from_bytes(sig[32:], 'little') % L
    get2 = padd(pmul(s, G()), pmul(h, A))  # A here is already -A_std (unpackneg parity rule)
    return encodepoint(get2) == sig[:32]

IDENT = bytes([1]) + b'\x00'*31

def local_test():
    import os, secrets
    sk = secrets.randbelow(L-1)+1
    vk = encodepoint(pmul(sk, G()))
    msg = b"CryptoHack"
    r = secrets.randbelow(L-1)+1
    R = pmul(r, G())
    h = int.from_bytes(hashlib.sha512(encodepoint(R)+vk+msg).digest(),'little') % L
    s = (r + h*sk) % L
    sig = encodepoint(R) + s.to_bytes(32,'little')
    assert verify_lax(vk, sig, msg), "baseline sig rejected"
    forged = sig[:32] + ((s+L) % 2**256).to_bytes(32,'little')
    assert forged != sig and verify_lax(vk, forged, msg), "L1 forge failed"
    print("L1 forge (s+L) OK")
    sig2 = IDENT + b'\x00'*32
    assert verify_lax(IDENT, sig2, os.urandom(16)), "L2 identity forge failed"
    assert verify_lax(IDENT, sig2, os.urandom(16)), "L2 identity forge failed"
    print("L2 identity-key forge OK")

def live(host="archive.cryptohack.org", port=31144):
    s = socket.create_connection((host, port), timeout=30); s.settimeout(25)
    f = s.makefile('rwb')
    def rd():
        line = f.readline()
        if not line: raise EOFError
        print("S:", line.decode().rstrip())
        return line.decode().rstrip()
    def wr(x):
        f.write(x.encode()+b"\n"); f.flush()
    prev = ""
    for _ in range(6):
        t = rd()
        if t.startswith("Enter new signature"): break
        prev = t
    sig = base64.b64decode(prev)
    s_int = int.from_bytes(sig[32:], 'little')
    forged = sig[:32] + ((s_int + L) % 2**256).to_bytes(32,'little')
    wr(base64.b64encode(forged).decode())
    for _ in range(8):
        t = rd()
        if t.startswith("Enter verifying key"): break
    else:
        raise RuntimeError("did not reach level 2")
    wr(base64.b64encode(IDENT).decode())
    rd()  # Enter signature:
    wr(base64.b64encode(IDENT + b'\x00'*32).decode())
    for _ in range(4):
        t = rd()
        if "crypto{" in t:
            print("FLAG:", t); return t
    return None

if __name__ == "__main__":
    if "--local" in sys.argv:
        local_test()
    else:
        live()
