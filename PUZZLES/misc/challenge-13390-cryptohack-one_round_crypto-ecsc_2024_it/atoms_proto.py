#!/usr/bin/env python3
"""Recover the 16 byte-subspaces S_j = M3^{-T}(B_j) from nullspaces W_i of
byte-difference datasets, as atoms of the intersection lattice. Then fit
sigma^-1 per byte (k_j and basis labeling) via Fourier tables psi.
Part 1 here: W_i bases + atoms (dim-8 intersections)."""
import random
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
    return list(piv.values())

def intersect(b1,b2):
    # intersect spans of two basis lists: vectors u in span(b1) orthogonal to ... use: u in span(b1) and <u, r>=0 all r in b2-perp?
    # u in span(b1) ∩ span(b2)  <=> u=sum a_i b1_i and orthogonal to (span(b2))^perp
    # build: rows b1 ; constraints: u·c=0 for c in basis of perp(b2): solve via RREF of dual... simpler known trick:
    # span(b1) ∩ span(b2): u in span(b1) iff u·y=0 for y in N1 (nullspace of b1 as rows... )
    # do: u in span(b1): param; impose u·z=0 for all z in nullrows(b2-rows)... but we have bases as ROWS of vector space.
    # use: dim(V∩W)=dim V + dim W - dim(V+W); membership: u in span(S) via rref reduce.
    # compute basis of intersection: for each u in b1 basis ... standard: collect {b1} rows; find combos giving...
    # brute-force approach for dims<=64: parametrize span(b1) and impose orthogonality to nullspace(b2).
    N2=nullspace_basis(b2)
    # unknown coeffs a (len b1): u=Σa_i b1_i; constraints u·N2_j=0 → linear system on a
    rows=[]
    for n in N2:
        rows.append([ (b1[i]>>? ) for i in range(len(b1))]) if False else None
    # implement properly below
    raise NotImplementedError

def nullspace_basis(vecs):
    # basis of u with <u,v>=0 for all v in vecs (vecs as list of ints)
    piv={}
    for v in vecs:
        x=v
        while x:
            b=x.bit_length()-1
            if b in piv: x^=piv[b]
            else: piv[b]=x; break
    free=[b for b in range(128) if b not in piv]
    # RREF pivots
    piv2=dict(piv)
    for b in sorted(piv2):
        for b2 in sorted(piv2):
            if b!=b2 and (piv2[b2]>>b)&1: piv2[b2]^=piv2[b]
    ns=[]
    for f in free:
        u=1<<f
        for b,r in piv2.items():
            if (r>>f)&1: u^=(1<<b)
        ns.append(u)
    return ns

def span_reduce(vecs):
    return rref(vecs)

def in_span(u, basis):
    x=u
    red={}
    for b in basis:
        t=b
        bb=t.bit_length()-1
        if bb not in red: red[bb]=t
        else: t^=red[bb]
    # do proper rref once
    red=rref(basis)
    piv={v.bit_length()-1:v for v in red}
    x=u
    while x:
        b=x.bit_length()-1
        if b not in piv: return False
        x^=piv[b]
    return True

def inter(basisA, basisB):
    # basisA rows; find u in span(basisA) with <u, n>=0 for n in nullspace(basisB)
    N=nullspace_basis(basisB)
    bA=basisA
    # solve: coeffs a over bA: constraints Σ a_i (bA_i · n) = 0
    # build matrix: cols = bA_i dots n
    rows=[]
    for n in N:
        rows.append([ bin(bA_i & n).count('1')&1 for bA_i in bA ])
    # nullspace of rows over GF2: coeffs a with Σ a_i rows[j][i] = 0
    m=len(bA)
    coeffs=[1<<i for i in range(m)]
    piv={}
    for r,row in enumerate(rows):
        x=0
        for i,bit in enumerate(row):
            if bit: x|=1<<i
        while x:
            b=x.bit_length()-1
            if b in piv: x^=piv[b][0]
            else: piv[b]=(x,r); break
    ns=[]
    red={b:piv[b][0] for b in piv}
    for b in sorted(red):
        for b2 in sorted(red):
            if b!=b2 and (red[b2]>>b)&1: red[b2]^=red[b]
    for f in range(m):
        if f not in red:
            a=1<<f
            for b,r in red.items():
                if (r>>f)&1: a^=1<<b
            u=0
            for i in range(m):
                if (a>>i)&1: u^=bA[i]
            ns.append(u)
    return rref(ns)

if __name__=="__main__":
    import time
    rng=random.Random(11)
    sess=Session()
    # datasets: delta=1, all i
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
    print("nullities",[len(w) for w in Ws],"time",time.time()-t0)
    # find dim-8 intersections via greedy refinement
    import itertools
    found={}
    cand=[([],Ws[0][:])]
    # brute: all subsets of size up to 5
    seen=set()
    atoms=set()
    t0=time.time()
    for size in range(1,7):
        for comb in itertools.combinations(range(16),size):
            cur=None
            for idx in comb:
                cur=Ws[idx] if cur is None else inter(cur,Ws[idx])
                if len(cur)<8: break
            if len(cur)==8:
                key=frozenset(frozenset(x) for x in [tuple(v.to_bytes(16,'big')) for v in rref(cur)])
                atoms.add(key)
        print("size",size,"atoms so far",len(atoms),t0-time.time())
        if len(atoms)>=16: break
    print("distinct dim-8 atoms:",len(atoms))
