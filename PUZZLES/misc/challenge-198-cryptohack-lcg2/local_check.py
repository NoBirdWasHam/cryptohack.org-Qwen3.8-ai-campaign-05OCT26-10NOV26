import random, itertools
from solve import f, finv, top, recover_first, a, b, mod
ok=0
for trial in range(50):
    # simulate get_a_challenge: blocks v,w,k,i of 16 states each
    def block():
        x=random.getrandbits(48); out=[]
        for _ in range(16):
            x=f(x); out.append(x)
        return out
    v=block(); w=block(); k=block(); i=block()
    pt=bytes(top(v[j]) for j in range(8,16))+bytes(top(w[j]) for j in range(0,8))
    key=bytes(top(w[j]) for j in range(8,16))+bytes(top(k[j]) for j in range(0,8))
    iv=bytes(top(k[j]) for j in range(8,16))+bytes(top(i[j]) for j in range(0,8))
    # key[0:8] = top(w9..w16): recover w1 from top(w1..w8)=pt[8:16], advance 8 then collect 8
    w1=recover_first(list(pt[8:16]),a,b)
    assert w1 is not None, f"trial {trial}: w1 None"
    xs=w1
    for _ in range(8):
        xs=f(xs)            # reach w9
    key0=bytearray()
    for _ in range(8):
        key0.append(top(xs))
        xs=f(xs)
    # key[8:16] = top(k1..k8): recover k9 from top(k9..k16)=iv[0:8], step back 8 (finv+insert)
    k9=recover_first(list(iv[0:8]),a,b)
    assert k9 is not None, f"trial {trial}: k9 None"
    key8=bytearray(); xs=k9
    for _ in range(8):
        xs=finv(xs); key8.insert(0,top(xs))
    reckey=bytes(key0)+bytes(key8)
    if reckey!=key:
        print(f"FAIL {trial}\n rec ={reckey.hex()}\n true={key.hex()}")
        print(" pt=",pt.hex()); print(" iv=",iv.hex())
        break
    ok+=1
print(f"recovered key {ok}/50")
