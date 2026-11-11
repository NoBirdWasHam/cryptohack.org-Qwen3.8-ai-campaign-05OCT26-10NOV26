# Honest-flags BKZ probe on the real lattice: does the min row norm2 move off 16129?
import sys, time, threading, gzip, traceback
from fpylll import IntegerMatrix, BKZ
d = 1024
def log(*a): print(round(time.time()-T0, 1), *a, flush=True)
T0 = time.time()
def hb():
    while True:
        time.sleep(60); log("ALIVE")
threading.Thread(target=hb, daemon=True).start()
def minrow(M):
    return min(sum(M[i, j]**2 for j in range(d)) for i in range(d))
ERR = []
def guarded():
    try:
        M = IntegerMatrix(d, d)
        with gzip.open("M_lll.txt.gz", "rt") as f:
            for i, line in enumerate(f):
                for j, tok in enumerate(line.split()):
                    M[i, j] = int(tok)
        log("loaded; min row norm2", minrow(M))
        for ft, prec, cap in (("ld", 0, 240), ("mpfr", 300, 240)):
            try:
                t1 = time.time()
                if ft == "ld":
                    BKZ.reduction(M, BKZ.EasyParam(20, max_time=cap, flags=BKZ.AUTO_ABORT),
                                  float_type="ld")
                else:
                    BKZ.reduction(M, BKZ.EasyParam(20, max_time=cap, flags=BKZ.AUTO_ABORT),
                                  float_type="mpfr", precision=prec)
                log(ft.upper(), "SURVIVED", round(time.time()-t1, 1),
                    "min row norm2", minrow(M), flush=True)
                with gzip.open("M_honest_%s.txt.gz" % ft, "wt") as f:
                    for i in range(d):
                        f.write(" ".join(str(M[i, j]) for j in range(d)) + "\n")
                log("checkpointed", ft)
            except BaseException:
                log(ft.upper(), "PYERR")
                print(traceback.format_exc()[-500:], flush=True)
        log("PROBE12 DONE")
    except BaseException:
        ERR.append(1)
        print(traceback.format_exc()[-500:], flush=True)
threading.stack_size(3 << 26)
th = threading.Thread(target=guarded)
th.start(); th.join()
sys.exit(1 if ERR else 0)
