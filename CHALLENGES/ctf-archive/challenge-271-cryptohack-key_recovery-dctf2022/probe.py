import os, itertools
import solve3 as s
K = os.urandom(16)
ks = s.key_schedule(K); k0,k1,k2,k3 = ks
sets = s.choose_sets()
data = {}
for i in sets:
    pts = [bytes([a if j == i else 0 for j in range(16)]) for a in range(256)]
    data[i] = (pts, [s.enc(K,p) for p in pts])
W3 = {i: [bytes(s.S_inv[c] for c in ct) for ct in data[i][1]] for i in sets}
W2 = {i: [bytes(s.S_inv[v] for v in s.per_inv(bytes([s.S_inv[c ^ k3[j]] for j,c in enumerate(ct)])))
          for ct in data[i][1]] for i in sets}
W1 = {i: [bytes(s.S_inv[v] for v in s.per_inv(bytes([a ^ k2[j] for j,a in enumerate(W2b)])))
          for W2b in W2[i]] for i in sets}

def test_counts(sample_fn, pairs_fn, g_full=True):
    """for a set, for each (b,w): count passing g under various predicates."""
    stats = {}
    for i in sets[:6]:
        for (b, w) in pairs_fn(i):
            samples = sample_fn(i)
            for pred in ["conf","size16","hi1","lo1","size1"]:
                cnt = []; tr = None
                for g in range(256):
                    vals = set()
                    for sx in samples:
                        blk = sx[:b] + bytes([sx[b]^g]) + sx[b+1:]
                        vals.add(blk[w])
                        if len(vals) > 17: break
                    if pred=="conf": okk = s._confined(vals) and len(vals)>=3
                    elif pred=="size16": okk = len(vals)==16
                    elif pred=="hi1": okk = len({v>>4 for v in vals})==1 and len(vals)>=3
                    elif pred=="lo1": okk = len({v&15 for v in vals})==1 and len(vals)>=3
                    else: okk = len(vals)==1
                    if okk:
                        cnt.append(g)
                    if g == sample_fn.key[b]: tr = (len(vals), sorted({v>>4 for v in vals}), sorted({v&15 for v in vals}))
                stats.setdefault(pred, []).append((i,b,len(cnt),tr))
    return stats

# stage k3: samples W3 (=z3^k3): guess shifts at z3; inner confined?
W3.key = k3
W2.key = k2
pairs3 = lambda i: [(b,w) for b,w,kind in s.testable(i,3)]
pairs2 = lambda i: [(b,w) for b,w,kind in s.testable(i,2)]
st3 = test_counts(W3, pairs3)
st2 = test_counts(W2, pairs2)
for nm, st in [("k3", st3), ("k2", st2)]:
    for pred, lst in st.items():
        tc = [t for t in lst if True]
        n_true_pass = sum(1 for (i,b,c,_) in lst)  # cnt includes true? check tr sizes
        print(nm, pred, "tests:", [(b,c,tr is not None) for (i,b,c,tr) in lst][:8])
