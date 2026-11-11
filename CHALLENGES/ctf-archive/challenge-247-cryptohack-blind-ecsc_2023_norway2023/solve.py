#!/usr/bin/env python3
# blind (ECSC 2023 Norway) solver.
# Real sig satisfies R = z*G + c*Y (Y = -x*G) with r = x(R) xor m1,
# m1 = F1(m) || (F2(F1(m)) xor m), m = _k (16 bytes).
# Scan all 10000 sigs: compute R, m1 = r xor R_x, m = F2(m1[:40]) xor m1[40:],
# accept iff m1[:40] == F1(m)  (320-bit test -> only real sig passes).
import ast, hashlib, sys, time
import gmpy2
from gmpy2 import mpz
P = (1 << 448) - (1 << 224) - 1
A_ED, D_ED = 1, 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffffffffffffffffffffffffffffffffffffffffffffffff6756
mod = P
A = (-(A_ED*A_ED + 14*A_ED*D_ED + D_ED*D_ED) * pow(48, P-2, P)) % P
B = ((A_ED + D_ED) * (-A_ED*A_ED + 34*A_ED*D_ED - D_ED*D_ED) * pow(864, P-2, P)) % P
ORDER = 0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF7CCA23E9C44EDB49AED63690216CC2728DC58F552378C292AB5844F3

def inv(x): return pow(int(x), P-2, P)

def to_w(x, y):
    x, y = mpz(x) % P, mpz(y) % P
    wx = (5*A_ED + A_ED*y - 5*D_ED*y - D_ED) * inv(12 - 12*y) % P
    wy = (A_ED + A_ED*y - D_ED*y - D_ED) * inv(4*x - 4*x*y) % P
    return (int(wx), int(wy))

GX, GY = to_w(0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa955555555555555555555555555555555555555555555555555555555,
              0xae05e9634ad7048db359d6205086c2b0036ed7a035884dd7b7e36d728ad8c4b80d6565833a2a3098bbbcb2bed1cda06bdaeafbcdea9386ed)

# Jacobian ops
def jdbl(X, Y, Z):
    if Z == 0: return (0, 1, 0)
    ZZ = Z*Z % P; YY = Y*Y % P; YYYY = YY*YY % P
    X = mpz(X); Y = mpz(Y); ZZ = mpz(ZZ); YY = mpz(YY); YYYY = mpz(YYYY)
    S = 2*((X+YY)*(X+YY) - X*X - YYYY) % P
    M = (3*X*X + A * ZZ*ZZ) % P
    T = (M*M - 2*S) % P
    X3 = int(T); Y3 = int(M*(S-T) - 8*YYYY) % P; Z3 = int(2*Y*Z) % P
    return (X3, Y3, Z3)

def jadd_aff(X, Y, Z, x2, y2):
    if Z == 0: return (x2, y2, 1)
    X = mpz(X); Y = mpz(Y); Z = mpz(Z); x2 = mpz(x2); y2 = mpz(y2)
    ZZ = Z*Z % P; U2 = x2*ZZ % P; S2 = y2*Z % P * ZZ % P
    H = U2 - X; R = S2 - Y
    if H == 0:
        if R == 0: return jdbl(X, Y, Z)
        return (0, 1, 0)
    H2 = H*H % P; H3 = H*H2 % P; XH2 = X*H2 % P
    X3 = (R*R - H3 - 2*XH2) % P
    Y3 = (R*(XH2 - X3) - Y*H3) % P
    Z3 = Z*H % P
    return (int(X3), int(Y3), int(Z3))

def to_aff(X, Y, Z):
    if Z == 0: return None
    zi = inv(Z); zi2 = zi*zi % P; zi3 = zi2*zi % P
    return (X*zi2 % P, Y*zi3 % P)

def mul(Ppt, k):
    X, Y, Z = 0, 1, 0
    for bit in bin(k)[2:]:
        X, Y, Z = jdbl(X, Y, Z)
        if bit == '1':
            X, Y, Z = jadd_aff(X, Y, Z, Ppt[0], Ppt[1])
    return to_aff(X, Y, Z)

def Hash(x, nin, n, div):
    nin //= 8; n //= 8; assert len(x) == nin
    r = b""; i = 0
    while len(r) < n:
        r += hashlib.sha256(x + b"||" + div + int(i).to_bytes(8, "big")).digest()
        i += 1
    return r[:n]
F1 = lambda x: Hash(x, 128, 320, b"1")
F2 = lambda x: Hash(x, 320, 128, b"2")
H  = lambda x: Hash(x, 448, 448, b"H")

def main():
    data = open('output.txt').read()
    lines = data.split('\n')
    Yu, Yv = ast.literal_eval(lines[0].split('=',1)[1].strip())
    ct = bytes.fromhex(lines[1].split('=',1)[1].strip())
    sigs = ast.literal_eval(data[data.find('['):].strip())
    print('sigs:', len(sigs), flush=True)
    YW = to_w(Yu, Yv)
    # sanity: G has order ORDER
    t0 = time.time()
    found = []
    for idx, (rh, z) in enumerate(sigs):
        rb = bytes.fromhex(rh)
        c = int.from_bytes(H(rb), 'big') % ORDER
        Rz = mul((GX, GY), z)
        Cy = mul(YW, c)
        if Rz is None or Cy is None: continue
        X, Y, Z = jadd_aff(Rz[0], Rz[1], 1, Cy[0], Cy[1])
        R = to_aff(X, Y, Z)
        if R is None: continue
        m1 = bytes(a ^ b for a, b in zip(rb, R[0].to_bytes(56, 'big')))
        m = bytes(a ^ b for a, b in zip(F2(m1[:40]), m1[40:]))
        if m1[:40] == F1(m):
            found.append((idx, m))
            print('REAL sig at', idx, 'k =', m.hex(), flush=True)
            if time.time()-t0 > 1 and idx < 3: print('rate: %.3f s/sig' % ((time.time()-t0)/(idx+1)), flush=True)
    if not found:
        print('no real sig found'); return
    import bcrypt
    from Crypto.Cipher import AES
    for idx, k in found:
        key = bcrypt.kdf(k, b"ICC_CHALLENGE", 16, 31337)
        pt = AES.new(key, AES.MODE_CTR, nonce=b"").decrypt(ct)
        print('candidate plaintext:', pt, flush=True)

if __name__ == '__main__':
    main()
