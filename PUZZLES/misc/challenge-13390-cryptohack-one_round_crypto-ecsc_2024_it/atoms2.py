#!/usr/bin/env python3
"""Recover byte-subspaces S_j = M3^{-T}(B_j) as dim-8 atoms of the
intersection lattice of the W_i nullspaces."""
import random, itertools, time
from local_oracle import *

def fr(b): return int.from_bytes(b,'big')

def rref(vecs):
    piv={}
    for v in vecs:
        x=v
        while x:
            b=x.bit_length()-1
            if b in piv: x^=piv[b]
            else: piv[b]=x; break
    for b in sorted(piv):
        for b2 in sorted(piv):
            if b!=b2 and (piv[b2]>>b)&1: piv[b2]^=piv[b]
    return list(piv.values())

def nullspace_basis(vecs):
    piv={}
    for v in vecs:
        x=v
        while x:
            b=x.bit_length()-1
            if b in piv: x^=piv[b]
            else: piv[b]=x; break
    free=[b for b in range(128) if b not in piv]
    piv2=rref(vecs)
    pd={v.bit_length()-1:v for v in piv2}
    ns=[]
    for f in free:
        u=1<<f
        for b,r in pd.items():
            if (r>>f)&1: u^=(1<<b)
        ns.append(u)
    return ns

def inter(basisA, basisB):
    N=nullspace_basis(basisB)
    bA=basisA
    piv={}
    for n in N:
        x=0
        for i,bA_i in enumerate(bA):
            if bin(bA_i & n).count('1')&1: x|=1<<i
        while x:
            b=x.bit_length()-1
            if b in piv: x^=piv[b]
            else: piv[b]=x; break
    m=len(bA)
    red=dict(piv)
    for b in sorted(red):
        for b2 in sorted(red):
            if b!=b2 and (red[b2]>>b)&1: red[b2]^=red[b]
    out=[]
    for f in range(m):
        if f not in red:
            a=1<<f
            for b,r in red.items():
                if (r>>f)&1: a^=1<<b
            u=0
            for i in range(m):
                if (a>>i)&1: u^=bA[i]
            out.append(u)
    return rref(out)

def canon(basis):
    return tuple(sorted(v for v in rref(basis)))

def matinv_cols(cols):
    cur=[[cols[b], 1<<b] for b in range(128)]
    piv={}
    for i in range(128):
        while cur[i][0]:
            b=cur[i][0].bit_length()-1
            if b in piv:
                j=piv[b]
                cur[i][0]^=cur[j][0]; cur[i][1]^=cur[j][1]
            else:
                piv[b]=i; break
    inv_cols=[]
    for f in range(128):
        y=1<<f; x=0
        while y:
            b=y.bit_length()-1
            if b in piv:
                j=piv[b]; x^=cur[j][1]; y^=cur[j][0]
            else: break
        chk=0
        for i in range(128):
            if (x>>i)&1: chk^=cols[i]
        assert chk==(1<<f), (f,chk)
        inv_cols.append(x)
    return inv_cols

if __name__=="__main__":
    rng=random.Random(11)
    sess=Session()
    T=200
    Ws=[]
    t0=time.time()
    for i in range(16):
        data=[]
        for _ in range(T):
            p=rng.getrandbits(120).to_bytes(15,'big'); b1=p+b'\x01'
            b2=bytearray(b1); b2[i]^=1; b2=bytes(b2)
            data.append(fr(sess.enc_block(b1))^fr(sess.enc_block(b2)))
        Ws.append(nullspace_basis(data))
    print("nullities",[len(w) for w in Ws],"t=%.1f"%(time.time()-t0))
    atoms={}
    frontier={frozenset([i]):Ws[i] for i in range(16)}
    level=1
    seen_content={}
    while frontier and level<=6:
        new={}
        for key,basis in frontier.items():
            if len(basis)==8:
                atoms[key]=basis
                continue
            if len(basis)<8: continue
            for i in range(16):
                if i in key: continue
                nb=inter(basis,Ws[i])
                if len(nb)>=8:
                    new[frozenset(key|{i})]=nb
        frontier=new
        level+=1
        print("level",level-1,"frontier",len(frontier),"atoms",len(set(canon(b) for b in atoms.values())),"%.1fs"%(time.time()-t0))
    distinct={}
    for key,basis in atoms.items():
        distinct.setdefault(canon(basis),basis)
    print("distinct dim-8 atoms:",len(distinct))
    M3T = lin_matrix(lambda v: fr(mix(v.to_bytes(16,'big'), sess.k3)))
    Minv=matinv_cols(M3T)
    for j in range(16):
        Sj=canon([Minv[8*j+b] for b in range(8)])
        print("S_byte",j,"found:", Sj in distinct)
