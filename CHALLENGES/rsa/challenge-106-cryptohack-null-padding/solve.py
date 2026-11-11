#!/usr/bin/env python
# null_padding (106): FLAG=43B, m = FLAG + 57x0x00 = 100B, e=3, 1024-bit n.
# m = flag << 456  =>  m^3 = flag^3 * 2^1368.  c = m^3 mod n.
# C = c*(2^1368)^-1 mod n = flag^3 mod n.  flag^3 ~1032 bits, n~1024 => flag^3 = C + k*n, k<256.
# Brute-force k: C + k*n perfect cube => flag.
import gmpy2
src=open('output_provided.txt').read()
n=int(src.split('n = ')[1].split()[0])
c=int(src.split('c = ')[1].split()[0])
pad=57; low=8*pad
C=(c*pow(pow(2,3*low,n),-1,n))%n
for k in range(0,512):
    X=C+k*n
    r,exact=gmpy2.iroot(X,3)
    if exact:
        b=r.to_bytes((r.bit_length()+7)//8,'big')
        try: s=b.decode()
        except: continue
        if 'crypto{' in s:
            # verify
            m=r<<low
            assert pow(m,3,n)==c
            print("FLAG:",s)
            break
