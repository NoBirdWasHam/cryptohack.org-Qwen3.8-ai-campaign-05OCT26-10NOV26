# Real instance: build G(k,p) lattice mod e, LLL, report short rows.
import re, sys
from fractions import Fraction
from bicop2 import build, rows_unscaled, pmul, ppow
from fpylll import IntegerMatrix, LLL

t = open('output.txt').read()
N = int(re.search(r'N = (0x[0-9a-f]+)', t).group(1), 16)
e = int(re.search(r'e = (0x[0-9a-f]+)', t).group(1), 16)
c = int(re.search(r'c = (0x[0-9a-f]+)', t).group(1), 16)

f = {(1,1): N+1, (1,2): -1, (1,0): -N, (0,1): 1}   # G(x,y)=x(y-1)(N-y)+y, root (k,p) mod e
X, Y = 1<<300, 1<<256

def norm_bits(fr):
    return fr.numerator.bit_length() - max(fr.denominator.bit_length(),1)

def run(m=2, cc=2):
    B, cols = build(f, e, X, Y, m=m, c=cc)
    print(f'config m={m} c={cc}: {B.nrows}x{B.ncols}', flush=True)
    LLL.reduction(B)
    rows = rows_unscaled(B, cols, X, Y)
    # rank rows by max |coeff| size (scaled-norm proxy): compute scaled norm
    out = []
    for ri, row in enumerate(rows):
        s = 0
        for (i,j),v in row.items():
            s += abs(v) * (X**i) * (Y**j)   # sum of scaled coeff magnitudes
        out.append((s, ri))
    out.sort()
    HG = (e**m) // (len(rows)**2)
    print('HG-ish bound bits:', HG.bit_length(), ' e^m bits:', (e**m).bit_length(), flush=True)
    good = []
    for s, ri in out[:8]:
        row = rows[ri]
        maxdeg = max(i+2*j for (i,j),v in row.items() if v)
        print(f'row{ri}: scaled-norm bits {s.bit_length()} vs bound {HG.bit_length()}  '
              f'monomials {sum(1 for v in row.values() if v)}  '
              f'x-deg-range {min(i for (i,j),v in row.items() if v)}..{max(i for (i,j),v in row.items() if v)} '
              f'y-deg {min(j for (i,j),v in row.items() if v)}..{max(j for (i,j),v in row.items() if v)}')
        if s < HG:
            good.append(row)
    print('rows under bound:', len(good), flush=True)
    # dump rows under bound to file for reuse
    import pickle
    with open(f'goodrows_m{m}c{cc}.pkl','wb') as fh:
        pickle.dump(good, fh)
    return good

if __name__ == '__main__':
    run(int(sys.argv[1]) if len(sys.argv)>1 else 2, int(sys.argv[2]) if len(sys.argv)>2 else 2)
