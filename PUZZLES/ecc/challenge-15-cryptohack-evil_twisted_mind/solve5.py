#!/usr/bin/env python3
# evil_twisted_mind — composite-modulus two-twist attack.
# p = q1*q2 (q1 recovered via gcd(order*x0.Z, p)).
#   #E(Fq1)   = order (prime)          #twist(Fq1) = T1s * T1big
#   #E(Fq2)   = E2 (prime)             #twist(Fq2) = S2s * R2
#   T1s = 1965293129*3945014767*6911909839           (96 bits)
#   S2s = 17*1789*8984179*9381319*83816652113        (97 bits)
# Pick x_R with f NR mod BOTH qi (twist on both sides). x0 = A*R, A = R2*T1big:
#   ord_q1(x0) | T1s, ord_q2(x0) | S2s  (A kills the big prime on its own side,
#   is an automorphism on the other). Oracle Y = x(k*x0). x-only rho per prime
#   factor on each side -> k mod (T1s*S2s) = k exactly (product > order > k).
import re, math, random, socket, json, ast

src = open("13418.py").read()
p = int(re.search(r"modulus\s*=\s*(\d+)", src).group(1))
a = -3
b = int(re.search(r"^b\s*=\s*(\d+)", src, re.M).group(1))
order = int(re.search(r"^order\s*=\s*(\d+)", src, re.M).group(1))

T1s_primes = [1965293129, 3945014767, 6911909839]
S2s_primes = [17, 1789, 8984179, 9381319, 83816652113]
T1s = math.prod(T1s_primes)
S2s = math.prod(S2s_primes)
T1big = 89250943167080667773197903811
R2 = 22324892568046125682687618733
A_mul = R2 * T1big

def sxz(X1, Z1, m):
    XX = X1*X1 % m; ZZ = Z1*Z1 % m
    A2 = 2*((X1+Z1)**2 - XX - ZZ) % m
    aZZ = a*ZZ % m
    X3 = ((XX - aZZ)**2 - 2*b*A2*ZZ) % m
    Z3 = (A2*(XX + aZZ) + 4*b*ZZ*ZZ) % m
    return (X3, Z3)

def sdiff(X1, Z1, X2, Z2, xd, m):
    X1Z2 = X1*Z2 % m; X2Z1 = X2*Z1 % m; Z1Z2 = Z1*Z2 % m
    T = (X1Z2 + X2Z1)*(X1*X2 + a*Z1Z2) % m
    Z3 = (X1Z2 - X2Z1)**2 % m
    X3 = (2*T + 4*b*Z1Z2**2 - xd*Z3) % m
    return (X3, Z3)

def ladder_full(scalar, x0, m):
    if scalar == 0: return (1, 0)
    R0 = (x0, 1); R1 = sxz(*R0, m)
    n = scalar.bit_length(); pbit = 0; bit = 0
    for i in range(n-2, -1, -1):
        bit = (scalar >> i) & 1
        pbit ^= bit
        if pbit: R0, R1 = R1, R0
        R1 = sdiff(*R0, *R1, x0, m)
        R0 = sxz(*R0, m)
        pbit = bit
    if bit: R0 = R1
    return R0

def ladder(scalar, x0, m):
    X, Z = ladder_full(scalar, x0, m)
    return None if Z == 0 else X * pow(Z, -1, m) % m

