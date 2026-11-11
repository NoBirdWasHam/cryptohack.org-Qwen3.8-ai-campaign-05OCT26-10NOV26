# ECLCG solve — port of author solve2.py (maple3142 My-CTF-Challenges,
# HITCON CTF 2024/ECLCG/solution/solve2.py; ALGORITHM only, final flag line ignored).
# sage flatter->fpylll LLL (author's lib itself falls back to LLL <4096b),
# change_ring(Zmod).echelon -> custom mod-prime echelon, left_kernel -> sympy nullspace.
import math
import hashlib
import os
import shutil
import subprocess
import re
from fpylll import IntegerMatrix, LLL
import sympy as sp
from Crypto.Cipher import AES

FLATTER = shutil.which("flatter") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "flatter", "flatter.exe")

def flatter_reduce(rows):
    z = "[[" + "]\n[".join(" ".join(str(x) for x in row) for row in rows) + "]]"
    out = subprocess.run([FLATTER], input=z.encode(), capture_output=True).stdout
    toks = re.findall(rb"-?\d+", out)
    nr, nc = len(rows), len(rows[0])
    if len(toks) != nr * nc:
        raise RuntimeError(f"flatter output shape {len(toks)} != {nr}x{nc}: {out[:200]}")
    it = iter(toks)
    return [[int(next(it)) for _ in range(nc)] for _ in range(nr)]

def lll_rows(rows, use_flatter=True):
    if use_flatter and os.path.exists(FLATTER):
        return flatter_reduce(rows)
    IM = IntegerMatrix(len(rows), len(rows[0]))
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            IM[i, j] = v
    LLL.reduction(IM, delta=0.99)
    return [[int(IM[i, j]) for j in range(IM.ncols)] for i in range(IM.nrows)]

Q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

MSGS = [
 b"https://www.youtube.com/watch?v=kv4UD4ICd_0",
 b"https://www.youtube.com/watch?v=IijOKxLclxE",
 b"https://www.youtube.com/watch?v=GH6akWYAtGc",
 b"https://www.youtube.com/watch?v=Y3JhUFAa9bk",
 b"https://www.youtube.com/watch?v=FGID8CJ1fUY",
 b"https://www.youtube.com/watch?v=_BfmEjHVYwM",
 b"https://www.youtube.com/watch?v=zH7wBliAhT0",
 b"https://www.youtube.com/watch?v=NROQyBPX9Uo",
 b"https://www.youtube.com/watch?v=ylH6VpJAoME",
 b"https://www.youtube.com/watch?v=hI34Bhf5SaY",
 b"https://www.youtube.com/watch?v=bef23j792eE",
 b"https://www.youtube.com/watch?v=ybvXNOWX-dI",
 b"https://www.youtube.com/watch?v=dt3p2HtLzDA",
 b"https://www.youtube.com/watch?v=1Z4O8bKoLlU",
 b"https://www.youtube.com/watch?v=S53XDR4eGy4",
 b"https://www.youtube.com/watch?v=ZK64DWBQNXw",
 b"https://www.youtube.com/watch?v=tLL8cqRmaNE",
]

def lll_rows(rows):
    IM = IntegerMatrix(len(rows), len(rows[0]))
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            IM[i, j] = v
    LLL.reduction(IM, delta=0.99)
    return [[int(IM[i, j]) for j in range(IM.ncols)] for i in range(IM.nrows)]

def find_ortho_fp(pmod, vecs):
    # N rows [vecs[j][i]*pmod | e_i]  +  nv rows [pmod^2 at col j | 0]
    # (sage scalar blocks are SCALAR MATRICES: [ZZ(p),0] == nv rows p*I_nv,
    #  then col-scale x p => p*p on the diagonal; quotients independent per family)
    N = len(vecs[0]); nv = len(vecs)
    L = []
    for i in range(N):
        row = [vecs[j][i] for j in range(nv)]
        row = [x * pmod for x in row] + [1 if k == i else 0 for k in range(N)]
        L.append(row)
    for j in range(nv):
        L.append([pmod * pmod if k == j else 0 for k in range(nv)] + [0] * N)
    red = lll_rows(L)
    ret = [r[nv:] for r in red if all(x == 0 for x in r[:nv])]
    return ret

def echelon_mod_p(M, p):
    # row echelon over GF(p) (rows independent-ish); returns nonzero echelon rows
    M = [row[:] for row in M]
    nr = len(M); nc = len(M[0])
    r = 0
    for c in range(nc):
        piv = None
        for i in range(r, nr):
            if M[i][c] % p != 0:
                piv = i; break
        if piv is None: continue
        M[r], M[piv] = M[piv], M[r]
        inv = pow(M[r][c], -1, p)
        M[r] = [x * inv % p for x in M[r]]
        for i in range(nr):
            if i != r and M[i][c] % p != 0:
                f = M[i][c] % p
                M[i] = [(a - f * b) % p for a, b in zip(M[i], M[r])]
        r += 1
        if r == nr: break
    return M[:r], r, nc

