# Correct comparison-oracle test: c = c0 * g^(n - t) -> m = m0 - t mod n
import os, hashlib, importlib.util, random
os.environ.setdefault('FLAG','crypto{t}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec); spec.loader.exec_module(chall)
random.seed(3)
p = chall.Paillier(); n,g = p.n, p.g
lam,mu = p.λ,p.µ
def decbytes(c):
    X = chall.L(pow(c,lam,n**2),n)*mu % n
    return X.to_bytes(256,'big'), X
FP=TN=TP=FN=0
for _ in range(40):
    s1 = hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode()
    t  = int.from_bytes(hashlib.sha512(random.randrange(65536).to_bytes(2,'big')).hexdigest().encode(),'big')
    c0 = p.encrypt(s1); s = int.from_bytes(s1,'big')
    c = c0*pow(g,n-t,n**2)%n**2
    b,X = decbytes(c)
    # predicted: s>=t -> m0-t clean; else borrow: byte191=ff, P-1, low=~(t-s-1)
    if s>=t:
        pred = True
        TP += (p.fast_decrypt(c) if False else _ok(p,c)); FN += 0
    ok = _ok(p,c) if False else None
print('placeholder')
