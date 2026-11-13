import time, threading, gzip, random, traceback
from fpylll import IntegerMatrix, BKZ, FPLLL
def hb():
    t0=time.time()
    while True:
        time.sleep(30); print("ALIVE", round(time.time()-t0), flush=True)
threading.Thread(target=hb, daemon=True).start()
try:
    print("float_types:", FPLLL.get_flags(), flush=True)
except Exception as e:
    print("flagq err", e, flush=True)
rng = random.Random(7)

# T1: small intrel control
m = 60
A = IntegerMatrix(m, m + 1)
for i in range(m):
    A[i, i] = 1
    A[i, m] = rng.randrange(2**40)
t0 = time.time()
BKZ.reduction(A, BKZ.EasyParam(10))
print("T1_SURVIVED", round(time.time()-t0), flush=True)

# T2: 512-dim intrel control (previous session: BKZ-20 ~42 s OK)
m = 512
Bm = IntegerMatrix(m, m + 1)
for i in range(m):
    Bm[i, i] = 1
    Bm[i, m] = rng.randrange(2**60)
t0 = time.time()
BKZ.reduction(Bm, BKZ.EasyParam(20))
print("T2_SURVIVED", round(time.time()-t0), flush=True)

# T3: real lattice, BKZ-20, short cap -> does it exit clean before ~240 s?
M = IntegerMatrix(1024, 1024)
with gzip.open("M_lll.txt.gz", "rt") as f:
    for i, line in enumerate(f):
        for j, tok in enumerate(line.split()):
            M[i, j] = int(tok)
print("T3 loaded", flush=True)
t0 = time.time()
try:
    BKZ.reduction(M, BKZ.EasyParam(20, max_time=100))
    mn = min(sum(M[i, j] ** 2 for j in range(1024)) for i in range(1024))
    print("T3_SURVIVED", round(time.time()-t0), "min norm2", mn, flush=True)
except BaseException:
    print("T3_PYERR", traceback.format_exc(), flush=True)
print("MATRIX2_DONE", flush=True)
