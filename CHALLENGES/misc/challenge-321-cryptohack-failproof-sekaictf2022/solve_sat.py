# SAT-based solver: exact-cardinality popcount equations + byte domain tries + per-position assumptions
import ast, hashlib, os, sys, time, itertools
D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()
A = [[(pub[j] >> (255 - k)) & 1 for k in range(256)] for j in range(128)]
PRINTABLE = list(range(32, 127))

from pysat.formula import IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

def build_block(bi):
    """fresh IDPool+clauses for block bi; returns (pool, clauses, card, bitvar)"""
    pool = IDPool()
    clauses = []
    def bitvar(pos):  # pos 1..256, MSB-first within block
        return pool.id(('bit', pos))
    # cardinality: exact sums on non-MSB positions
    lit_of = {}
    def b_lit(pos):
        v = bitvar(pos)
        if pos not in lit_of:
            lit_of[pos] = pool.id(('c', pos))
            clauses.append([lit_of[pos], v]); clauses.append([-lit_of[pos], -v])
        return lit_of[pos]
    free = [p for p in range(1, 257) if (p - 1) % 8 != 0]
    pb = PBEncoder([pool.id('dummy')] + [lit_of_settle() for _ in []] or [0])
    # PBEncoder needs nb_vars; rebuild with proper size after collecting lits
    enc = PBEncoder(2 * len(free) + 10)
    # map: use sequential helper vars via pb itself; simplest: pass helper ids through pool
    hbase = [pool.id(('h', i)) for i in range(200000)]
    class PB:
        def add_atmost(self, lits, bound, enc='cardnetwork'):
            def next_var():
                return pool.id('h')
            pb_local = PBEncoder(0, next_var=next_var)
            pb_local.update_atmost(list(lits), bound, enc)
            clauses.extend(pb_local.clauses)
    PB().add_atmost([b_lit(p) for p in free], enc[bi][sum(1 for j in range(1))])
    return pool, clauses, bitvar

# The above got messy; do it directly instead.
def build(bi):
    pool = IDPool()
    clauses = []
    _ctr = [0]
    def fresh(key):
        _ctr[0] += 1
        return pool.id((key, _ctr[0]))
    def bv(pos): return pool.id(('bit', pos))
    def impl(p, vals, bitpos_list, byte_bits):
        """clause set: literal p => (byte value in vals), byte bits = [lits for bits 7..0]"""
        if len(vals) == 1:
            v = vals[0]
            return [[~p] + [(~b if (v >> (7 - i)) & 1 == 0 else b) for i, b in enumerate(byte_bits)]]
        # shared bits can be added directly
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
                res += [[~p] + cl for cl in impl(a, z, None, byte_bits)]
                res += [[~p] + cl for cl in impl(~a, o, None, byte_bits)]
                return res
        return out
    # cardinality equations
    for j in range(128):
        lits = []
        for k in range(256):
            if k % 8 == 0: continue  # MSB always 0 for printable
            if A[j][k]:
                b = bv(k + 1)
                hv = fresh('c')
                clauses.append([hv, b]); clauses.append([-hv, -b])
                lits.append(hv)
        clauses.extend(CardEnc.atmost(lits, bound=enc[bi][j], vpool=pool, encoding='totalizer').clauses)
        clauses.extend(CardEnc.atmost([~x for x in lits], bound=len(lits) - enc[bi][j] - 1, vpool=pool, encoding='totalizer').clauses)
    # byte domains with control var
    ctrl = []
    for b in range(32):
        g = pool.id(('dom', b))
        ctrl.append(g)
        bits = [bv(8 * b + i + 1) for i in range(8)]
        clauses.extend(impl(g, PRINTABLE, None, bits))
    return pool, clauses, bv, ctrl

def assumptions_zero(b, ctrl, bv):
    out = [-ctrl[b]]
    for i in range(8): out.append(-bv(8 * b + i + 1))
    return out

