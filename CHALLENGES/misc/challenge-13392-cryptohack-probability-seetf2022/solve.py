#!/usr/bin/env python3
"""SEETF 'probability' (probability-seetf2022).

Honest optimal play wins 0.4244/round < 800/1337 needed. So: the server prints
every random.random() draw -> each reveals bits 31..5 of one MT19937 output and
bits 31..6 of its partner. Recover the state (enumerate <=6 unknown low bits of
each observed output for the 624 base words; filter twist words by the observed
top bits of temper(w_i)), verify by round-trip, then play with foresight.

  python3 solve.py          local end-to-end sim (server reimplemented from
                            probability.py, same protocol handling)
  python3 solve.py --net    archive.cryptohack.org:59737
"""
import re, sys, random, socket, time

PROMPT = 'Do you want to hit or stand? '
DRAW_RE = re.compile(r'\[([0-9.eE+-]+)\]')

# ---------- MT19937 ----------
R = 0x9908b0df

def temper(y):
    y ^= y >> 11
    y = (y ^ ((y << 7) & 0x9d2c5680)) & 0xffffffff
    y = (y ^ ((y << 15) & 0xefc60000)) & 0xffffffff
    y ^= y >> 18
    return y

def _inv_rshift_xor(y, s):
    x = y
    m = s
    while m < 32:
        x ^= y >> m
        m *= 2
    return x & 0xffffffff

def _inv_lshift_xor(y, s, mask):
    x = [(y >> i) & 1 for i in range(32)]
    for i in range(s, 32):
        if (mask >> i) & 1:
            x[i] ^= x[i - s]
    return sum(x[i] << i for i in range(32)) & 0xffffffff

def untemper(y):
    x = _inv_rshift_xor(y, 18)
    x = _inv_lshift_xor(x, 15, 0xefc60000)
    x = _inv_lshift_xor(x, 7, 0x9d2c5680)
    return _inv_rshift_xor(x, 11)

_rr = random.Random(7)
for _ in range(500):
    _w = _rr.getrandbits(32)
    assert untemper(temper(_w)) == _w

def mt_next(ws, i):
    """CPython in-place twist, stream-indexed (verified vs live CPython):
    ws[i] = ws[i-227] ^ f(ws[i-624], ws[i-623])."""
    a, b = ws[i - 624], ws[i - 623]
    y = ((a & 0x80000000) | (b & 0x7fffffff)) >> 1
    if b & 1:
        y ^= R
    return (ws[i - 227] ^ y) & 0xffffffff

