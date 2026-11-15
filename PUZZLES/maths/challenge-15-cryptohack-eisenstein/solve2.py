# eisenstein (97): h = sum ord(c_i)*sqrt(p_i), ct = floor(h*2^256).
# Recover 15 unknown chars via CVP: Kannan embedding, fpylll LLL.
# Scaling S=2^264 so the interval width (2^-256*S = 16) and v-rounding noise
# (~sqrt(15)*0.5*80 ~ 155) are both << |z| ~ 310; D' ~ 2^85 ~ expected norm.
import gmpy2, ast, re
from gmpy2 import mpfr, get_context
get_context().precision = 600
from fpylll import IntegerMatrix
from fpylll.fplll.lll import lll_reduction
from fpylll.fplll.bkz import bkz_reduction
from fpylll.fplll.bkz_param import BKZParam

src = open('real_eisenstein_provided.py').read()
ct = int(re.search(r'ciphertext: (\d+)', src).group(1))
PRIMES = ast.literal_eval(re.search(r'PRIMES = (\[.+\])', src).group(1))
FLAG0 = re.search(r'FLAG = "(.+?)"', src).group(1)
L = len(FLAG0); PRIMES = PRIMES[:L]
sqrt_p = [mpfr(gmpy2.sqrt(mpfr(p))) for p in PRIMES]
known = {i: ord(c) for i, c in enumerate(FLAG0) if c != '?'}
unk = [i for i in range(L) if FLAG0[i] == '?']
m = len(unk)
h_known = sum(mpfr(known[i]) * sqrt_p[i] for i in known)
T0 = mpfr(ct) / mpfr(2)**256 - h_known          # target interval [T0, T0+2^-256)
S = 2**264
v = [int(round(sqrt_p[unk[j]] * S)) for j in range(m)]
w = int((T0 + mpfr(2)**-257) * S)               # interval centre
Dp = 2**85

rows = []
for j in range(m):
    r = [0] * (m + 2); r[j] = 1; r[m] = v[j]; rows.append(r)
r = [0] * (m + 2); r[m] = w; r[m + 1] = Dp; rows.append(r)
M = IntegerMatrix.from_iterable(m + 1, m + 2, [x for row in rows for x in row])

def recon(zz):
    h2 = h_known + sum(mpfr(zz[j]) * sqrt_p[unk[j]] for j in range(m))
    return int(h2 * mpfr(2)**256) == ct
def in_box(zz):
    return all(32 <= x <= 126 for x in zz)

for tag, red in (("LLL", lll_reduction(M)), ("BKZ14", bkz_reduction(IntegerMatrix(M), BKZParam(14)))):
    hit = None
    for i in range(red.nrows):
        row = [red[i, j] for j in range(m + 2)]
        if abs(row[m + 1]) != Dp:
            continue
        sgn = 1 if row[m + 1] < 0 else -1
        z = [sgn * row[j] for j in range(m)]
        if in_box(z) and recon(z):
            hit = z; break
    print(tag, "->", hit)
    if hit:
        out = list(FLAG0)
        for j, i in enumerate(unk):
            out[i] = chr(hit[j])
        print("FLAG:", "".join(out))
        break
