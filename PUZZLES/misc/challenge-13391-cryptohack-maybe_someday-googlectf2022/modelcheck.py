# Verify predicate model r vs REAL fast_decrypt on real padded/encrypted messages.
# Model: K=0: ge|h ; K=255: ~ge|h ; mid: h  where ge=[S>=t], h=haszero((S-t) mod 2^512)
import hashlib, random, sys
sys.path.insert(0, '.')
from chall import Paillier

M = 1 << 512
def haszero(x): return 0 in x.to_bytes(64, 'big')

p = Paillier()
n = p.n
n2 = n * n
random.seed(1234)
bad = 0
N = 800
for trial in range(N):
    seed = random.randrange(65536)
    secret = hashlib.sha512(seed.to_bytes(2, 'big')).hexdigest().encode()
    c0 = p.encrypt(secret)
    S = int.from_bytes(secret, 'big')
    for _ in range(3):
        K = random.choice([0, 255] + [random.randrange(1, 255)] if trial % 2 else [0, 255])
        t = random.randrange(M) if trial % 3 == 0 else random.choice([S, S+1, (S + random.randrange(2**40)) % M])
        delta = K * M + t
        c = c0 * pow(pow(g_ := p.g, delta, n2), -1, n2) % n2
        try:
            p.fast_decrypt(c); got = 1
        except Exception:
            got = 0
        ge = S >= t
        h = haszero((S - t) % M)
        want = (ge or h) if K == 0 else ((not ge) or h) if K == 255 else h
        if got != int(want):
            bad += 1
            print('MISMATCH K', K, 'S>=t', ge, 'h', h, 'got', got)
print('checked', N*3, 'bad', bad)
