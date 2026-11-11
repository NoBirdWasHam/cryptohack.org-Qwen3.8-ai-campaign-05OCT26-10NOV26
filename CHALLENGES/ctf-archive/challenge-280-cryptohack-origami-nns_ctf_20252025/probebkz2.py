import sys, time, threading, gzip, traceback
from fpylll import IntegerMatrix, BKZ
d = 1024
ERR = []
def hb():
    t0 = time.time()
    while True:
        time.sleep(60)
        print("ALIVE", round(time.time() - t0), flush=True)
threading.Thread(target=hb, daemon=True).start()
def guarded():
    try:
        t0 = time.time()
        M = IntegerMatrix(d, d)
        with gzip.open("M_lll.txt.gz", "rt") as f:
            for i, line in enumerate(f):
                for j, tok in enumerate(line.split()):
                    M[i, j] = int(tok)
        print("loaded", round(time.time() - t0), flush=True)
        for ft, prec, cap in (("mpfr", 200, 400), ("dpe", 0, 400)):
            try:
                t1 = time.time()
                if ft == "dpe":
                    BKZ.reduction(M, BKZ.EasyParam(20, max_time=cap), float_type="dpe")
                else:
                    BKZ.reduction(M, BKZ.EasyParam(20, max_time=cap), float_type="mpfr", precision=prec)
                mn = min(sum(M[i, j] ** 2 for j in range(d)) for i in range(d))
                print(ft.upper(), "SURVIVED", round(time.time() - t1), "min norm2", mn, flush=True)
            except BaseException as e:
                print(ft.upper(), "PYERR", type(e).__name__, str(e)[:200], flush=True)
                print(traceback.format_exc()[-400:], flush=True)
        print("PROBE2_DONE", flush=True)
    except BaseException:
        ERR.append(1)
        print(traceback.format_exc(), flush=True)
threading.stack_size(3 << 26)
th = threading.Thread(target=guarded)
th.start()
th.join()
sys.exit(1 if ERR else 0)
