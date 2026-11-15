import os, hashlib, importlib.util
os.environ.setdefault('FLAG','crypto{t}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec); spec.loader.exec_module(chall)
p = chall.Paillier(); n,g = p.n,p.g
sec = hashlib.sha512(b'\x01\x02').hexdigest().encode()
c0 = p.encrypt(sec)
print('decrypt roundtrip:', p.decrypt(c0) == sec, ' fast:', p.fast_decrypt(c0)==sec)
lam, mu = p.λ, p.µ
P = chall.L(pow(c0, lam, n**2), n) * mu % n
b = P.to_bytes(256,'big')
print('P hex head:', b[:4].hex(), 'tail:', b[-8:].hex())
print('sec in tail?', b[-64:] == sec, ' zero idx:', [i for i,x in enumerate(b) if x==0][:6])
# what does encrypt's padded integer look like?
pad = p.pad(sec); m0 = int.from_bytes(pad,'big')
print('padded int == P?', m0 == P, ' pad zeros:', [i for i,x in enumerate(pad) if x==0])
