# Offline check: information-theoretic identifiability of E=AES_K(J0) from server tags.
# Model (verified numerically in a prior run against pycryptodome GCM):
#   state s=[A,C], A=m blocks, C=n blocks, every block a uniform element of the
#   96-dim subspace V = {x in GF(2^128): last 4 bytes zero} (server blocks are 12 bytes).
#   T = sum a_i H^{n+m+1-i} + sum c_j H^{n+1-j} + L(m,n) H + E   (GCM GHASH)
# Goal of player: output E. Equivalently: for the observed transcript, is E unique
# over all worlds (H',E',block values in V) consistent with it?
#
# Alternate-world kernel: E' = E ^ DELTA is consistent iff DELTA lies in the
# intersection of subspaces imposed by each observed operation type:
#   u2-chain on C (known path) : DELTA in (H+1)^{-1} V      (shift every appended block by (H+1)DELTA)
#   u2-chain on A (known path) : DELTA in H^2 (H+1)^{-1} V
#   u1 hitting C only (2 tags) : DELTA in H  V              ((c'^c)H = DELTA)
#   u1 hitting A only (2 tags) : DELTA in H^2 V
# This script computes the dimension of intersections of these subspaces for random H.

P = (1 << 128) + (1 << 7) + (1 << 2) + (1 << 1) + 1  # GCM poly x^128+x^7+x^2+x+1

def clmul(a, b):
    r = 0
    while b:
        if b & 1: r ^= a
        b >>= 1; a <<= 1
        if a & (1 << 128): a ^= P
    return r

def inverse(a):
    r, s = a, P
    t, u = 1, 0
    deg = lambda x: x.bit_length() - 1
    while r and deg(r) >= 128:
        sh = deg(r) - deg(s)
        r ^= s << sh; t ^= u << sh
    if not r:  # r==0: s divides P -> invert s mod P
        r, t = s, u
        return None
    return t

def gf_inv(a):  # inverse in GF(2^128) via x^(2^128-2)
    r, b = 1, a
    for _ in range(127):
        if r & 1: pass
        b = clmul(b, b)
        r = clmul(r, r)
        r ^= 0  # placeholder
    # simpler: square-and-multiply exponent 2^128-2 = sum of 2^k, k=1..127
    r, p = 1, a
    for k in range(128):
        if k >= 1:
            r = clmul(r, p)
        p = clmul(p, p)
    return r

def basis(x):
    """GF(2)-basis of the span of {x*v : v in V}; V = multiples of x^32 (top... low 32 bits free?).
    Define V = elements whose low 32 bits are zero, i.e. span of x^32..x^127 (multiply by 2^32-aligned)."""
    return [clmul(x, 1 << (32 + i)) for i in range(96)]

def intersect(b1, b2):
    """dim of intersection of two subspace bases via row-reduction over GF(2) of stacked [b1|b2] trick:
    dim(A&B) = dim A + dim B - dim(A+B)."""
    def rank(bs):
        rows = bs[:]
        piv = {}
        for r0 in rows:
            r = r0
            while r:
                i = r.bit_length() - 1
                if i in piv: r ^= piv[i]
                else: piv[i] = r; break
        return len(piv)
    return rank(b1) + rank(b2) - rank(b1 + b2)

import random
random.seed(1)
for trial in range(3):
    H = random.getrandbits(128) | 1
    V  = basis(1)
    HV = basis(H); H2V = basis(clmul(H, H))
    # (H+1)^{-1} V and H^2 (H+1)^{-1} V
    inv = gf_inv(H ^ 1)
    C_c = basis(inv); C_a = basis(clmul(clmul(H, H), inv))
    d1 = intersect(HV, H2V)
    d2 = intersect(basis(clmul(HV[0],0)) if False else HV, C_c)
    # triple
    t = intersect(HV, C_c); t3 = intersect(H2V, C_c)
    print(f"trial {trial}: dim V={len(basis(1))} HVcapH2V={d1}  HVcap(H+1)^-1V={t}  H2Vcap(H+1)^-1V={t3}")
    # full 3-way
    def rank(bs):
        piv={}
        for r0 in bs:
            r=r0
            while r:
                i=r.bit_length()-1
                if i in piv: r^=piv[i]
                else: piv[i]=r; break
        return len(piv)
    ab = intersect(HV, C_c)
    # basis of HV cap C_c by brute force (96x96 solve) then intersect with H2V and C_a
    def inter_basis(b1, b2):
        # solve sum a_i u_i = sum b_j w_j  -> pairs
        u,w = b1,b2
        # build matrix [u | w] columns, find dependencies
        import itertools
        cols = u + w
        # row reduce columns as vectors over GF(2) tracking combos
        piv = {}  # bit -> (colidx, combo_mask_u, combo_mask_w)
        sols = []
        for idx,vec in enumerate(cols):
            cu = 1<<idx if idx<len(u) else 0
            cw = 1<<(idx-len(u)) if idx>=len(u) else 0
            r, a_u, a_w = vec, cu, cw
            inserted = False
            while r:
                i = r.bit_length()-1
                if i in piv:
                    r ^= piv[i][0]; a_u ^= piv[i][1]; a_w ^= piv[i][2]
                else:
                    piv[i] = (r,a_u,a_w); r = 0; inserted = True; break
            if not inserted and r == 0 and (a_u or a_w):
                # dependency: sum a_u u = sum a_w w
                val = 0; m = a_u
                j = 0
                while m:
                    if m & 1: val ^= u[j]
                    m >>= 1; j += 1
                sols.append(val)
        return sols
    X = inter_basis(HV, C_c)
    Y = inter_basis(X, H2V)
    Z = inter_basis(Y, C_a)
    print(f"   dim(HV & C_c)={len(X)}  & H2V={len(Y)}  & C_a={len(Z)}  (0 => E identifiable given H)")
