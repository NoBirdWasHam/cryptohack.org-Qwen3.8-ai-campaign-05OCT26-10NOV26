import sys
P = 17585255163044402023
def set_p(p):
    global P
    P = p

def rref(A, b):
    # solve A x = b over GF(P), A: n x 16
    n = len(A); m = len(A[0])
    M = [row[:] + [bb] for row, bb in zip(A, b)]
    piv = []
    r = 0
    for c in range(m):
        pr = None
        for i in range(r, n):
            if M[i][c] % P:
                pr = i; break
        if pr is None:
            continue
        M[r], M[pr] = M[pr], M[r]
        inv = pow(M[r][c], P-2, P)
        M[r] = [x*inv % P for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] % P:
                fct = M[i][c]
                M[i] = [(M[i][j] - fct*M[r][j]) % P for j in range(m+1)]
        piv.append(c); r += 1
        if r == n:
            break
    # check consistency
    for i in range(r, n):
        if M[i][m] % P and all(x % P == 0 for x in M[i][:m]):
            return None
    # particular solution (free vars = 0)
    x = [0]*m
    for i, c in enumerate(piv):
        x[c] = M[i][m] % P
    # nullspace basis
    basis = []
    freec = [c for c in range(m) if c not in piv]
    for fc in freec:
        vec = [0]*m; vec[fc] = 1
        for i, c in enumerate(piv):
            vec[c] = (-M[i][fc]) % P
        basis.append(vec)
    return x, basis

def solve_f_from_samples(samples):
    # samples: list of (u monic coeffs low->high deg7, v coeffs)
    A = []; b = []
    for u, v in samples:
        # f ≡ v^2 (mod u)  <=>  f = q*u + r; rows: x^k = u * (x^{k-7}) + (coeff relation)
        # f_j unknowns j=0..15. Equation f - r = q*u, deg q <= 8 -> for each t in 0..14:
        # sum_j f_j [j=t] - sum_i q_i u_{t-i} = r_t ; eliminating q: use remainder map instead:
        pass
    # simpler: f ≡ r (mod u) means f mod u = r. f mod u is linear in f coeffs:
    for u, v in samples:
        r = polymod(polymul(v, v), u)
        r += [0]*(len(u)-1-len(r))
        k = len(u)-1  # deg u
        for t in range(k):
            row = [0]*16
            # coefficient of x^t in f mod u: compute via reducing x^t mod u? t<deg u -> just f_t... 
            # BUT f mod u coefficient depends on ALL f_j: reduce x^j mod u for j>=k.
            row = [0]*16
            for j in range(16):
                xj = [0]*j + [1]
                rr = polymod(xj, u)
                if t < len(rr):
                    row[j] = rr[t]
            b.append(r[t] if t < len(r) else 0)
            A.append(row)
    sol = rref(A, b)
    if sol is None:
        return None, None
    return sol  # (particular, basis)

def polymul(a, b):
    r = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    r[i+j] = (r[i+j]+x*y) % P
    while len(r) > 1 and r[-1] == 0:
        r.pop()
    return r

def polymod(a, m):
    a = a[:]; m = m[:]
    inv = pow(m[-1], P-2, P)
    while True:
        while len(a) > 1 and a[-1] == 0:
            a.pop()
        if a == [0] or len(a) < len(m):
            break
        d = len(a)-len(m); c = a[-1]*inv % P
        for i in range(len(m)):
            a[i+d] = (a[i+d]-c*m[i]) % P
    return a
