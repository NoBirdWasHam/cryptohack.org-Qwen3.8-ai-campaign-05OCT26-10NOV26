# SAT solver v2: native cardinality (RC2/Minicard add_atmost) + byte-domain tries + assumptions
import ast, hashlib, os, sys, time
D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()
A = [[(pub[j] >> (255 - k)) & 1 for k in range(256)] for j in range(128)]
PRINTABLE = list(range(32, 127))

from pysat.formula import IDPool
from pysat.solvers import Solver

def pick_name():
    for nm in ('RC2', 'Minicard', 'Glucose4', 'Glucose3'):
        try:
            with Solver(name=nm) as s:
                return nm
        except Exception:
            continue
    raise RuntimeError('no solver')

NAME = pick_name()

def build(bi):
    pool = IDPool()
    clauses = []
    cards = []
    _ctr = [0]
    def fresh(key):
        _ctr[0] += 1
        return pool.id((key, _ctr[0]))
    def bv(pos): return pool.id(('bit', pos))
    def impl(p, vals, byte_bits):
        if len(vals) == 1:
            v = vals[0]
            return [[~p] + [(~b if (v >> (7 - i)) & 1 == 0 else b) for i, b in enumerate(byte_bits)]]
        out = []
        shared = []
        for i in range(8):
            bits = [(v >> (7 - i)) & 1 for v in vals]
            if all(b == bits[0] for b in bits):
                shared.append(byte_bits[i] if bits[0] else ~byte_bits[i])
        if shared: out.append([~p] + shared)
        for i in range(8):
            z = [v for v in vals if ((v >> (7 - i)) & 1) == 0]
            o = [v for v in vals if ((v >> (7 - i)) & 1) == 1]
            if z and o:
                a = fresh('g')
                res = [[~p, a]]
                res += [[~p] + cl for cl in impl(a, z, byte_bits)]
                res += [[~p] + cl for cl in impl(~a, o, byte_bits)]
                return res
        return out
    for j in range(128):
        lits = [bv(k + 1) for k in range(256) if k % 8 != 0 and A[j][k]]
        cards.append((lits, enc[bi][j]))
    ctrl = []
    for b in range(32):
        g = pool.id(('dom', b))
        ctrl.append(g)
        bits = [bv(8 * b + i + 1) for i in range(8)]
        clauses.extend(impl(g, PRINTABLE, bits))
    return pool, clauses, cards, bv, ctrl

def solve_with(bi, asm):
    pool, clauses, cards, bv, ctrl = build(bi)
    with Solver(name=NAME) as s:
        for cl in clauses:
            s.add_clause(cl)
        for lits, c in cards:
            s.add_atmost(lits, max(c, 0))
            if len(lits) - c - 1 >= 0:
                s.add_atmost([~x for x in lits], len(lits) - c - 1)
        full = asm + [ctrl[b] for b in range(32)]
        if not s.solve(assumptions=full):
            return None
        model = set(s.get_model())
        return bytes(int(''.join('1' if bv(8 * b + i + 1) in model else '0' for i in range(8)), 2) for b in range(32))

def char_asm(b, ch, bv):
    return [bv(8 * b + i + 1) if (ch >> (7 - i)) & 1 else -bv(8 * b + i + 1) for i in range(8)]

def verify(bi, mb):
    v = int.from_bytes(mb, 'big')
    return all((pub[j] & v).bit_count() == enc[bi][j] for j in range(128))

which = sys.argv[1] if len(sys.argv) > 1 else 'b0'
t0 = time.time()
print('solver:', NAME, flush=True)
if which == 'b0':
    asm = []
    for b in range(7):
        asm += char_asm(b, b'crypto{'[b], None) if False else []
    # need bv for assumptions -> use closure trick: bv maps pos->id deterministically via fresh? no, bv uses pool.id(('bit',pos)) stable. Rebuild same pool.
    pool, clauses, cards, bv, ctrl = build(0)
    asm = []
    for b in range(7):
        asm += char_asm(b, b'crypto{'[b], bv)
    with Solver(name=NAME) as s:
        for cl in clauses: s.add_clause(cl)
        for lits, c in cards:
            s.add_atmost(lits, c)
            s.add_atmost([~x for x in lits], len(lits) - c - 1)
        ok = s.solve(assumptions=asm + [ctrl[b] for b in range(32)])
        print('b0 sat:', ok, f'{time.time()-t0:.0f}s', flush=True)
        if ok:
            model = set(s.get_model())
            mb = bytes(int(''.join('1' if bv(8*b+i+1) in model else '0' for i in range(8)), 2) for b in range(32))
            print('block0 =', mb, flush=True)
            print('VERIFIED' if verify(0, mb) else 'VERIFY FAIL', flush=True)
            if verify(0, mb): open(os.path.join(D, 'seg0.txt'), 'wb').write(mb)
elif which == 'b1':
    mb = solve_with(1, [])
    print('b1 sat:', mb is not None, f'{time.time()-t0:.0f}s', flush=True)
    if mb:
        print('block1 =', mb, flush=True)
        print('VERIFIED' if verify(1, mb) else 'VERIFY FAIL', flush=True)
        if verify(1, mb): open(os.path.join(D, 'seg1.txt'), 'wb').write(mb)
elif which == 'b2':
    tlo = int(sys.argv[2]); thi = int(sys.argv[3])
    pool, clauses, cards, bv, ctrl = build(2)
    done = False
    with Solver(name=NAME) as s:
        for cl in clauses: s.add_clause(cl)
        for lits, c in cards:
            s.add_atmost(lits, c)
            s.add_atmost([~x for x in lits], len(lits) - c - 1)
        for t in range(tlo, thi + 1):
            asm = []
            for b in range(32):
                if b >= 32 - t:
                    asm.append(-ctrl[b])
                    asm += [-bv(8*b+i+1) for i in range(8)]
                elif b == 32 - t - 1:
                    asm.append(ctrl[b])
                    asm += char_asm(b, ord('}'), bv)
                else:
                    asm.append(ctrl[b])
            ok = s.solve(assumptions=asm)
            print(f't={t} sat={ok} {time.time()-t0:.0f}s', flush=True)
            if ok:
                model = set(s.get_model())
                mb = bytes(int(''.join('1' if bv(8*b+i+1) in model else '0' for i in range(8)), 2) for b in range(32))
                if not verify(2, mb):
                    print('verify fail at t', t, '-> skip', flush=True); continue
                print('block2 =', mb, 't =', t, flush=True)
                open(os.path.join(D, 'seg2.txt'), 'wb').write(mb)
                done = True
                break
    if not done: print('no t worked', flush=True)
