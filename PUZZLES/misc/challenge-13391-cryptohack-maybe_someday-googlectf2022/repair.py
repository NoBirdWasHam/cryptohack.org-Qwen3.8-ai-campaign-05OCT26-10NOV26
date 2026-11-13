# Repair loop: targeted t values to break remaining collision classes.
import hashlib, json, random, time, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
t0 = time.time()
M = 1 << 1024
D = json.load(open(os.path.join(HERE,'design3.json')))
QS = [(int(K), int(t)) for K, t in D['qs']]
strs = [hashlib.sha512(i.to_bytes(2,'big')).hexdigest() for i in range(65536)]
blob = b''.join(s.encode() for s in strs)
S_bytes = np.frombuffer(blob, dtype=np.uint8).reshape(65536,128).copy()
S16 = S_bytes.view('>u8')
Sints = [int.from_bytes(blob[i*128:(i+1)*128],'big') for i in range(65536)]

def col_of(K, t):
    tb = np.frombuffer(t.to_bytes(128,'big'), dtype=np.uint8) if t else np.zeros(128, dtype=np.uint8)
    out = np.empty_like(S_bytes); borrow = np.zeros(65536, dtype=np.int16)
    for i in range(127,-1,-1):
        d = S_bytes[:,i].astype(np.int16) - int(tb[i]) - borrow
        borrow = (d < 0).astype(np.int16); out[:,i] = (d & 0xFF)
    h = (out == 0).any(1)
    if K == 0 or K == 255:
        tlim = np.frombuffer(t.to_bytes(128,'big') if t else b'\0'*128, dtype='>u8')
        gt = np.zeros(65536, dtype=bool); eq = np.ones(65536, dtype=bool)
        for k in range(16):
            gt |= eq & (S16[:,k] > tlim[k]); eq &= (S16[:,k] == tlim[k])
        ge = gt | eq
        return (ge | h) if K == 0 else (~ge | h)
    return h.astype(np.uint8)

cols = [col_of(K, t) for K, t in QS]
def pack():
    p = np.zeros(65536, dtype=np.uint64)
    for j in range(20):
        p |= cols[j].astype(np.uint64) << np.uint64(j)
    return p
def score():
    u, cnt = np.unique(pack(), return_counts=True)
    return int((cnt*(cnt-1)//2).sum()), cnt

random.seed(3)
pairs, cnt = score()
print('start pairs', pairs, flush=True)
TIMECAP = 1500
while pairs > 0 and time.time()-t0 < TIMECAP:
    # collision classes
    u, inv = np.unique(pack(), return_inverse=True)[:2]
    members = {}
    for i in range(65536):
        members.setdefault(int(inv[i]), []).append(i)
    big = sorted([v for v in members.values() if len(v) > 1], key=len, reverse=True)
    # targeted t candidates from up to 40 biggest classes
    targs = []
    for cl in big[:40]:
        for i in cl:
            S = Sints[i]
            targs.append(S)
            targs.append((S + random.randrange(2**50)) % M)
            targs.append((S - random.randrange(2**50)) % M)
            targs.append((S + (random.randrange(1<<16) << random.randrange(0,100)*8)) % M)
    improved = False
    random.shuffle(targs)
    for (slot, K) in [(s, random.choice([9,9,9,0,255])) for s in range(20)]:
        for t in targs[:300]:
            keep = cols[slot]; new = col_of(K, t)
            cols[slot] = new
            p2, _ = score()
            if p2 < pairs:
                pairs = p2; QS[slot] = (K, t)
                print('repair slot', slot, 'K', K, 'pairs->', p2, '%.0fs' % (time.time()-t0), flush=True)
                improved = True
                break
            cols[slot] = keep
        if improved: break
    if not improved:
        print('repair stuck at pairs', pairs, flush=True); break
pairs2, cnt = score()
print('FINAL pairs', pairs2, '%.0fs' % (time.time()-t0), flush=True)
pat = pack(); table = {}; seen = {}; dups = 0
for i in range(65536):
    k = int(pat[i]); seen[k] = seen.get(k, 0) + 1
dupset = {k for k, c in seen.items() if c > 1}
for i in range(65536):
    k = int(pat[i])
    if k in dupset: dups += 1; continue
    table[k] = strs[i]
json.dump({'qs': [[K, str(t)] for K, t in QS], 'pairs': pairs2, 'table': table, 'dup': sorted(dupset)},
          open(os.path.join(HERE,'design4.json'),'w'))
print('saved design4.json table', len(table), 'dup-cands', dups, flush=True)
