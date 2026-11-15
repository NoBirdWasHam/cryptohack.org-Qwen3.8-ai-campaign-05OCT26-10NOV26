# Resultant over Z[y] for polynomials given as {(xdeg, ydeg): coeff}, via Sylvester + Bareiss.
def resultant_x(h1, h2):
    def coeffs(h, dx):
        d = {}
        for (a, b), v in h.items():
            if a == dx: d[b] = v
        return d
    d1 = max((a for a, b in h1), default=0); d2 = max((a for a, b in h2), default=0)
    if d1 + d2 == 0:
        return {}
    n = d1 + d2
    c1 = [coeffs(h1, i) for i in range(d1+1)]
    c2 = [coeffs(h2, i) for i in range(d2+1)]
    def pmul(p, q):
        r = {}
        for k1, v1 in p.items():
            for k2, v2 in q.items():
                r[k1+k2] = r.get(k1+k2, 0) + v1*v2
        return {k: v for k, v in r.items() if v}
    def psub(p, q):
        r = {k: v for k, v in p.items()}
        for k, v in q.items():
            r[k] = r.get(k, 0) - v
        return {k: v for k, v in r.items() if v}
    def pdiv(p, q):
        if not p: return {}
        q = dict(q)
        dn = max(q)
        res = {}
        r = dict(p)
        while r and max(r) >= dn:
            hn, hd = max(r), dn
            co = r[hn] // q[hd]
            sh = hn - hd
            res[sh] = res.get(sh, 0) + co
            for kd, vd in q.items():
                r[kd+sh] = r.get(kd+sh, 0) - co*vd
            r = {k2: v2 for k2, v2 in r.items() if v2}
        if r:
            raise ZeroDivisionError("non-exact division")
        return res
    rows = []
    for i in range(d2):
        row = [{}]*n
        for j in range(d1+1):
            row[i+j] = dict(c1[j])
        rows.append(row)
    for i in range(d1):
        row = [{}]*n
        for j in range(d2+1):
            row[i+j] = dict(c2[j])
        rows.append(row)
    A = rows
    sign = 1
    prev = {0: 1}
    for k in range(n-1):
        piv = None
        for rr in range(k, n):
            if A[rr][k]:
                piv = rr; break
        if piv is None:
            return {}
        if piv != k:
            A[k], A[piv] = A[piv], A[k]; sign = -sign
        p = A[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                num = psub(pmul(A[i][j], p), pmul(A[i][k], A[k][j]))
                if prev != {0: 1}:
                    num = pdiv(num, prev)
                A[i][j] = num
        prev = p
    det = A[n-1][n-1]
    if sign < 0:
        det = {k: -v for k, v in det.items()}
    return det