def legendre(n, q): return pow(n % q, (q-1)//2, q)
def fval(x, m): return (x**3 + a*x*x + x) * pow(b, -1, m) % m

# ---------- factor p ----------
rng = random.Random(11)
while True:
    X, Z = ladder_full(order, rng.randrange(2, p), p)
    g = math.gcd(Z, p)
    if g not in (1, p): break
q1, q2 = sorted((g, p//g))
assert q1 * q2 == p
print("q1 bits", q1.bit_length(), "q2 bits", q2.bit_length(), flush=True)

# ---------- x_R on twist over both components ----------
def find_nr(q):
    while legendre(fval(rng.randrange(2, q), q), q) != q-1: pass
    # returns x with f NR
    while True:
        x = rng.randrange(2, q)
        if legendre(fval(x, q), q) == q-1: return x
# careful: first while is a bug-free rewrite below
def find_nr2(q):
    while True:
        x = rng.randrange(2, q)
        if legendre(fval(x, q), q) == q-1: return x
x1 = find_nr2(q1); x2 = find_nr2(q2)
xR = x1 * q2 * pow(q2, -1, q1) + x2 * q1 * pow(q1, -1, q2)
xR %= p
assert legendre(fval(xR % q1, q1), q1) == q1-1
assert legendre(fval(xR % q2, q2), q2) == q2-1
x0 = ladder(A_mul, xR, p)
assert x0 is not None
# verify component orders
assert ladder(T1s, x0 % q1, q1) is None, "q1 order not dividing T1s"
assert ladder(S2s, x0 % q2, q2) is None, "q2 order not dividing S2s"
# ensure each prime factor actually present (else retry with new xR)
def full_presence(primes, N, x0c, q):
    for pp in primes:
        if ladder(N//pp, x0c, q) is None:
            return False
    return True
if not (full_presence(T1s_primes, T1s, x0 % q1, q1) and full_presence(S2s_primes, S2s, x0 % q2, q2)):
    print("missing a factor; rerun (rare)"); raise SystemExit(1)
print("x0 ready: ord_q1 | T1s, ord_q2 | S2s, all primes present", flush=True)

# ---------- oracle ----------
s = socket.create_connection(("socket.cryptohack.org", 13418), timeout=30)
f = s.makefile("rwb")
def send(o):
    f.write((json.dumps(o)+"\n").encode()); f.flush()
    return ast.literal_eval(f.readline().decode())
banner = b""
while banner.count(b"\n") < 2:
    ln = f.readline()
    if not ln: break
    banner += ln
Y = int(send({"option": "get_pubkey", "x0": str(x0)})["pubkey"])
print("pubkey received", flush=True)

# ---------- x-only rho (GLV-style, state (xP, x(P-G))) ----------
def dlog_x(Gx, Hx, pp, q, xG):
    """find d in [0,pp) with x(d*G) == Hx; G has order pp; xG = x(G)."""
    if Hx is None: return 0
    mask = (1 << 20) - 1
    table = {}
    # walk on (xP, x(P-G)) with P = a*G + b*H
    def step(state):
        xP, xPmG, aa, bb = state
        if xP is None or xPmG is None:
            # P or P-G at infinity: nudge by adding G (x(P+G)=diffadd(P,G,x(P-G)) fails
            # if xPmG None; handle by restarting walk with different start (rare)
            return None
        if xP & 1:  # double: P->2P: x2P=dbl(xP); x(2P-G)=diffadd(P, P-G, xG)
            X2, Z2 = sxz(xP, 1, q)
            x2 = None if Z2 == 0 else X2 * pow(Z2, -1, q) % q
            Xd, Zd = sdiff(xP, 1, xPmG, 1, xG, q)
            xd = None if Zd == 0 else Xd * pow(Zd, -1, q) % q
            return (x2, xd, (2*aa) % pp, (2*bb) % pp)
        else:       # add G: P->P+G: x(P+G)=diffadd(P,G,x(P-G)); new x(P'-G)=xP
            Xa, Za = sdiff(xP, 1, xG, 1, xPmG, q)
            xa = None if Za == 0 else Xa * pow(Za, -1, q) % q
            return (xa, xP, (aa+1) % pp, bb)
    def walk(x0s, x0mG, a0, b0, store):
        st = (x0s, x0mG, a0, b0)
        for it in range(12 * math.isqrt(pp) + 100000):
            st = step(st)
            if st is None or st[0] is None: return None, st
            xP = st[0]
            if (xP & mask) == 0:
                if store:
                    table[xP] = (st[2], st[3])
                elif xP in table:
                    a2, b2 = table[xP]
                    a1, b1 = st[2], st[3]
                    # x equal: P1 = +P2 or P1 = -P2
                    for sgn in (1, -1):
                        # a1 G + b1 H = sgn*(a2 G + b2 H); H = k G
                        # (a1 - sgn a2) + (b1 - sgn b2) k = 0  (mod pp)
                        cb = (b1 - sgn*b2) % pp
                        ca = (sgn*a2 - a1) % pp
                        if cb:
                            cand = ca * pow(cb, -1, pp) % pp
                            if ladder(cand, Gx, q) == Hx:
                                return cand, st
                    # false collision, keep walking
                    continue
        return None, st
    # distinguished-point rho: single walk storing DP; collision with itself gives
    # nothing; standard trick: store DP then look for repeat x from DIFFERENT (a,b).
    # Simplest robust: store all DPs; when xP already in table with different (a,b):
    st = (Hx, None, 0, 1)  # P=H: x(P-G) unknown! start P=H needs x(H-G): compute?
    # x(H-G) = x((k-1)G) unknown. START at P=O instead: xP=None breaks step.
    # Start P = H + G? x(P-G)=x(H) known! xP = x(H+G)=diffadd(H,G,x(H-G)) unknown.
    # Start P = 2G? then a=2,b=0: x(P-G)=xG known, xP=x(2G)=dbl(xG) known. Walk with
    # b starting 0: but pure (a,0) + steps addG/dbl reach b>0 only via... b doubles/increments
    # from 0 stays 0! Need b0 != 0: P = H + 2G: x(P-G) = x(H+G) unknown.
    # Use state (xP, x(P+G)) variant instead: start P=H: x(P+G)=diffadd(H,G,x(H-G)) unknown.
    # => start P = G + H is problematic; instead track (xP, x(P - H)) too? Standard MONL:
    # initialize P0 = G + H with x(P0 - G)=x(H) known and x(P0 - H)=x(G) known; track
    # BOTH x(P-G) and x(P-H): addG needs x(P-G) -> new x(P+G-G)=xP, x(P+G-H)=diffadd(P-H? )
    # For simplicity: THREE-way state (xP, xPmG, xPmH):
    #  addG: xP'=diffadd(xP,xG,xPmG); xPmG'=xP; xPmH'=x(P+G-H)=diffadd(xPmH, xG, x(P-H-G))✗
    # Not closed. FINAL: use two independent walks (tortoise on multiples of G vs H-walk)
    # meeting: x(aG) == x(a'G + b H)? no.
    # WORKING approach: distinguished-point rho on walk P=aG+bH with state (xP, x(P-G)),
    # START at P = G (a=1,b=0): x(P-G)=x(O)=None -> step dbl: x(2G), x(2G-G)=xG: fine
    # (dbl needs xPmG=x(O)? x(2P-G)=diffadd(P,P-G,xG): P-G=O -> x(O) undefined -> dbl
    # from P=G: x(2G-G)=x(G)=xG known directly!). Special-case: if PmG is O then
    # x(2P-G)=xG and x(P+G)... Let me just special-case None xPmG:
    #   dbl with P-G=O: x(2P-G) = xG. addG with P-G=O: x(P+G)=diffadd needs x(P-G)=x(O)
    #   -> but P=G: P+G=2G: x=dbl(xG). Handle via ladder fallback when aa,bb small.
    raise NotImplementedError

print("rho design needs care; using incremental-walk enumeration for small primes and "
      "careful DP-rho for 83816652113", flush=True)
s.close()
