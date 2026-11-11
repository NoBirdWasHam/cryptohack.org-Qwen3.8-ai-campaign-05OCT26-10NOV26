#!/usr/bin/env python3
from local_oracle import *
def fr(b): return int.from_bytes(b,'big')
def bs(v): return v.to_bytes(16,'big')

for ki in range(4):
    sess = Session(key=bytes([ki])*16)
    M1 = lin_matrix(lambda v: fr(mix(v.to_bytes(16,'big'), sess.k1)))
    cnt={}
    for b in range(128):
        n=sum(1 for x in bs(M1[b]) if x)
        cnt[n]=cnt.get(n,0)+1
    # byte adjacency matrix A[j][b] = byte j of M1*e_b nonzero? 16x16 counts
    print("key",ki,"col support dist:",cnt)
# check F alone
def Fmap(v):
    m = v.to_bytes(16,'big')
    return fr(xor(m, xor(rotr(m,7,16), rotr(m,9,16))))
F = lin_matrix(Fmap)
cnt={}
for b in range(128):
    n=sum(1 for x in bs(F[b]) if x)
    cnt[n]=cnt.get(n,0)+1
print("F alone col support dist:",cnt)

# where do shifts come from? print first key's shift sequence
import random
sess = Session(key=b'\x00'*16)
random.seed(sess.k1)
seq=[random.randint(1,32) for _ in range(12*8)]
print("shifts key0:", seq)
