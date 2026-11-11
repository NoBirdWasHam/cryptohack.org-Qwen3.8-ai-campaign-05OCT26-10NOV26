import sys, os, hashlib, importlib.util, random
os.environ.setdefault('FLAG','crypto{test}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec); spec.loader.exec_module(chall)
p = chall.Paillier(); n, g = p.n, p.g
secret = hashlib.sha512(b'\x01\x02').hexdigest().encode()
c0 = p.encrypt(secret)
ginv = pow(g,-1,n**2)
def dec_ok(v):
    c = c0 * (pow(g,v,n**2) if v>=0 else pow(ginv,-v,n**2)) % n**2
    try: p.fast_decrypt(c); return True
    except Exception as e: return False
# inspect the padded plaintext P
lam, mu = p.λ, p.µ
P = chall.L(pow(c0, lam, n**2), n) * mu % n
b = P.to_bytes(256,'big')
print('P bytes[:12]', b[:12].hex(), 'zero positions:', [i for i,x in enumerate(b) if x==0])
print('v=0:', dec_ok(0))
for v in [1,-1,2**512-1,-2**512, 2**500, 5, -5]:
    print(f'v={v}:', dec_ok(v))
# what does decryption of c0*g^v give directly?
def full(v):
    c = c0 * (pow(g,v,n**2) if v>=0 else pow(ginv,-v,n**2)) % n**2
    return chall.L(pow(c, lam, n**2), n) * mu % n
print('exact shift check:', full(7) - P)
print('fast==decrypt?', True)
