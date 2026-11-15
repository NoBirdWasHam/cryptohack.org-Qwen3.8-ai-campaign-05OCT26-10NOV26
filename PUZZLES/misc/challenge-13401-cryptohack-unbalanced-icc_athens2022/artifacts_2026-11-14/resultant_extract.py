"""Exact extraction: H_i(x,y) = y^Dz * h_i(x, y, N/y); Res_x(H1,H2) via fraction-free
Bareiss over Z[y]; integer roots -> p | N. Uses flint fmpz_poly for exact univariate poly math."""
import flint
import variants as V

Fp = flint.fmpz_poly


def h_to_H(poly, N, dz=None):
    """(x,y,z) poly (yz-reduced) -> Z[x,y] after z=N/y, times y^dz clearing denoms."""
    if dz is None:
        dz = max((m[2] for m in poly), default=0)
    out = {}  # (i,j) -> coeff
    for (a, b, c), v in poly.items():
        out[(a, b + (dz - c))] = out.get((a, b + (dz - c)), 0) + v * (N ** c)
    return out, dz


def poly_in_y(H, dx, degs=None):
    """H dict (i,j)->c  -> list over x-degree i of Fp in y. Return (polys, dy)."""
    dy = max((j for (_, j), v in H.items() if v), default=0) + 1
    rows = []
    for i in range(dx + 1):
        coeffs = [H.get((i, j), 0) for j in range(dy)]
        rows.append(Fp(coeffs))
    return rows, dy


def sub_poly(a, b):
    """a - b*mult with mult = lead(a)/lead(b) (monic-less): use exact fmpz_poly arithmetic.
    Only works when division exact; used in Bareiss where divisibility holds."""
    return a - b * flint.fmpz_poly([0])


def sylvester_bareiss(rows1, rows2, dx1, dx2):
    """Resultant of f=sum rows1[i] x^i, g=sum rows2[i] x^i over Z[y] by fraction-free
    Bareiss on the (dx1+dx2) x (dx1+dx2) Sylvester matrix of Fp entries."""
    dy = max(max(r.degree() for r in rows1), max(r.degree() for r in rows2)) + 1
    n = dx1 + dx2
    M = []
    for k in range(dx2):
        M.append([Fp(0)] * k + list(rows1) + [Fp(0)] * (dx2 - 1 - k))
    for k in range(dx1):
        M.append([Fp(0)] * k + list(rows2) + [Fp(0)] * (dx1 - 1 - k))
    # Bareiss fraction-free over commutative ring Z[y]
    prev = Fp([1])
    for k in range(n - 1):
        if M[k][k].is_zero():
            # find swap row
            for r in range(k + 1, n):
                if not M[r][k].is_zero():
                    M[k], M[r] = M[r], M[k]
                    break
            else:
                return Fp([0])
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                num = M[i][j] * M[k][k] - M[i][k] * M[k][j]
                quo = num.exactly_divide(prev) if hasattr(num, "exactly_divide") else num // prev
                assert quo * prev == num, "Bareiss divisibility failed"
                M[i][j] = quo
        prev = M[k][k]
    return M[n - 1][n - 1]


def find_p(h1, h2, N, verbose=True):
    """h1,h2 dicts vanishing at (2k,p,q). Return list of integer candidates p dividing N."""
    H1, dz1 = h_to_H(h1, N)
    H2, dz2 = h_to_H(h2, N)
    dx1 = max(i for (i, j) in H1)
    dx2 = max(i for (i, j) in H2)
    rows1, dy1 = poly_in_y(H1, dx1)
    rows2, dy2 = poly_in_y(H2, dx2)
    # pad row dy lengths to common
    dy = max(dy1, dy2)
    rows1 = [Fp(list(r) + [0] * (dy - len(r))) for r in rows1]
    rows2 = [Fp(list(r) + [0] * (dy - len(r))) for r in rows2]
    if verbose:
        print(f"resultant: dx1={dx1} dx2={dx2} dy={dy}")
    R = sylvester_bareiss(rows1, rows2, dx1, dx2)
    if verbose:
        print(f"Res degree in y: {R.degree()}, coeff bits ~{max(abs(c).bit_length() for c in list(R)) if R.degree()>=0 else 0}")
    # integer roots
    cands = []
    if R.degree() < 0 or R.is_zero():
        return cands
    # strip content
    cont = R.content()
    R = R // cont
    # exact integer roots first (fmpz_poly.roots gives exact rational/integer roots)
    try:
        for r_, mult in R.roots():
            if r_.q == 1:
                p_ = int(r_.p)
                if p_ > 1 and N % p_ == 0:
                    cands.append(p_)
    except Exception:
        pass
    if not cands and R.degree() >= 1:
        try:
            cont_, fac = R.factor()
            for f_, mult in fac:
                if f_.degree() == 1:
                    a0, a1 = int(f_[0]), int(f_[1])
                    if a1 != 0 and a0 % a1 == 0:
                        p_ = -a0 // a1
                        if p_ > 1 and N % p_ == 0:
                            cands.append(p_)
        except Exception as ex:
            print("factor path failed:", ex)
    if not cands and R.degree() >= 1:
        rr_list = R.real_roots(prec=8000) if hasattr(R, "real_roots") else []
        for rt in rr_list:
            rr = int(rt)
            for adj in range(-2, 3):
                p_ = rr + adj
                if p_ > 1 and N % p_ == 0:
                    cands.append(p_)
    return sorted(set(cands))
