import re, math

txt = open(r"~/AppData/Local/hermes/cache/scratch/unbal/output.txt").read()
e = int(re.search(r"e = (0x[0-9a-f]+)", txt).group(1), 16)
N = int(re.search(r"N = (0x[0-9a-f]+)", txt).group(1), 16)

def optimize(logE, xu, yv, loss_per_dim, fixed_slack, verbose=False):
    """Region: a in {0,1} (linear in k). R = {(0,j):0<=j<=m} P-rows -> lead kp^(j+2).
       box: a=0: b in [0, m+2] (e-rows), a=1: b in {0,1} (e-rows), b in [2, m+2] via P-rows."""
    best = None
    for m in range(1, 400):
        B = m + 2
        D = 2 * (B + 1)
        logdet = 0.0
        # P rows (a=1, b=j+2): diagonal X^1 Y^(j+2)
        for j in range(m + 1):
            logdet += xu + yv * (j + 2)
        # e rows a=0, b=0..B
        for b in range(B + 1):
            logdet += logE + yv * b
        # e rows a=1, b=0,1
        logdet += (logE + xu) + (logE + xu + yv)
        margin = logE - logdet / D - loss_per_dim * D - fixed_slack
        if best is None or margin > best[1]:
            best = (m, margin, D)
        if verbose and m in (5, 10, 20, 30, 40, 60, 80, 120):
            print(f"m={m:4d} D={D:4d} margin={margin:8.1f}")
    return best

# real parameters: e bitlog
logE = math.log2(e)
xu, yv = 300, 256          # k < 2^300, p < 2^256
print("real: m*, margin*, D* =", optimize(logE, xu, yv, 0.0195, 20.0, verbose=True))
# also LLL-only worst case 1.02^D
print("LLL-worst(1.02^D): m* =", optimize(logE, xu, yv, 0.0286, 20.0))
# selftest params
print("selftest: m* =", optimize(255.0, 76, 65, 0.0195, 20.0, verbose=True))
