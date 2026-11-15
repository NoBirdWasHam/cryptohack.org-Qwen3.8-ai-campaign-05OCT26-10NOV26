import random, sys, time
from gmpy2 import is_prime
sys.path.insert(0, '.')
random.seed(42)
# mirror chall.py's draws exactly
g_true = random.getrandbits(256)
while True:
    p_true = random.getrandbits(256)
    if is_prime(p_true):
        break
print("p_true bits", p_true.bit_length())
t0 = time.time()
from solve import find_collision, PREF, TARGET, M
X = None
for L in (64, 62, 66):
    X = find_collision(p_true, L)
    if X:
        print("found X at L=%d in %.0fs" % (L, time.time() - t0)); break
assert X is not None
m = int.from_bytes(PREF + X, 'big')
assert pow(g_true, m, p_true) == pow(g_true, M, p_true)
print("offline collision OK, X len", len(X))
inputs = ['l', 'n', 'm', 'o', X.decode()]
out = []
g = {'__name__': '__main__', 'input': lambda *a: inputs.pop(0),
     'print': lambda *a, **k: out.append(' '.join(map(str, a)))}
import os
os.environ['FLAG'] = 'firebird{local_test_flag}'
try:
    exec(compile(open('chall.py').read(), 'chall.py', 'exec'), g)
except SystemExit:
    pass
print("LAST LINES:", out[-2:])
