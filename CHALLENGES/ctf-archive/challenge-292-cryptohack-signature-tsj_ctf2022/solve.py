# TSJ CTF 2022 "Signature": ECDSA variant with nonce k = d XOR z.
#   s = k^-1 (z + r d) mod q  =>  d (s-r) - 2 s (d & z) = z (1-s) mod q
#   => sum_j 2^j d_j ((s-r) - 2 s z_j) = (1-s) z mod q,  d_j in {0,1}
# 6 eqs, 256 binary unknowns -> CVP in kernel lattice of M mod q (det q^6),
# target = particular solution x0; true d is at distance ~sqrt(128) << GH (~250).
# Stages: LLL+Babai -> BKZ(20)+Babai -> BKZ(30)+exact CVP.
# Run: ~/tools/crypto-ctf/venv/Scripts/python.exe solve.py [sim|real]
import sys, ast
from hashlib import sha256
from Crypto.Cipher import AES

q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 256

def ec_add(P1, P2):
    if P1 is None: return P2
    if P2 is None: return P1
    x1, y1 = P1; x2, y2 = P2
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P1 == P2:
        m = (3 * x1 * x1) * pow(2 * y1, -1, p) % p
    else:
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)

def ec_mul(P, n):
    R = None
    while n:
        if n & 1: R = ec_add(R, P)
        P = ec_add(P, P); n >>= 1
    return R
G = (Gx, Gy)

def load(path):
    Z, R, S = [], [], []
    ct = None
    for line in open(path).read().split('\n'):
        parts = line.split()
        if len(parts) == 3 and all(t.isdigit() for t in parts):
            Z.append(int(parts[0])); R.append(int(parts[1])); S.append(int(parts[2]))
        elif line.strip().startswith("b'"):
            ct = bytes(ast.literal_eval(line.strip()))
    return Z, R, S, ct

def build_system(Z, R, S):
    M, v = [], []
    for z, r, s in zip(Z, R, S):
        row = [ (pow(2, j, q) * (((s - r) - 2 * s * ((z >> j) & 1)) % q)) % q for j in range(N) ]
        M.append(row)
        v.append(((1 - s) * z) % q)
    return M, v

def particular(M, v):
    """Particular solution of M x = v mod q (free vars = 0) or None."""
    m = len(M)
    rows = [list(M[i]) + [v[i]] for i in range(m)]
    piv, used = [], set()
    for i in range(m):
        for j in range(N):
            if j in used: continue
            if rows[i][j] % q:
                inv = pow(rows[i][j], -1, q)
                rows[i] = [(t * inv) % q for t in rows[i]]
                for k in range(m):
                    if k != i and rows[k][j] % q:
                        c = rows[k][j]
                        rows[k] = [(a - c * b) % q for a, b in zip(rows[k], rows[i])]
                piv.append(j); used.add(j)
                break
        else:
            return None
    x0 = [0] * N
    for i, j in enumerate(piv): x0[j] = rows[i][N] % q
    return x0

def kernel_basis(M):
    from fpylll import IntegerMatrix, LLL
    m = len(M)
    B = IntegerMatrix(m + N, N)
    for i in range(m):
        for j in range(N): B[i, j] = M[i][j] % q
    for i in range(N): B[m + i, i] = q
    LLL.reduction(B)
    keep = [i for i in range(m + N) if any(B[i, j] for j in range(N))]
    assert len(keep) == N, f"rank {len(keep)} != {N}"
    C = IntegerMatrix(N, N)
    for r, i in enumerate(keep):
        for j in range(N): C[r, j] = B[i, j]
    return C

def try_candidate(vec, Z, R):
    d = sum(vec[j] << j for j in range(N))
    if d >= q or d <= 0: return None
    for z, r in zip(Z, R):
        k = d ^ z  # challenge uses UNreduced k (z is raw sha256, may exceed q)
        if k % q == 0: return None
        P = ec_mul(G, k)
        if P is None or P[0] != r: return None
    return d

