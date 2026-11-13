# identify sage GF(p^2) primitive basis vs our a-basis using P_G2 = u*G2 (unknown u)
import tower as T, json
T.discover()
P=T.P
G2=(T.G2X,T.G2Y)
G2Xs = "100774561144590475569157120930767342387*a + 218728496724280042701446122970647661523"
G2Ys = "115367896606755692925113233629944781384*a + 211093354487559124632805793736258741445"

def parse_fp2(s, a_sage):
    # returns our-tuple for element with poly coeff over sage a: c1*a + c0 -> c0 + c1*a_sage
    import re
    s = s.replace(' ','')
    m = re.match(r'^(\d+)\*a\+(\d+)$', s)
    if m:
        c1,c0 = int(m.group(1)), int(m.group(2))
    else:
        m = re.match(r'^(\d+)$', s); c0 = int(m.group(1)); c1 = 0
    return T.f2add((c0,0), T.f2mul((c1,0), a_sage))

def e2_double(Pp): return T.e2_double(Pp)
def e2_add(A,B): return T.e2_add(A,B)
def e2_mul(k,Pp): return T.e2_mul(k,Pp)
def e2_eq(A,B): return A==B

def match(PG2, a_sage):
    # search u in small range
    acc = T.e2_add(PG2, PG2)  # start k=2... do incremental
    cur = T.e2_double(PG2)
    for k in range(2, 300000):
        if cur == G2:
            print('MATCH u =', k); return k
        if cur is not None and (cur[1] == T.f2neg(G2[1]) and cur[0] == G2[0]):
            print('MATCH u =', -k % T.N); return -k % T.N
        cur = T.e2_add(cur, PG2)
    return None

def try_repr(PG2, name, a_sage):
    # check PG2 on curve (necessary; model-independent consistency)
    if not T.e2_oncurve(PG2):
        print(name, ': PG2 NOT on curve -> repr wrong'); return None
    print(name, ': on curve ok')
    u = match(PG2, a_sage)
    if u is None:
        print(name, ': no small u'); return None
    # verify: Sage int repr of a_sage = (a_sage[1], a_sage[0])
    sage_a_int = (a_sage[1], a_sage[0])
    print(name, '=> u =', u, ' sage a =', a_sage, ' a_minpoly ok:', T.f2eqv(T.f2add(T.f2add(T.f2sq(a_sage), a_sage), T.F21), T.F20))
    return sage_a_int

def main(params_str, du0, du1):
    params = json.loads(params_str)
    pg2_raw = params['P_G2']
    du0_raw = du0  # list [x,y] ints-as-strings (sage ints)
    # candidates for sage a in our basis: roots of x^2+x-1
    disc = (1 + 4) % P
    import gmpy2
    s = int(gmpy2.isqrt(disc)) if False else None
    from tower import fp_sqrt
    sq = fp_sqrt(5 % P)
    cands = []
    for root in ((-1 + sq) * pow(2, P-2, P) % P, (-1 - sq) * pow(2, P-2, P) % P):
        cands.append(((P - 1 + root) % P, 1))  # a_sage = (c0,c1) = (root-1?? ) NO:
    # a_sage is element with trace -1 norm -1: a_sage = (-1 + sqrt(5))/2 where sqrt(5) in our ext: sqrt5 = e*(1-2a)
    e = T.f2inv(T.EPS); one_minus_2a = T.f2sub(T.F21, T.f2mulk(T.EPSA and T.f2inv(T.EPS) and (0,1) or (0,1), 2))
    # careful: our a = (0,1). sqrt5 = e*(1-2a):
    sqrt5 = T.f2mul(T.f2inv(T.EPS), T.f2sub(T.F21, T.f2mulk((0,1), 2)))
    print('sqrt5 check:', T.f2eqv(T.f2sq(sqrt5), (5,0)))
    inv2 = (P+1)//2
    a_sage1 = T.f2mulk(T.f2add(T.f2neg(T.F21), sqrt5), inv2)
    a_sage2 = T.f2mulk(T.f2sub(T.f2neg(T.F21), sqrt5), P-1)
    a_sage2 = T.f2neg(T.f2add(T.F21, a_sage1))
    for i, a_sage in enumerate([a_sage1, a_sage2]):
        print('--- candidate a_sage', i, a_sage)
        PG2 = tuple(parse_fp2(s, a_sage) for s in pg2_raw)
        try_repr(PG2, f'cand{i}', a_sage)

if __name__ == '__main__':
    import socket
    s = socket.create_connection(("archive.cryptohack.org",25469), timeout=25)
    f = s.makefile('rwb')
    rl = lambda: f.readline().decode().strip()
    sd = lambda l: (f.write((l+"\n").encode()), f.flush())
    l1 = rl(); ps = rl()
    sd("idfuser")
    du0 = rl(); du1 = rl()
    s.close()
    print('P_G2 raw:', ps[:100])
    main(ps, du0, du1)
