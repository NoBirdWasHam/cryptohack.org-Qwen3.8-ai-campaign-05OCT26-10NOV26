# Verify CORRECTED model: secret=128 hex chars, sep byte127, t<2^1024, h over 128 bytes.
import hashlib, random, sys
sys.path.insert(0, '.')
from chall import Paillier
M = 1 << 1024
def haszero(x): return 0 in x.to_bytes(128, 'big')
p = Paillier(); n = p.n; n2 = n*n
random.seed(1234)
bad = 0; tot = 0
for trial in range(80):
    seed = random.randrange(65536)
    secret = hashlib.sha512(seed.to_bytes(2,'big')).hexdigest().encode()
    c0 = p.encrypt(secret); S = int.from_bytes(secret,'big')
    for _ in range(3):
        K = random.choice([0, 255, random.randrange(1,255)])
        t = random.choice([random.randrange(M), S, S+1, (S + random.randrange(2**80)) % M, M-1, 0])
        delta = K*M + t
        c = c0 * pow(pow(p.g, delta, n2), -1, n2) % n2
        try:
            p.fast_decrypt(c); got = 1
        except Exception:
            got = 0
        ge = S >= t
        h = haszero((S - t) % M)
        want = (ge or h) if K == 0 else ((not ge) or h) if K == 255 else h
        want = int(want)
        tot += 1
        if got != want:
            bad += 1
            print('MISMATCH K',K,'ge',ge,'h',h,'got',got,'(got>want = P_last==1 noise):', got>want)
print('checked',tot,'bad',bad)
