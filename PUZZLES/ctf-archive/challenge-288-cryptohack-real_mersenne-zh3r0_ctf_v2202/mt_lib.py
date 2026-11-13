"""MT19937 recovery for 'real_mersenne': random() leaks top 27 bits of o_{2i}
and top 26 bits of o_{2i+1}. Unknowns = low 5 bits (even) + low 6 bits (odd) of
the first 624 outputs; observed bits of cycle-2 outputs -> GF(2) equations.
"""
N, M, MA = 624, 397, 0x9908b0df

def temper(y):
    y &= 0xffffffff
    y ^= y >> 11
    y ^= (y << 7) & 0x9d2c5680
    y ^= (y << 15) & 0xefc60000
    y ^= y >> 18
    return y & 0xffffffff

def untemper(t):
    # invert temper steps in reverse order; (I+N)^7 = I+N+...+N^7 (all binom
    # coefficients odd) which equals (I+N)^{-1} once N^5 = 0.
    y = t & 0xffffffff
    y ^= y >> 18
    for _ in range(7):
        y ^= (y << 15) & 0xEFC60000
    for _ in range(7):
        y ^= (y << 7) & 0x9D2C5680
    for _ in range(7):
        y ^= y >> 11
    return y & 0xffffffff

def gen_cycle(s):
    o = []
    for i in range(N):
        y = (s[i] & 0x80000000) | (s[(i + 1) % N] & 0x7FFFFFFF)
        s[i] = (s[(i + M) % N] ^ (y >> 1) ^ (MA if y & 1 else 0)) & 0xffffffff
        o.append(temper(s[i]))
    return o

def _untamper_matrix():
    T = [temper(1 << i) for i in range(32)]  # col i: image of raw basis vec
    # A[j][i] = bit j of T[i]; invert 32x32 GF(2) matrix A via [A|I] row ops
    A = [0] * 32  # each row: 64-bit int, left = A part, right = I part
    for j in range(32):
        left = 0
        for i in range(32):
            if (T[i] >> j) & 1:
                left |= 1 << i
        A[j] = left | (1 << (32 + j))
    for col in range(32):
        piv = next(r for r in range(col, 32) if (A[r] >> col) & 1)
        A[col], A[piv] = A[piv], A[col]
        for r in range(32):
            if r != col and (A[r] >> col) & 1:
                A[r] ^= A[col]
    return [[j for j in range(32) if (A[i] >> (32 + j)) & 1] for i in range(32)]

TINV = _untamper_matrix()

def uidx(j, b):
    return (j >> 1) * 11 + (b if (j & 1) == 0 else 5 + b)

