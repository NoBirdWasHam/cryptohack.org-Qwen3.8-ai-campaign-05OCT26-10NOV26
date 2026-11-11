# Diagnostic/pivot probe: BKZ-20 from M_lll checkpoint with explicit float_type and
# verbose BKZ logging. Usage: probebkz.py [float_type] [blocksize]
import sys, time, threading, gzip, traceback
from fpylll import IntegerMatrix, BKZ, FPLLL
d = 1024
ft = sys.argv[1] if len(sys.argv) > 1 else "d"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 20
try:
    FPLLL.set_verbose("bkz", "info")
except Exception as e:
    print("verbose set failed:", e, flush=True)
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
        p = BKZ.EasyParam(k, max_time=240)
        print("starting BKZ", k, "float", ft, flush=True)
        BKZ.reduction(M, p, float_type=(None if ft == "auto" else ft))
        mn = min(sum(M[i, j] ** 2 for j in range(d)) for i in range(d))
        print("SURVIVED min norm2", mn, flush=True)
    except BaseException:
        ERR.append(1)
        print(traceback.format_exc(), flush=True)
threading.stack_size(3 << 26)
th = threading.Thread(target=guarded)
th.start()
th.join()
sys.exit(1 if ERR else 0)
