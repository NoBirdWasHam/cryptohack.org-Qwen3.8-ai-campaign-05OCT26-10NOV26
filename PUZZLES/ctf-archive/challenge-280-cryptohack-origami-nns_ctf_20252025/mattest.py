import time, threading, gzip
from fpylll import IntegerMatrix, BKZ
def hb():
    t0=time.time()
    while True:
        time.sleep(30); print("ALIVE", round(time.time()-t0), flush=True)
threading.Thread(target=hb, daemon=True).start()
print("A start", flush=True)
A = IntegerMatrix(200, 200); A.randomize("intrel", bits=40)
t0=time.time()
BKZ.reduction(A, BKZ.EasyParam(10, max_time=25))
print("A_SURVIVED", round(time.time()-t0), flush=True)
print("B start", flush=True)
M = IntegerMatrix(1024, 1024)
with gzip.open("M_lll.txt.gz","rt") as f:
    for i, line in enumerate(f):
        for j, tok in enumerate(line.split()):
            M[i, j] = int(tok)
t0=time.time()
BKZ.reduction(M, BKZ.EasyParam(10, max_time=150))
print("B_SURVIVED", round(time.time()-t0), flush=True)
print("MATRIX_DONE", flush=True)