def solve_cvp(M, v, Z, R, stage='auto'):
    from fpylll import CVP, BKZ
    x0 = particular(M, v)
    if x0 is None:
        print('no particular solution'); return None
    B = kernel_basis(M)
    def check(w, flip=True):
        x = [x0[j] - int(w[j]) for j in range(N)]
        bad = [j for j, t in enumerate(x) if t not in (0, 1)]
        if len(bad) == 0:
            return try_candidate(x, Z, R)
        if flip and len(bad) <= 12:
            print(f'  {len(bad)} nonbinary coords -> trying {2**len(bad)} flips')
            for mask in range(1 << len(bad)):
                y = list(x)
                for b, j in enumerate(bad):
                    y[j] = (mask >> b) & 1
                d = try_candidate(y, Z, R)
                if d is not None: return d
        else:
            print('  nonbinary diff:', len(bad), 'entries')
        return None
    order = ['babai', 'bkz20', 'cvp30'] if stage == 'auto' else [stage]
    for st in order:
        if st == 'babai':
            print('stage LLL+babai')
            d = check(CVP.babai(B, x0))
        elif st == 'bkz20':
            print('stage BKZ(20)+babai')
            BKZ.reduction(B, BKZ.Param(20))
            d = check(CVP.babai(B, x0))
        elif st == 'cvp30':
            print('stage BKZ(30)+exact CVP')
            BKZ.reduction(B, BKZ.Param(30))
            d = check(CVP.closest_vector(B, x0))
        else:
            d = None
        if d is not None:
            print(f'recovered d at stage {st} =', d)
            return d
        print(f'stage {st} failed')
    return None

def decrypt(d, ct):
    key = sha256(str(d).encode()).digest()[:16]
    from Crypto.Util import Counter
    variants = []
    if ct and len(ct) > 8:
        n0, body = ct[:8], ct[8:]
        variants.append(('prefix iv0', AES.new(key, AES.MODE_CTR, counter=Counter.new(64, prefix=n0, initial_value=0)), body))
        variants.append(('prefix iv1', AES.new(key, AES.MODE_CTR, counter=Counter.new(64, prefix=n0, initial_value=1)), body))
        variants.append(('nonce default', AES.new(key, AES.MODE_CTR, nonce=n0), body))
        variants.append(('suffix iv1', AES.new(key, AES.MODE_CTR, counter=Counter.new(64, suffix=n0, initial_value=1)), ct[:-8]))
    variants.append(('zero128 iv0', AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=0)), ct))
    for name, c, data in variants:
        pt = c.decrypt(data)
        if b'Congrats' in pt:
            print(f'[{name}] PT: {pt.decode(errors="replace")}')
            return pt
    # KPA nonce recovery: server pycryptodome >=3.21 drops the random 8-byte
    # nonce (not prepended). Known plaintext 'Congrats! This i' + AES-128-ECB
    # decrypt of (P0 ^ ct[:16]) under our key yields the counter block; its
    # first 8 bytes are the nonce when the low 64 bits are zero.
    P0 = b'Congrats! This i'
    ecb = AES.new(key, AES.MODE_ECB)
    ks0 = bytes(a ^ b for a, b in zip(P0, ct[:16]))
    cb = ecb.decrypt(ks0)
    if cb[8:] == b'\x00' * 8:
        c = AES.new(key, AES.MODE_CTR, counter=Counter.new(64, prefix=cb[:8], initial_value=0))
        pt = c.decrypt(ct)
        print(f'[kpa-nonce {cb[:8].hex()}] PT: {pt.decode(errors="replace")}')
        return pt
    print('decryption variants failed; first variant gives:', variants[0][1].decrypt(variants[0][2])[:40])
    return None

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'real'
    msgs = ["https://www.youtube.com/watch?v=16M9oC-a5bY","https://www.youtube.com/watch?v=QDadz5JZCw8",
            "https://www.youtube.com/watch?v=kyNh7KnsTN0","https://www.youtube.com/watch?v=Lqn42JJxS3I",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ","https://www.youtube.com/watch?v=1Gw_-E784l0"]
    if mode == 'sim':
        import random
        d = random.randrange(1, q)
        Z, R, S = [], [], []
        for m in msgs:
            z = int(sha256(m.encode()).hexdigest(), 16)
            k = d ^ z
            r = ec_mul(G, k % q)[0]
            s = pow(k % q, -1, q) * (z + r * d) % q
            Z.append(z); R.append(r); S.append(s)
        M, v = build_system(Z, R, S)
        print('sim: particular ok:', particular(M, v) is not None)
        d2 = solve_cvp(M, v, Z, R, stage='auto')
        print('SIM SUCCESS' if d2 == d else f'SIM FAIL got {d2}')
    else:
        Z, R, S, ct = load('output.txt')
        assert len(Z) == 6
        M, v = build_system(Z, R, S)
        d = solve_cvp(M, v, Z, R, stage='auto')
        if d is not None:
            decrypt(d, ct)

if __name__ == '__main__':
    main()