def assumptions_char(b, ch, ctrl, bv):
    out = [ctrl[b]]
    for i in range(8):
        out.append(bv(8 * b + i + 1) if (ch >> (7 - i)) & 1 else -bv(8 * b + i + 1))
    return out

def run(bi, extra_assumptions, use_name=None):
    pool, clauses, bv, ctrl = build(bi)
    names = None
    ok = None
    with Solver(name='Glucose4', bootstrap_with=clauses) as s:
        ok = s.solve(assumptions=[ctrl[b] for b in range(32)] + extra_assumptions)
        if ok:
            model = s.get_model()
            vals = {}
            for b in range(32):
                v = 0
                for i in range(8):
                    lit = bv(8 * b + i + 1)
                    bit = (lit in model)
                    v = (v << 1) | (1 if bit else 0)
                vals[b] = v
            return bytes(vals[b] for b in range(32))
    return None

which = sys.argv[1] if len(sys.argv) > 1 else 'b0'
t0 = time.time()
if which == 'b0':
    asm = []
    for b in range(7):
        asm += assumptions_char(b, b'crypto{'[b], *(())) if False else []
    pool, clauses, bv, ctrl = build(0)
    with Solver(name='Glucose4', bootstrap_with=clauses) as s:
        asm = [ctrl[b] for b in range(32)]
        for b in range(7):
            ch = b'crypto{'[b]
            asm += [bv(8*b+i+1) if (ch >> (7-i)) & 1 else -bv(8*b+i+1) for i in range(8)]
        ok = s.solve(assumptions=asm)
        print('b0 sat:', ok, f'{time.time()-t0:.0f}s', flush=True)
        if ok:
            model = set(s.get_model())
            mb = bytes(int(''.join('1' if bv(8*b+i+1) in model else '0' for i in range(8)), 2) for b in range(32))
            print('block0 =', mb)
            assert all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == enc[0][j] for j in range(128)), 'verify FAIL'
            print('VERIFIED block0'); open(os.path.join(D, 'seg0.txt'), 'wb').write(mb)
elif which == 'b1':
    res = run(1, [])
    print('b1 sat:', res is not None, f'{time.time()-t0:.0f}s', flush=True)
    if res:
        mb = res
        assert all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == enc[1][j] for j in range(128)), 'verify FAIL'
        print('block1 =', mb); open(os.path.join(D, 'seg1.txt'), 'wb').write(mb)
elif which == 'b2':
    tlo = int(sys.argv[2]); thi = int(sys.argv[3])
    res = None
    for t in range(tlo, thi + 1):
        # rebuild each t is costly; instead reuse one build with assumptions per t:
        if 's' not in dir():
            pool, clauses, bv, ctrl = build(2)
            s = Solver(name='Glucose4', bootstrap_with=clauses)
            s.enter_context_state()
        asm = []
        for b in range(32):
            if b >= 32 - t:
                asm.append(-ctrl[b])
                asm += [-bv(8*b+i+1) for i in range(8)]
            elif b == 32 - t - 1:
                ch = ord('}')
                asm.append(ctrl[b])
                asm += [bv(8*b+i+1) if (ch >> (7-i)) & 1 else -bv(8*b+i+1) for i in range(8)]
            else:
                asm.append(ctrl[b])
        ok = s.solve(assumptions=asm)
        print(f't={t} sat={ok} {time.time()-t0:.0f}s', flush=True)
        if ok:
            model = set(s.get_model())
            mb = bytes(int(''.join('1' if bv(8*b+i+1) in model else '0' for i in range(8)), 2) for b in range(32))
            assert all((pub[j] & int.from_bytes(mb, 'big')).bit_count() == enc[2][j] for j in range(128))
            print('block2 =', mb, 't=', t)
            open(os.path.join(D, 'seg2.txt'), 'wb').write(mb)
            res = (t, mb); break
    if 's' in dir():
        s.exit_context_state(); s.delete()
    if res is None: print('no t worked')
