import os
import solve3 as s
K = os.urandom(16)
k0,k1,k2,k3 = s.key_schedule(K)
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
INV = s.S_inv; PINV = s.per_inv

def confined(vals):
    return len({v>>4 for v in vals})==1 or len({v&15 for v in vals})==1

def broken(vals):
    return len(vals) >= 3 and not confined(vals)

# predicate f(g, samples, b, w) -> pass?, samples: list of exact layer blocks
def mk(kind):
    if kind == "self":   # confined(blk[b])
        return lambda blk,w: confined(blk[b:w[0]+1]) and False if False else None
    return None

def count(kind, samples, b, w, pts=None):
    passing = []
    for g in range(256):
        good = True
        vals = set()
        for idx, blk0 in enumerate(samples):
            blk = blk0[:b] + bytes([blk0[b]^g]) + blk0[b+1:]
            if kind == "self":
                t = blk[b]
            elif kind == "u":            # confined(per_inv(blk)[w])
                t = PINV(blk)[w]
            elif kind == "Sinv_u":       # confined(S_inv[per_inv(blk)[w]])
                t = INV[PINV(blk)[w]]
            elif kind == "Sinv_b":
                t = INV[PINV(blk)[b]]
            elif kind == "k0c":          # candidate k0[i] constant
                vals.add(pts[idx][w] ^ INV[PINV(blk)[w]])
                continue
            vals.add(t)
            if kind in ("self","u","Sinv_u","Sinv_b") and not confined(vals):
                good = False; break
        if kind == "k0c":
            good = len(vals) == 1
        if good:
            passing.append(g)
    return passing[:20], len(passing)

print("stage k3 (guess z3 byte b):")
for i in sets[:5]:
    for (b,w,kindt) in s.testable(i,3):
        r = {k: count(k, W3[i], b, w, data[i][0]) for k in ("self","u","Sinv_u","Sinv_b")}
        print(" i",i,"b",b,"w",w,"true k3[b]",k3[b],r)
print("stage k2 (guess z2 byte b):")
for i in sets[:5]:
    for (b,w,kindt) in s.testable(i,2):
        r = {k: count(k, W2[i], b, w, data[i][0]) for k in ("self","u","Sinv_u","Sinv_b")}
        print(" i",i,"b",b,"w",w,"true k2[b]",k2[b],r)
print("stage k1 (guess z1 byte b, partner i):")
for i in sets[:5]:
    for (b,iact,kindt) in s.testable(i,1):
        r = {k: count(k, W1[i], b, iact, data[i][0]) for k in ("self","u","Sinv_u","Sinv_b","k0c")}
        print(" i",i,"b",b,"true k1[b]",k1[b],r)
