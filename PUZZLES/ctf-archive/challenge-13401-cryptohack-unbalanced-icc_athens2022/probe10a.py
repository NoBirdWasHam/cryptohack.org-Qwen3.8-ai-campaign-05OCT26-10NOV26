import sys; sys.path.insert(0,".")
import gmpy2
# micro-test of extraction math via dng4.attack internals: replicate res_var + gcd_mod here
def res_var(H1, H2, keep):
    idx = 1 if keep == 'x' else 0
    oth = 1 - idx
    def coeffs(H, dv):
        d = {}
        for (ax, ay), v in H.items():
            if (ax, ay)[idx] == dv:
                d[(ax, ay)[oth]] = d.get((ax, ay)[oth], 0) + v
        return {k: v for k, v in d.items() if v}
    d1 = max((t[idx] for t in H1), default=0); d2 = max((t[idx] for t in H2), default=0)
    if d1 + d2 == 0: return None
    n = d1 + d2
    c1 = [coeffs(H1, i) for i in range(d1 + 1)]
    c2 = [coeffs(H2, i) for i in range(d2 + 1)]
    rows = []
    for i in range(d2):
        row = [{} for _ in range(n)]
        for j in range(d1 + 1): row[i + j] = dict(c1[j])
        rows.append(row)
    for i in range(d1):
        row = [{} for _ in range(n)]
        for j in range(d2 + 1): row[i + j] = dict(c2[j])
        rows.append(row)
    from probe9 import sylv_det_generic  # not in probe9; inline instead
