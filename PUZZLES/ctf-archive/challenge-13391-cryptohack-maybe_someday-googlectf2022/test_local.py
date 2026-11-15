# Local validation of the comparison-oracle attack against in-process chall.py logic
import sys, os, random, hashlib, importlib.util
os.environ.setdefault('FLAG','crypto{test}')
spec = importlib.util.spec_from_file_location('chall', os.path.join(os.path.dirname(__file__),'chall.py'))
chall = importlib.util.module_from_spec(spec)
spec.loader.exec_module.__self__ if False else spec.loader.exec_module(chall)

# table of candidate secrets
SECRETS = sorted(hashlib.sha512(i.to_bytes(2,'big')).hexdigest().encode() for i in range(65536))

def run_round(p):
    secret = os.urandom(2)
    secret = hashlib.sha512(secret).hexdigest().encode()
    c0 = p.encrypt(secret)
    msg = int.from_bytes(secret,'big')
    n, g = p.n, p.g
    # sanity: exactness of the validity window for random seeds
    ok = True
    # binary search over sorted candidate msg list (16 queries)
    vals = [int.from_bytes(s,'big') for s in SECRETS]
    lo, hi = 0, 65535  # answer index within [lo, hi]
    ginv = pow(g, -1, p.n**2)
    def shift(c0, v):
        return c0 * (pow(g, v, p.n**2) if v>=0 else pow(ginv, -v, p.n**2)) % p.n**2
    while hi - lo > 1:
        mid = (lo+hi)//2
        v = -vals[mid]
        c = shift(c0, v)   # r=1: homomorphic shift
        try:
            p.fast_decrypt(c); res = True   # 😀  <=> msg >= vals[mid]
        except Exception:
            res = False
        expect = (msg >= vals[mid])
        if res != expect:
            ok = False
        if res: lo = mid
        else: hi = mid
    if hi - lo == 1 and lo != 0 or True:
        # disambiguate boundary (msg may equal vals[hi])
        try:
            p.fast_decrypt(shift(c0, -vals[hi])); ans = hi if msg >= vals[hi] else lo
        except Exception:
            ans = lo
    guess = SECRETS[ans]
    return guess == secret, ok

random.seed(1234)
p = chall.Paillier()
for trial in range(5):
    win, exact = run_round(p)
    print(f'trial {trial}: win={win} oracle_exact={exact}')
