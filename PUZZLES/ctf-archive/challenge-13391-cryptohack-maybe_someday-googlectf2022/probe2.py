import os, hashlib, importlib.util, random
os.environ.setdefault('FLAG','crypto{test}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec); spec.loader.exec_module(chall)
random.seed(7)
p = chall.Paillier(); n, g = p.n, p.g
ginv = pow(g,-1,n**2)
def dec_ok(c):
    try: p.fast_decrypt(c); return True
    except Exception: return False
A=B0=B1=0
N=60
for _ in range(N):
    s1 = hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode()
    s2 = hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode()
    c0 = p.encrypt(s1)
    m1 = int.from_bytes(s1,'big'); t = int.from_bytes(s2,'big')
    if m1==t: continue
    c = c0 * (pow(g,-t,n**2) if t>=0 else pow(ginv,t,n**2)) % n**2
    # v = -t -> use g^{-t}
    c = c0 * pow(ginv, t, n**2) % n**2
    ok = dec_ok(c)
    if m1>=t: A += ok
    else:
        B1+=1; B0 += ok
print(f'msg>=t: 😀 {A}   msg<t: n={B1} 😀 {B0} 😡 {B1-B0}')
