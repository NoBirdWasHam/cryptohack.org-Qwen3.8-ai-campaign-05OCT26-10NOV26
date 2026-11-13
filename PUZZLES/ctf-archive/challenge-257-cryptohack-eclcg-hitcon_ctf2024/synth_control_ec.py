# ECLCG (HITCON CTF 2024) solve — port of Connor McCartney's verified writeup
# (connor-mccartney.github.io/cryptography/ecc/ECLCG-HITCON-2024, cited 2026-11-08).
# Method: consecutive-pair linearization kk_i = k_{i+1}-k_i = u_i d + v_i (mod q);
# short integer combos c annihilating u,v AND shifted u,v mod q (Stern-style lattice);
# linear system on symbolic kk -> kernel -> kk -> d -> AES-CTR flag. LCG mod p handled
# implicitly; p never recovered. Sage->python/fpylll/sympy port by parent, 2026-11-08.
import sys, hashlib
from math import gcd
from Crypto.Cipher import AES
from fpylll import IntegerMatrix, LLL
import sympy as sp

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

# EC point ops (secp256k1) for verification only
P256 = (1<<256) - (1<<32) - 977
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

def padd(P, Qp, mod=P256):
    if P is None: return Qp
    if Qp is None: return P
    x1,y1=P; x2,y2=Qp
    if x1==x2 and (y1+y2)%mod==0: return None
    if P==Qp: lam=(3*x1*x1)*pow(2*y1,-1,mod)%mod
    else: lam=(y2-y1)*pow(x2-x1,-1,mod)%mod
    x3=(lam*lam-x1-x2)%mod; y3=(lam*(x1-x3)-y1)%mod
    return (x3,y3)
def pmul(k, Pt, mod=P256):
    R=None; A=Pt
    while k:
        if k&1: R=padd(R,A,mod)
        A=padd(A,A,mod); k>>=1
    return R

def solve(sigs, ct, nonce, msgs, verbose=True):
    assert len(sigs)==len(msgs)
    zs = [int.from_bytes(hashlib.sha256(m).digest(),"big") % Q for m in msgs]
    n = len(sigs)
    us=[]; vs=[]
    for i in range(n-1):
        (r1,s1),(r2,s2) = sigs[i], sigs[i+1]
        z1,z2 = zs[i], zs[i+1]
        s1i=pow(s1,-1,Q); s2i=pow(s2,-1,Q)
        us.append((r2*s2i - r1*s1i) % Q)
        vs.append((z2*s2i - z1*s1i) % Q)
    U = us; V = vs
    U2 = us[1:] + [0]; V2 = vs[1:] + [0]   # shifted families, zero-padded to same length
    m = len(U)                 # pairs
    # short combos c in Z^m with c.U = c.V = c.U2 = c.V2 = 0 mod Q
    # kernel basis over Z_Q via Gauss, then LLL of <lifts, Q*I>
    A = [U, V, U2, V2]
    rows = [[A[j][i] for i in range(m)] for j in range(4)]
    M = sp.Matrix(rows)
    kb = M.change_domain(sp.GF(Q)).rref()[0].nullspace() if False else None
    # sympy GF rref: build augmented manually
    Mgf = sp.Matrix(rows)
    piv = []
    mat = [r[:] for r in rows]
    r_ = 0
    for col in range(m):
        sel = None
        for rr in range(r_, 4):
            if mat[rr][col] % Q != 0: sel = rr; break
        if sel is None: continue
        mat[r_], mat[sel] = mat[sel], mat[r_]
        inv = pow(mat[r_][col], -1, Q)
        mat[r_] = [(x*inv) % Q for x in mat[r_]]
        for rr in range(4):
            if rr != r_ and mat[rr][col] % Q != 0:
                fct = mat[rr][col]
                mat[rr] = [(a - fct*b) % Q for a,b in zip(mat[rr], mat[r_])]
        piv.append(col); r_ += 1
    free = [c for c in range(m) if c not in piv]
    lifts = []
    for fc in free:
        v = [0]*m; v[fc] = 1
        for i,pc in enumerate(piv):
            v[pc] = (-mat[i][fc]) % Q
        lifts.append(v)
    gens = lifts + [[Q if i==j else 0 for j in range(m)] for i in range(m)]
    t = len(gens)
    IM = IntegerMatrix(t, m)
    for i,row in enumerate(gens):
        for j,v in enumerate(row): IM[i,j] = v
    LLL.reduction(IM)
    combs = []
    for i in range(min(t, 2*(m)+0)):
        row = [int(IM[i,j]) for j in range(m)]
        if not any(row): continue
        ok = all(sum(a*b for a,b in zip(row,fam)) % Q == 0 for fam in (U,V,U2,V2))
        if ok: combs.append(row)
    if verbose: print("annihilator combs:", len(combs))
    # linear system on symbolic kk_0..kk_m
    NEQ = len(combs)
    E = sp.zeros(2*NEQ, m+1)
    for e_i, c in enumerate(combs):
        for j in range(m):
            E[e_i, j] += c[j]
            E[NEQ + e_i, j+1] += c[j]
    ker = E.nullspace()
    if verbose: print("kernel dim:", len(ker))
    best = None
    for kv in ker:
        den = sp.lcm([sp.Rational(1,1)] + [sp.Rational(x).q for x in kv])
        vv = [int((x*den)) for x in kv]
        for mm in (1, -1):
            kk = [(mm*x) % Q for x in vv]
            d = (kk[0] - V[0]) * pow(U[0], -1, Q) % Q
            # verify all sigs
            good = True
            for i,(r,s) in enumerate(sigs):
                k = (zs[i] + r*d) * pow(s,-1,Q) % Q
                pt = pmul(k, (GX,GY))
                if pt is None or pt[0] % Q != r: good=False; break
            if good:
                best = d
                break
        if best: break
    if best is None:
        return None
    key = hashlib.sha256(str(best).encode()).digest()
    from Crypto.Util.Counter import Counter
    # pycryptodome CTR with 8-byte nonce: full-block counter starting with nonce
    counter = AES.new(key, AES.MODE_CTR, nonce=nonce)
    flag = counter.decrypt(ct)
    return best, flag

if __name__ == "__main__":
    src = sys.argv[1]
    ns={}
    exec(open(src).read(), ns)
    sigs, ct, nonce = ns["sigs"], ns["ct"], ns["nonce"]
    msgs = MSGS[:len(sigs)]
    out = solve(sigs, ct, nonce, msgs)
    if out is None:
        print("NO CANDIDATE PASSED r-CHECK")
    else:
        d, flag = out
        print("d =", d)
        print("FLAG:", flag)
