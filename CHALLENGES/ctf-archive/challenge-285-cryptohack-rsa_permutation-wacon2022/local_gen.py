# Synthetic clone of chal.py: generates instance + true answer for DP testing
import os, sys, random
from Crypto.Util.number import getStrongPrime, inverse, long_to_bytes

def gen(seed=None):
    if seed is not None: random.seed(seed)
    e = 293
    while True:
        p = getStrongPrime(1024)
        q = getStrongPrime(1024)
        if (p-1) % e != 0 and (q-1) % e != 0:
            break
    n = p*q
    d_p = inverse(e, p-1)
    d_q = inverse(e, q-1)
    perm = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']
    random.shuffle(perm)
    def mapped(s, perm):
        return ''.join(perm[int(x,16)] for x in s)
    return dict(n=n, p=p, q=q,
                sp=mapped(long_to_bytes(d_p,128).hex(), perm),
                sq=mapped(long_to_bytes(d_q,128).hex(), perm),
                perm=''.join(perm))

if __name__ == '__main__':
    import json
    inst = gen(int(sys.argv[1]) if len(sys.argv)>1 else 1)
    json.dump({k:str(v) for k,v in inst.items()}, open('local_instance.json','w'))
    print("wrote local_instance.json  n bits:", inst['n'].bit_length())
