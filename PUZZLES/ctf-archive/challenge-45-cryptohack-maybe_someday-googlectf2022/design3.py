# Collision-free 20-query design, CORRECTED model (1024-bit secret region).
# r(K=0)=ge|h ; r(K=255)=~ge|h ; r(mid)=h ; ge=[S>=t], h=haszero((S-t) mod 2^1024)
import hashlib, json, random, time, sys
import numpy as np

M = 1 << 1024
t0 = time.time()
strs = [hashlib.sha512(i.to_bytes(2,'big')).hexdigest() for i in range(65536)]
blob = b''.join(s.encode() for s in strs)
S_bytes = np.frombuffer(blob, dtype=np.uint8).reshape(65536,128).copy()
S16 = S_bytes.view('>u8')
Sints = [int.from_bytes(blob[i*128:(i+1)*128],'big') for i in range(65536)]
Ssort = sorted(Sints)
print('setup %.1fs' % (time.time()-t0), flush=True)

TB = np.frombuffer(t0.to_bytes(0,'big'), dtype=np.uint8) if False else None
def haszero_vec(t):
    tb = np.frombuffer(t.to_bytes(128,'big'), dtype=np.uint8)
    out = np.empty_like(S_bytes)
    borrow = np.zeros(65536, dtype=np.int16)
    for i in range(127,-1,-1):
        d = S_bytes[:,i].astype(np.int16) - int(tb[i]) - borrow
        borrow = (d < 0).astype(np.int16)
        out[:,i] = (d & 0xFF)
    return (out == 0).any(1)

def ge_vec(t):
    tlim = np.frombuffer(t.to_bytes(128,'big'), dtype='>u8')
    gt = np.zeros(65536, dtype=bool); eq = np.ones(65536, dtype=bool)
    for k in range(16):
        gt |= eq & (S16[:,k] > tlim[k])
        eq &= (S16[:,k] == tlim[k])
    return gt | eq

# ---- pool ----
random.seed(7)
pool = []   # (K, t)
qs = [int(65536*j/128) for j in range(1,128)]
for r in qs:
    t = Ssort[r]
    pool.append((0,t)); pool.append((255,t))
for _ in range(1150):
    pool.append((9, random.randrange(M)))
for _ in range(150):
    pool.append((9, (random.choice(Ssort) + random.randrange(2**160)) % M))
P = len(pool)
print('pool', P, flush=True)

cols = np.zeros((P,65536), dtype=np.uint8)
for idx,(K,t) in enumerate(pool):
    h = haszero_vec(t)
    if K == 0:   c = ge_vec(t) | h
    elif K == 255: c = ~ge_vec(t) | h
    else: c = h
    cols[idx] = c
    if idx % 400 == 0: print('pool col', idx, '%.0fs' % (time.time()-t0), flush=True)
print('cols done %.0fs' % (time.time()-t0), flush=True)

def pack(sel):
    p = np.zeros(65536, dtype=np.uint64)
    for j,q in enumerate(sel):
        p |= cols[q].astype(np.uint64) << np.uint64(j)
    return p
def score(sel):
    u,inv,cnt = np.unique(pack(sel), return_inverse=True, return_counts=True)
    pairs = int((cnt*(cnt-1)//2).sum())
    return pairs, inv, cnt

# ---- greedy: maximize pairs removed each step ----
sel = []
inv = np.zeros(65536, dtype=np.int64)  # all one class
for step in range(20):
    cnt_c = np.bincount(inv)
    n_c = cnt_c.astype(np.float64)
    best = None
    for q in range(P):
        if q in sel: continue
        q1 = cols[q]
        a = np.bincount(inv[q1==1], minlength=len(cnt_c)).astype(np.float64)
        gain = float((a*(n_c-a)).sum())
        if best is None or gain > best[0]: best = (gain, q)
    sel.append(best[1])
    pairs, inv, cnt = score(sel)
    print('greedy step', len(sel), 'pairs', pairs, '%.0fs' % (time.time()-t0), flush=True)

# ---- hill climb on total pairs ----
best_pairs = pairs
TIMECAP = 1500
epochs = 0
while best_pairs > 0 and time.time()-t0 < TIMECAP:
    improved = False
    for slot in range(20):
        cur = sel[slot]
        for q in range(P):
            if q == cur or q in sel: continue
            trial = sel[:]; trial[slot] = q
            p2,_,_ = score(trial)
            if p2 < best_pairs:
                best_pairs = p2; sel = trial; improved = True
                print('hc swap slot',slot,'-> pairs',p2, '%.0fs'%(time.time()-t0), flush=True)
                if best_pairs == 0: break
        if best_pairs == 0: break
    epochs += 1
    if not improved and best_pairs > 0:
        print('hc converged at pairs', best_pairs, flush=True); break
print('FINAL pairs', best_pairs, 'epochs', epochs, '%.0fs'%(time.time()-t0), flush=True)

pairs, inv, cnt = score(sel)
assert pairs == best_pairs
qs_out = [[pool[q][0], str(pool[q][1])] for q in sel]
pat = pack()
u, cnt = np.unique(pat, return_counts=True)
dupset = {int(x) for x, c in zip(u, cnt) if c > 1}
table = {}
dups = 0
for i in range(65536):
    k = int(pat[i])
    if k in dupset: dups += 1; continue
    table[k] = strs[i]
print('table size', len(table), 'dup-cands', dups, flush=True)
json.dump({'qs': qs_out, 'pairs': pairs, 'table': table, 'dup': sorted(dupset)}, open('design3.json','w'))
print('saved design3.json', flush=True)
