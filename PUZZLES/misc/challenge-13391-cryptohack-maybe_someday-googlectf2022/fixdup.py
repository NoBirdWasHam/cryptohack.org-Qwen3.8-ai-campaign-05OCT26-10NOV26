# Recompute collision pattern set for design3.json; rewrite with 'dup' + clean table.
import hashlib, json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE,'design3.json')))
QS = [(int(K), int(t)) for K, t in D['qs']]
strs = [hashlib.sha512(i.to_bytes(2,'big')).hexdigest() for i in range(65536)]
blob = b''.join(s.encode() for s in strs)
S_bytes = np.frombuffer(blob, dtype=np.uint8).reshape(65536,128).copy()
S16 = S_bytes.view('>u8')
def col_of(K, t):
    tb = np.frombuffer(t.to_bytes(128,'big'), dtype=np.uint8)
    out = np.empty_like(S_bytes); borrow = np.zeros(65536, dtype=np.int16)
    for i in range(127,-1,-1):
        d = S_bytes[:,i].astype(np.int16) - int(tb[i]) - borrow
        borrow = (d < 0).astype(np.int16); out[:,i] = (d & 0xFF)
    h = (out == 0).any(1)
    if K in (0, 255):
        tlim = np.frombuffer(t.to_bytes(128,'big'), dtype='>u8')
        gt = np.zeros(65536, dtype=bool); eq = np.ones(65536, dtype=bool)
        for k in range(16):
            gt |= eq & (S16[:,k] > tlim[k]); eq &= (S16[:,k] == tlim[k])
        ge = gt | eq
        return (ge | h) if K == 0 else (~ge | h)
    return h.astype(np.uint8)
pat = np.zeros(65536, dtype=np.uint64)
for j,(K,t) in enumerate(QS):
    pat |= col_of(K,t).astype(np.uint64) << np.uint64(j)
u, cnt = np.unique(pat, return_counts=True)
dupset = {int(x) for x, c in zip(u, cnt) if c > 1}
table = {}
ncoll = 0
for i in range(65536):
    k = int(pat[i])
    if k in dupset: ncoll += 1; continue
    table[k] = strs[i]
D['table'] = {str(k): v for k, v in table.items()}
D['dup'] = sorted(dupset)
json.dump(D, open(os.path.join(HERE,'design3.json'),'w'))
print('dup patterns', len(dupset), 'collision candidates', ncoll, 'table', len(table))