def recover(doubles):
    """624-word MT19937 state from observed random() outputs, or None.

    GF(2) linear recovery: every base word w_i is known up to its low 5 (even
    draw-slot) / 6 (odd slot) bits after untemper, so parametrize by those free
    bits. twist and temper are GF(2)-linear, so each observed top bit of a twist
    word gives one linear equation in the free bits. Propagate 32 symbolic
    bit-rows (bitset over all free-bit columns + constant column U) through
    words 624..2T-1, collect equations, bitset Gaussian, require full rank,
    round-trip verify every observed double.
    """
    T = len(doubles)
    W = 2 * T
    ints = [int(round(d * (1 << 53))) for d in doubles]
    nfree = [5 if i % 2 == 0 else 6 for i in range(624)]
    col0 = [0] * 624
    s = 0
    for i in range(624):
        col0[i] = s
        s += nfree[i]
    U = s                      # = 3432 unknowns; column U = constant term
    one = 1 << U
    vm = [untemper(1 << m) for m in range(6)]
    rows = [None] * W
    for i in range(624):
        X = ints[i // 2]
        top = (X >> 26) << 5 if i % 2 == 0 else (X & ((1 << 26) - 1)) << 6
        w0 = untemper(top)
        r = []
        for k in range(32):
            v = one if (w0 >> k) & 1 else 0
            for m in range(nfree[i]):
                if (vm[m] >> k) & 1:
                    v ^= 1 << (col0[i] + m)
            r.append(v)
        rows[i] = r
    def twist_row(i):
        a, b, c = rows[i - 624], rows[i - 623], rows[i - 227]   # a31 | b30..0>>1, parity b0^R
        out = []
        for k in range(32):
            y = a[31] if k == 30 else (b[k + 1] if k <= 29 else 0)
            if (R >> k) & 1:
                y ^= b[0]
            out.append(c[k] ^ y)
        return out
    def temper_sym(r):
        r = [r[k] ^ (r[k + 11] if k + 11 < 32 else 0) for k in range(32)]
        r = [(r[k] ^ (r[k - 7] if k >= 7 else 0)) if (0x9d2c5680 >> k) & 1 else r[k] for k in range(32)]
        r = [(r[k] ^ (r[k - 15] if k >= 15 else 0)) if (0xefc60000 >> k) & 1 else r[k] for k in range(32)]
        r = [r[k] ^ (r[k + 18] if k + 18 < 32 else 0) for k in range(32)]
        return r
    piv = {}
    def push(eq):
        while True:
            d = eq & (one - 1)          # variable columns only
            if not d:
                return (eq & one) == 0  # pure constant row must be 0
            c = d.bit_length() - 1
            p = piv.get(c)
            if p is None:
                piv[c] = eq
                return True
            eq ^= p
    for i in range(624, W):
        rows[i] = twist_row(i)
        t = temper_sym(rows[i])
        X = ints[i // 2]
        if i % 2 == 0:
            top, lo = (X >> 26) << 5, 5
        else:
            top, lo = (X & ((1 << 26) - 1)) << 6, 6
        for k in range(lo, 32):
            if not push(t[k] ^ (((top >> k) & 1) << U)):
                return None
    free = [c for c in range(U) if c not in piv]
    if free:
        # Known leak: the in-place twist reads w_{j-624} only via its bit 31, and
        # w_0 is never used as the b-operand (that needs j=623, already observed),
        # so low31(w_0) appears in NO future equation: exactly the kernel of the
        # observed system (and it cannot move w_0 bit31, which IS constrained by
        # the w_624 equation), so all future predictions are kernel-invariant.
        if any(c >= nfree[0] for c in free):
            print(f'  crack: rank {len(piv)}/{U}, {len(free)} free cols beyond w0'
                  ' -> need more doubles', flush=True)
            return None
        print(f'  crack: rank {len(piv)}/{U}, free = low bits of w0 '
              '(provably irrelevant to future words)', flush=True)
    g = [0] * U
    for c in sorted(piv):             # ascending: pivot row bits are all < c
        row = piv[c]
        x = (row >> U) & 1
        d = row & (one - 1)
        while d:
            lsb = d & -d
            x ^= g[lsb.bit_length() - 1]
            d ^= lsb
        g[c] = x
    state = []
    for i in range(624):
        X = ints[i // 2]
        top = (X >> 26) << 5 if i % 2 == 0 else (X & ((1 << 26) - 1)) << 6
        w = untemper(top)
        for m in range(nfree[i]):
            if g[col0[i] + m]:
                w ^= vm[m]
        state.append(w)
    ws = state[:]
    for i in range(624, W):
        ws.append(mt_next(ws, i))
    for j in range(T):                # round-trip verify every observed double
        X = ints[j]
        if (temper(ws[2 * j]) >> 5) != (X >> 26):
            return None
        if (temper(ws[2 * j + 1]) >> 6) != (X & ((1 << 26) - 1)):
            return None
    return state

class Stream:
    def __init__(self, state, words_consumed):
        self.ws = state[:]
        self.pos = words_consumed
        self.v = []
        for i in range(624, words_consumed):   # materialize skipped words
            self.ws.append(mt_next(self.ws, i))
    def ensure(self, n):
        while len(self.v) < n:
            for _ in range(2048):
                i = self.pos
                w1 = self.ws[i] if i < 624 else (self.ws.append(mt_next(self.ws, i)) or self.ws[-1])
                self.pos += 1
                i = self.pos
                w2 = self.ws[i] if i < 624 else (self.ws.append(mt_next(self.ws, i)) or self.ws[-1])
                self.pos += 1
                self.v.append(((temper(w1) >> 5) * 67108864 + (temper(w2) >> 6)) / float(1 << 53))

# ---------- game client (works for net + sim) ----------
THRESH = 0.55

MAXJ = 12

def opts_from(v, k, s0, maxj=MAXJ):
    """Legal continuations from a prompt state: next draw index k, total s0.
    Returns list indexed by j (number of hits to take now): (newpos, win)."""
    res = []
    ss, k2 = s0, k
    for j in range(maxj + 1):
        p2, c = 0.0, 0
        while p2 <= ss:
            p2 += v[k2 + c]
            c += 1
        res.append((k2 + c, p2 >= 1.0))
        if k2 >= len(v) - 2 or ss + v[k2] >= 1.0:
            break
        ss += v[k2]
        k2 += 1
    return res

def dp_plan(v, starts, R, maxj=MAXJ):
    """Forward DP over (future round, stream pos) maximizing total wins.
    starts: dict pos -> wins-so-far (pos = index of that round's first draw,
    already consumed, so its total is v[pos] and the next unconsumed draw is
    pos+1). R = number of FUTURE rounds after the current one.
    Returns (WIN, PAR) tables or None if the window overflows."""
    WIN, PAR = [], []
    cur = dict(starts)
    for _ in range(R):
        nxt, par = {}, {}
        lim = len(v) - maxj - 40
        for p, w in cur.items():
            if p >= lim:
                continue
            for j, (np_, win) in enumerate(opts_from(v, p + 1, v[p], maxj)):
                val = w + (1 if win else 0)
                if nxt.get(np_, -1) < val:
                    nxt[np_] = val
                    par[np_] = (p, j, win)
        if not nxt:
            return None
        WIN.append(nxt)
        PAR.append(par)
        cur = nxt
    return WIN, PAR

def plan_actions(v, cur_k, cur_s, R, maxj=MAXJ):
    """Full plan from a mid-round crack state: returns (j0, [j1..jR]) or None.
    cur_k: next unconsumed double; cur_s: player total now; R: future rounds."""
    o0 = opts_from(v, cur_k, cur_s, maxj)
    starts = {}
    best_j0 = {}
    for j, (np_, win) in enumerate(o0):
        if np_ >= len(v) - maxj - 40:
            continue
        w = 1 if win else 0
        if w >= starts.get(np_, -1):
            starts[np_] = w
            best_j0[np_] = j
    if not starts:
        return None
    if R == 0:
        j0 = max(starts, key=lambda p: starts[p])
        return best_j0[j0], []
    r = dp_plan(v, starts, R, maxj)
    if r is None:
        return None
    WIN, PAR = r
    p = max(WIN[-1], key=lambda q: WIN[-1][q])
    path = []
    for i in range(R - 1, -1, -1):
        ppos, j, win = PAR[i][p]
        path.append(j)
        p = ppos
    path.reverse()
    return best_j0[p], path

def dealer_bust_at(st, k, p1):
    p2 = 0.0
    c = 0
    while p2 <= p1:
        p2 += st[k + c]
        c += 1
    return p2 >= 1.0

class Client:
    def __init__(self):
        self.obs = []          # all doubles seen, in stream order
        self.p1 = 0.0
        self.off = 0           # == len(obs)
        self.base = 0          # stream.v[0] corresponds to obs index base
        self.stream = None
        self.flag = None
        self.crack_at = 630    # theoretical min: word 623's free bits enter eq at j=1247
        self.desync = False
        self.rounds = 0        # 'Round ' lines seen
        self.new_round = False
        self.plan = None       # list of j for future rounds
        self.plan_idx = 0
        self.hits_left = None
    def maybe_crack(self):
        if self.stream is None and len(self.obs) >= self.crack_at:
            t0 = time.time()
            state = recover(self.obs)
            print(f'  crack attempt at {len(self.obs)} doubles -> '
                  f'{"OK" if state else "FAIL"} ({time.time()-t0:.1f}s)', flush=True)
            if state:
                self.base = len(self.obs)
                self.stream = Stream(state, 2 * len(self.obs))
                self.stream.ensure(60000)
                R = 1337 - self.rounds
                res = plan_actions(self.stream.v, self.off - self.base, self.p1, R)
                if res is not None:
                    j0, self.plan = res
                    self.hits_left = j0
                    self.plan_idx = 0
                    print(f'  plan ready for {R} future rounds; current round j0={j0}',
                          flush=True)
                else:
                    print('  plan overflow -> falling back to per-round greedy',
                          flush=True)
            else:
                self.crack_at = len(self.obs) + 70
    def win_at(self, k, s, left=6):
        """Can the player force a win knowing the whole future? k is index into
        stream.v (relative), s current total. Stand wins iff dealer busts."""
        if dealer_bust_at(self.stream.v, k, s):
            return True
        if left and s + self.stream.v[k] < 1.0:
            return self.win_at(k + 1, s + self.stream.v[k], left - 1)
        return False
    def handle_line(self, line):
        if self.flag or self.desync:
            return
        if line.startswith('Here is your flag:'):
            self.flag = line.split(':', 1)[1].strip()
            return
        if line.startswith('Round '):
            self.p1 = 0.0
            self.rounds += 1
            self.new_round = True
            return
        m = DRAW_RE.search(line)
        if not m:
            return
        v = float(m.group(1))
        if self.stream is not None:
            self.stream.ensure(self.off - self.base + 200)
            if self.v_at(self.off) != v:
                self.desync = True
                print(f'  DESYNC at {self.off}: predicted {self.v_at(self.off)!r} got {v!r}', flush=True)
        self.obs.append(v)
        if line.startswith('You draw'):
            self.p1 += v
        self.off += 1
    def v_at(self, i):
        return self.stream.v[i - self.base]
    def handle_prompt(self):
        self.maybe_crack()
        if self.stream is None:
            return 's' if self.p1 >= THRESH else 'h'
        if self.new_round:
            self.new_round = False
            if (self.hits_left is None and self.plan is not None
                    and self.plan_idx < len(self.plan)):
                self.hits_left = self.plan[self.plan_idx]
                self.plan_idx += 1
        st = self.stream.v
        rel = self.off - self.base
        s = self.p1
        if self.hits_left is not None:
            if self.hits_left > 0:
                self.hits_left -= 1
                if s + st[rel] < 1.0:
                    return 'h'
                # plan busts?? desync guard would have fired; stand instead
            self.hits_left = None
            return 's'
        if dealer_bust_at(st, rel, s):
            return 's'                       # fallback: standing now already wins
        if s + st[rel] < 1.0 and self.win_at(rel + 1, s + st[rel]):
            return 'h'                       # fallback: some future stop wins
        return 's'                           # dead round: stop bleeding draws

# ---------- local simulator ----------
def run_local(seed=4242):
    rng = random.Random(seed)
    c = Client()
    scores = [0, 0]
    for i in range(1337):
        c.handle_line(f'Round {i+1}:')
        p1 = 0.0
        bust = False
        while True:
            d = rng.random()
            p1 += d
            c.handle_line(f'You draw a [{d}]. (p1 = {p1})')
            if p1 >= 1:
                c.handle_line('You have gone bust. Dealer wins!')
                bust = True
                break
            a = c.handle_prompt()
            if a.lower() in ('s', 'stand'):
                break
        if not bust:
            p2 = 0.0
            while p2 <= p1:
                d = rng.random()
                p2 += d
                c.handle_line(f'Dealer draws a [{d}]. (p2 = {p2})')
            if p2 >= 1:
                scores[0] += 1
                c.handle_line('Dealer has gone bust. You win!')
            else:
                scores[1] += 1
                c.handle_line('Dealer has a higher total. Dealer wins!')
        else:
            scores[1] += 1
        c.handle_line(f'Score: {scores[0]}-{scores[1]}')
        c.handle_line('-' * 80)
        if c.desync or c.flag:
            break
        if scores[0] >= 800:
            c.handle_line('Here is your flag: crypto{SIMULATED_LOCAL_TEST}')
            break
    print(f'local: rounds~{i+1} score {scores[0]}-{scores[1]} '
          f'desync={c.desync} flag={c.flag}', flush=True)
    return c.flag is not None and not c.desync

# ---------- network ----------
class Net:
    def __init__(self, host, port):
        self.s = socket.create_connection((host, port), timeout=30)
        self.s.settimeout(60)
        self.buf = b''
    def events(self):
        while True:
            while True:
                nl = self.buf.find(b'\n')
                if nl < 0:
                    break
                line = self.buf[:nl].decode(errors='replace')
                self.buf = self.buf[nl + 1:]
                yield ('line', line)
            if self.buf.endswith(PROMPT.encode()):
                self.buf = self.buf[:-len(PROMPT)]
                yield ('prompt', None)
            data = self.s.recv(4096)
            if not data:
                self.buf = self.buf.decode(errors='replace')
                if self.buf:
                    yield ('line', self.buf)
                return
            self.buf += data
    def send(self, s):
        self.s.sendall(s.encode())

def run_net(attempt=0):
    net = Net('archive.cryptohack.org', 59737)
    c = Client()
    t0 = time.time()
    last = ''
    nsc = 0
    try:
        for kind, payload in net.events():
            if kind == 'line':
                last = payload
                if payload.startswith('Score:'):
                    nsc += 1
                    if nsc % 100 == 0:
                        print(f'  r{nsc}: {payload}', flush=True)
                c.handle_line(payload)
                if payload.startswith('Better luck') or c.flag:
                    print(f'ATT {attempt} LAST:',
                          payload if not c.flag else f'FLAG: {c.flag}', flush=True)
                    if c.flag:
                        open('flag_probability-seetf2022.txt', 'w').write(c.flag + '\n')
                    break
            else:
                a = c.handle_prompt()
                net.send(a + '\n')
                if c.desync:
                    print('DESYNC -> abort', flush=True)
                    break
                if time.time() - t0 > 3000:
                    print('TIMEOUT after %ds' % (time.time() - t0), flush=True)
                    break
    finally:
        try:
            net.s.close()
        except Exception:
            pass
    print(f'ATT {attempt} done. rounds={nsc} last="{last}" desync={c.desync} '
          f'flag={c.flag}', flush=True)
    return c.flag

if __name__ == '__main__':
    if '--net' in sys.argv:
        run_net()
    else:
        ok = run_local()
        sys.exit(0 if ok else 1)
