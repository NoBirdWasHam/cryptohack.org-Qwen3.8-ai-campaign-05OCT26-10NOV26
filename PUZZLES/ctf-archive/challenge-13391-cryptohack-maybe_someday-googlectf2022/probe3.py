import os, hashlib, importlib.util, random
os.environ.setdefault('FLAG','crypto{test}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec); spec.loader.exec_module(chall)
random.seed(7)
p = chall.Paillier(); n, g = p.n, p.g
ginv = pow(g,-1,n**2)
lam, mu = p.λ, p.µ
def decbytes(v):
    c = p_enc * pow(g, v, n**2) % n**2 if v>=0 else p_enc * pow(ginv, -v, n**2) % n**2
    X = chall.L(pow(c, lam, n**2), n) * mu % n
    return X.to_bytes(256,'big'), X
random.seed(11)
for trial in range(3):
    s1 = hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode()
    s2 = hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode()
    p_enc = p.encrypt(s1)
    m1 = int.from_bytes(s1,'big'); t = int.from_bytes(s2,'big')
    b, X = decbytes(-t)
    zp = [i for i,x in enumerate(b) if x==0]
    print(f'msg{">=" if m1>=t else "<"}t  zeros@{zp[:5]} first_zero_idx={zp[0] if zp else None}')
    print('  b[0:4]:', b[:4].hex(), ' b[189:196]:', b[189:196].hex(), ' last16:', b[-16:].hex())
