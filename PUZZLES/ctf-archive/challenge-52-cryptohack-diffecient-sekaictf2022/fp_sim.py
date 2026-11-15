# Local sim: build DB like server, measure false-positive rate + FP-search speed
import random, time, math, mmh3, re, string
random.seed(42)
M, K, SEC = 2**32-5, 47, 768
def security(i):
    fp = pow(1 - pow(math.e, -K*i/M), K)
    try: return int(1/fp).bit_length()
    except: return float('inf')
dig = set(); i = 0
while security(i) > SEC: i += 1
for _ in range(i):
    pass
# rebuild digests properly
dig = set()
for _ in range(i):
    for s in range(K): dig.add(mmh3.hash(bytes([random.randint(0,255) for _ in range(256)]), s) % M)
fp = pow(1 - pow(math.e, -K*i/M), K)
print('keys:', i, 'digests:', len(dig), 'sec:', security(i), 'fp ~ 1/%.3g' % (1/fp))
AL = (string.ascii_letters+string.digits+'!@#$%^&*()-_=+').encode()
ok = re.compile(rb'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)')
def check(key):
    for s in range(K):
        if mmh3.hash(key, s) % M not in dig: return False
    return True
N = 3000000; t0 = time.time()
for n in range(N):
    key = bytes(random.choice(AL) for _ in range(32))
    if not ok.match(key): continue
    if check(key):
        print('FP FOUND after', n+1, key); break
else:
    print('no fp in', N)
el = time.time()-t0
print('tested %d in %.1fs (%.0f/s), fp=%.3e, expected tries %.3e' % (n+1, el, (n+1)/el, pow(len(dig)/M,K), 1/pow(len(dig)/M,K)))
