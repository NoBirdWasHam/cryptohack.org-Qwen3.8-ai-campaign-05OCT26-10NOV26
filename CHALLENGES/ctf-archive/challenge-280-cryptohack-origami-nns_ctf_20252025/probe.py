import time
t0=time.time()
from fpylll import IntegerMatrix, BKZ
print("import ok", time.time()-t0, flush=True)
M = IntegerMatrix(64,64)
for i in range(64): M[i,i]=1
t0=time.time(); BKZ.reduction(M, BKZ.EasyParam(20)); print("bkz tiny ok", time.time()-t0, flush=True)
