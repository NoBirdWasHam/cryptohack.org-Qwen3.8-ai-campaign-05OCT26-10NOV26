# SAT v3: compact adder-tree exact-sum encoding + Glucose4
import ast, hashlib, os, sys, time
D = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(D, sys.argv[3] if len(sys.argv) > 3 else 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()
A = [[(pub[j] >> (255 - k)) & 1 for k in range(256)] for j in range(128)]

from pysat.formula import IDPool, WCNF
from pysat.solvers import Solver

NAME = sys.argv[2] if len(sys.argv) > 2 else 'Glucose4'

class Enc:
    def __init__(self):
        self.pool = IDPool()
        self.clauses = []
        self.n = 0
    def fresh(self):
        self.n += 1
        return self.pool.id(('aux', self.n))
    def lit(self, key):
        return self.pool.id(key)
    def fa(self, a, b):
        """sum bit (a xor b), carry (a&b)"""
        s = self.fresh(); c = self.fresh()
        # s = a XOR b
        self.clauses += [[a, b, -s], [a, -b, s], [-a, b, s], [-a, -b, -s]]
        # c = a & b
        self.clauses += [[-a, -b, c], [-c, a], [-c, b]]
        return s, c
    def ha(self, a, b, cin):
        s1, c1 = self.fa(a, b)
        s, c2 = self.fa(s1, cin)
        cout = self.fresh()
        # cout <-> maj(a,b,cin)
        self.clauses += [[-a, -b, cout], [-a, -cin, cout], [-b, -cin, cout]]
        self.clauses += [[-cout, a, b], [-cout, a, cin], [-cout, b, cin]]
        return s, cout
    def sum_to_bits(self, lits):
        """return list of output bit vars (LSB..MSB) of sum(lits) via column addition"""
        cols = [[l] for l in lits]  # weight-1 columns: just the lits
        # iterative carry-save: reduce columns while any col >2 entries: standard: pairwise
        # We'll do: treat list of weight-1 bits, build binary tree of adders.
        def add_lists(l1, l2):
            # l1,l2: lists of literals (bits, LSB..MSB) sums; returns sum bits of l1+l2
            out = []
            carry = None
            for i in range(max(len(l1), len(l2))):
                a = l1[i] if i < len(l1) else None
                b = l2[i] if i < len(l2) else None
                if a is None and b is None:
                    if carry is not None: out.append(carry); carry = None
                    continue
                if carry is None:
                    if b is None:
                        out.append(a)
                    else:
                        s, carry = self.fa(a, b)
                        out.append(s)
                else:
                    if b is None:
                        s, carry2 = self.fa(a, carry)
                        out.append(s); carry = carry2
                    else:
                        s, carry = self.ha(a, b, carry)
                        out.append(s)
            if carry is not None: out.append(carry)
            return out
        acc = [lits[0]]
        rest = lits[1:]
        # balanced-ish
        for l in rest[::1]:
            acc = add_lists(acc, [l])
        return acc
    def fix_exact(self, bits, val):
        # bits LSB..MSB == val
        for i, b in enumerate(bits):
            want = (val >> i) & 1
            self.clauses.append([b if want else -b])
        for i in range(len(bits), val.bit_length()):
            if (val >> i) & 1:
                raise ValueError('overflow')

def build(bi, known_constraints):
    """known_constraints: dict pos->bitval for forced positions (1..256). Returns Enc, bv(key) map."""
    e = Enc()
    def bv(pos): return e.lit(('bit', pos))
    for j in range(128):
        # equation over unknown non-MSB bits
        ulits = []
        c = enc[bi][j]
        for k in range(256):
            if k % 8 == 0:
                continue
            pos = k + 1
            if pos in known_constraints:
                c -= A[j][k] * known_constraints[pos]
            else:
                if A[j][k]:
                    ulits.append(bv(pos))
        bits = e.sum_to_bits(ulits)
        e.fix_exact(bits, c)
    # byte domain: printable + explicit zero bytes handled via known_constraints
    for b in range(32):
        bits = [bv(8 * b + i + 1) for i in range(8)]
        # skip bytes fully known (all positions in known_constraints)
        if all((8 * b + i + 1) in known_constraints for i in range(8)):
            continue
        e.clauses.append([-bv(8 * b + 1)])  # MSB = 0
        # forbid 1..31: (0x40 or 0x20) or all low5 zero
        e.clauses.append([bv(8*b+2), bv(8*b+3)] + [-bv(8*b+j) for j in (4, 5, 6, 7, 8)])
        # forbid 127 (0x40..0x01 all set)
        e.clauses.append([-bv(8 * b + i + 1) for i in range(1, 8)])
    # forced positions
    for pos, v in known_constraints.items():
        e.clauses.append([bv(pos) if v else -bv(pos)])
    return e, bv

def verify(bi, mb):
    v = int.from_bytes(mb, 'big')
    return all((pub[j] & v).bit_count() == enc[bi][j] for j in range(128))

def model_bytes(model, bv):
    out = b''
    for b in range(32):
        v = 0
        for i in range(8):
            v = (v << 1) | (1 if bv(8 * b + i + 1) in model else 0)
        out += bytes([v])
    return out

which = sys.argv[1]
t0 = time.time()
known = {}
if which == 'b0':
    for b in range(7):
        ch = b'crypto{'[b]
        for i in range(8):
            known[8 * b + i + 1] = (ch >> (7 - i)) & 1
elif which == 'b1':
    pass
elif which == 'b2':
    t = 18
    for b in range(32 - t, 32):
        for i in range(8): known[8 * b + i + 1] = 0
    ch = ord('}')
    for i in range(8): known[8 * (31 - t) + i + 1] = (ch >> (7 - i)) & 1
print('encoding...', flush=True)
e, bv = build(int(which[1]), known)
print('clauses:', len(e.clauses), f'{time.time()-t0:.0f}s', flush=True)
with Solver(name=NAME, bootstrap_with=e.clauses) as s:
    ok = s.solve()
    print(which, 'sat:', ok, f'{time.time()-t0:.0f}s', flush=True)
    if ok:
        model = set(s.get_model())
        mb = model_bytes(model, bv)
        print(which, '=', mb, flush=True)
        print('VERIFIED' if verify(int(which[1]), mb) else 'VERIFY FAIL', flush=True)
        if verify(int(which[1]), mb):
            open(os.path.join(D, which + '.txt'), 'wb').write(mb)