def build_and_solve(us, solve_lo, solve_hi, holdout_lo, holdout_hi):
    """us: round -> u (53-bit). Returns state-after-cycle-1 (624 words).
    Equations from rounds solve_lo..solve_hi; verifies holdout_lo..holdout_hi."""
    def sym_out(j, u):
        if (j & 1) == 0:
            e = [(1 << uidx(j, b)) if b < 5 else 0 for b in range(32)]
            c = (u >> 26) << 5
        else:
            e = [(1 << uidx(j, b)) if b < 6 else 0 for b in range(32)]
            c = (u << 6) & 0xFFFFFFC0
        return e, c

    state = []
    for j in range(N):
        oe, oc = sym_out(j, us[j >> 1])
        e = [0] * 32
        c = 0
        for i in range(32):
            ri, rc = 0, 0
            for jb in TINV[i]:
                ri ^= oe[jb]
                rc ^= (oc >> jb) & 1
            e[i] = ri
            c |= rc << i
        state.append((e, c))

    outputs = {}  # (cycle, idx) -> symbolic word
    for cyc in (2, 3):
        for i in range(N):
            ae, ac = state[i]
            s1e, s1c = state[(i + 1) % N]
            ye = [ae[31] if j == 31 else s1e[j] for j in range(32)]
            yc = ((ac >> 31) << 31) | (s1c & 0x7FFFFFFF)
            she, shc = ye[1:] + [0], yc >> 1
            me = [ye[0] if (MA >> j) & 1 else 0 for j in range(32)]
            mc = MA & (0xFFFFFFFF if (yc & 1) else 0)
            pe, pc = state[(i + M) % N]
            ne = [pe[j] ^ she[j] ^ me[j] for j in range(32)]
            nc = pc ^ shc ^ mc
            state[i] = (ne, nc)  # raw new word (tempering must NOT write back)
            te, tc = ne[:], nc
            def xorew(e, c, k):
                return [e[j] ^ e[j + k] for j in range(32 - k)] + e[32 - k:], c ^ (c >> k)
            def shlm(e, c, k, m):
                se = [0] * k + e[:32 - k]
                se = [se[j] if (m >> j) & 1 else 0 for j in range(32)]
                return [e[j] ^ se[j] for j in range(32)], c ^ ((c << k) & m)
            te, tc = xorew(te, tc, 11)
            te, tc = shlm(te, tc, 7, 0x9D2C5680)
            te, tc = shlm(te, tc, 15, 0xEFC60000)
            te, tc = xorew(te, tc, 18)
            outputs[(cyc, i)] = (te, tc)

    def out_for_round(r_):
        o1, o2 = 2 * r_, 2 * r_ + 1
        if o1 < 1248:
            return ("k", (2, o1 - 624), (2, o2 - 624))
        return ("k", (3, o1 - 1248), (3, o2 - 1248))

    rows = []
    for r_ in range(solve_lo, solve_hi + 1):
        u = us.get(r_)
        if u is None or r_ < 312 or r_ > 935:
            continue
        _, k1, k2 = out_for_round(r_)
        for j, k in ((0, k1), (1, k2)):
            te, tc = outputs[k]
            b0 = 5 if j == 0 else 6
            for bj in range(b0, 32):
                obs = (u >> (bj + 21)) & 1 if j == 0 else (u >> (bj - 6)) & 1
                rows.append((te[bj], obs ^ ((tc >> bj) & 1)))

    piv = {}
    for x, rhs in rows:
        while x:
            k = x.bit_length() - 1
            if k in piv:
                x2, r2 = piv[k]
                x ^= x2
                rhs ^= r2
            else:
                piv[k] = (x, rhs)
                break
        else:
            if rhs:
                raise ValueError("inconsistent system")
    val = {}
    if __import__("os").environ.get("MT_DEBUG"):
        print("rows=%d rank=%d unknowns=%d" % (len(rows), len(piv), 312 * 11))
    for k in sorted(piv):
        x, rhs = piv[k]
        acc = rhs
        m = x ^ (1 << k)
        while m:
            b = m & -m
            acc ^= val.get(b.bit_length() - 1, 0)
            m ^= b
        val[k] = acc

    outs = []
    for j in range(N):
        u = us[j >> 1]
        if (j & 1) == 0:
            high = (u >> 26) << 5
            low = sum(val.get(uidx(j, b), 0) << b for b in range(5))
        else:
            high = (u << 6) & 0xFFFFFFC0
            low = sum(val.get(uidx(j, b), 0) << b for b in range(6))
        outs.append(high | low)
    st1 = [untemper(o) for o in outs]

    s = st1[:]
    outs2 = []
    for _ in range((holdout_hi - 624) // 624 + 2):
        outs2 += gen_cycle(s)
    for r_ in range(holdout_lo, holdout_hi + 1):
        u = us.get(r_)
        if u is None:
            continue
        pred = ((outs2[2 * r_ - 624] >> 5) << 26) + (outs2[2 * r_ + 1 - 624] >> 6)
        if pred != u:
            raise ValueError("holdout mismatch at round %d" % r_)
    return st1

def make_predictor(st1):
    s = st1[:]
    buf = []
    def next_u():
        while len(buf) < 2:
            buf.extend(gen_cycle(s))
        a, b = buf.pop(0), buf.pop(0)
        return ((a >> 5) << 26) + (b >> 6)
    return next_u