def reduce_mod_p(p, M):
    Me, nr, nc = echelon_mod_p(M, p)
    rows = [row[:] for row in Me]
    for k in range(nc - nr):
        row = [0]*nr + [p if j == k else 0 for j in range(nc - nr)]
        rows.append(row)
    return lll_rows(rows)

def solve(sigs, ct, nonce, msgs, verbose=True):
    q = Q
    n = len(sigs)
    zs = [int.from_bytes(hashlib.sha256(m).digest(), "big") % q for m in msgs]
    v1 = []; v2 = []
    for i in range(n-1):
        r1, s1 = sigs[i]; r2, s2 = sigs[i+1]
        s1i = pow(s1, -1, q); s2i = pow(s2, -1, q)
        v1.append(s1i*zs[i] - s2i*zs[i+1])
        v2.append(s1i*r1 - s2i*r2)
    ortho = find_ortho_fp(q, [v1, v2])
    if verbose: print("ortho dim:", len(ortho), "x", len(ortho[0]))
    ortho2 = find_ortho_fp(q, ortho)
    if verbose: print("ortho2 dim:", len(ortho2), "x", (len(ortho2[0]) if ortho2 else 0))
    if not ortho2: return None
    n1 = n - 1
    n2rows = len(ortho2); n2cols = len(ortho2[0])
    # AT rows = columns of ortho2; sage ortho2.T[:-1]/[1:] drop LAST/FIRST ROWS (not cols).
    AT = [[ortho2[c][r] for c in range(n2rows)] for r in range(n2cols)]
    M = [f + b for f, b in zip(AT[:-1], AT[1:])]
    p2 = 2**255 - 19
    T = reduce_mod_p(p2, M)
    if verbose: print("T dim:", len(T), "x", len(T[0]))
    L2 = []
    for row in T[: n - 4]:
        L2.append(list(row[:n1]))
        L2.append(list(row[n1:]))
    ker = sp.Matrix(L2).nullspace()   # L2 * mu = 0
    if verbose: print("mu kernel dim:", len(ker))
    def ec_valid(d):
        P256 = (1<<256) - (1<<32) - 977
        GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
        GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
        def padd(A, B):
            if A is None: return B
            if B is None: return A
            x1,y1=A; x2,y2=B
            if x1==x2 and (y1+y2)%P256==0: return None
            if A==B: lam=(3*x1*x1)*pow(2*y1,-1,P256)%P256
            else: lam=(y2-y1)*pow(x2-x1,-1,P256)%P256
            x3=(lam*lam-x1-x2)%P256; y3=(lam*(x1-x3)-y1)%P256
            return (x3,y3)
        def pmul_(k):
            R=None; Aa=(GX,GY)
            while k:
                if k&1: R=padd(R,Aa)
                Aa=padd(Aa,Aa); k>>=1
            return R
        for (r,s),z in zip(sigs, zs):
            k = (z + r*d) * pow(s,-1,q) % q
            pt = pmul_(k)
            if pt is None or pt[0] % q != r: return False
        return True
    for kv in ker:
        den = sp.lcm([sp.Rational(x).q for x in kv])
        mu = [int(x*den) for x in kv]
        g = 0
        for t_ in mu: g = math.gcd(g, t_)
        if g > 1: mu = [t_ // g for t_ in mu]
        if len(mu) != len(ortho2):
            continue
        # diff_k = mu * ortho2  (row vector times matrix)
        diff_k = [sum(mu[c] * ortho2[c][i] for c in range(len(mu))) for i in range(n2cols)]
        for sgn in (1, -1):
            dk = sgn * diff_k[0]
            # solve s0*(k1+dk) = z0 + r0*d ; s1*k1 = z1 + r1*d  over GF(q)
            z0, r0, s0 = zs[0], sigs[0][0], sigs[0][1]
            z1, r1, s1 = zs[1], sigs[1][0], sigs[1][1]
            # from eq2: k1 = (z1 + r1 d)/s1. sub into eq1:
            # s0*(z1 + r1 d)/s1 + s0*dk = z0 + r0 d
            # d*(s0*r1/s1 - r0) = z0 - s0*z1/s1 - s0*dk
            A = (s0*r1*pow(s1,-1,q) - r0) % q
            B = (z0 - s0*z1*pow(s1,-1,q) - s0*dk) % q
            if A % q == 0: continue
            d = B * pow(A, -1, q) % q
            if ec_valid(d):
                key = hashlib.sha256(str(d).encode()).digest()
                flag = AES.new(key, AES.MODE_CTR, nonce=nonce).decrypt(ct)
                return d, flag
    return None

if __name__ == "__main__":
    import sys
    ns = {}
    exec(open(sys.argv[1]).read(), ns)
    out = solve(ns["sigs"], ns["ct"], ns["nonce"], MSGS[:len(ns["sigs"])])
    if out is None: print("FAILED")
    else: print("d =", out[0]); print("FLAG:", out[1])
