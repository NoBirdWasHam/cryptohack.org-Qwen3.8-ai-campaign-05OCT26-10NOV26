# xp by bit-lifting (Hensel over Z/256) ; writes xp.json
from ast import literal_eval
A = literal_eval(open("u-turn/A.txt").read())
h = bytes.fromhex(open("u-turn/output.txt").read().strip())
k, l = 48, 50
A2 = [[a & 1 for a in row] for row in A]

# gaussian elimination mod 2 with free vars; return one solution u for rhs
import itertools
piv = [-1] * l
used = [False] * k
rows = [r[:] for r in A2]
order = []
for col in range(l):
    found = -1
    for r in range(k):
        if rows[r][col] == 1 and not used[r]:
            found = r
            break
    if found == -1:
        continue
    used[found] = True
    piv[col] = found
    order.append(col)
    for r in range(k):
        if r != found and rows[r][col] == 1:
            rows[r] = [a ^ b for a, b in zip(rows[r], rows[found])]

def rref(M, nrows, ncols):
    M = [row[:] for row in M]
    piv = {}
    r = 0
    for col in range(ncols):
        sel = next((i for i in range(r, nrows) if M[i][col]), -1)
        if sel < 0:
            continue
        M[r], M[sel] = M[sel], M[r]
        for i in range(nrows):
            if i != r and M[i][col]:
                M[i] = [a ^ b for a, b in zip(M[i], M[r])]
        piv[col] = r
        r += 1
    return M, piv, r

def all_solutions(rhs):
    M = [A2[i][:] + [rhs[i]] for i in range(k)]
    M, piv, r = rref(M, k, l)
    for i in range(r, k):
        if M[i][l]:
            return []
    free = [c for c in range(l) if c not in piv]
    base = [0] * l
    for col, rr in piv.items():
        base[col] = M[rr][l]
    out = []
    for mask in range(1 << len(free)):
        u = base[:]
        for bi, fc in enumerate(free):
            if mask >> bi & 1:
                u[fc] ^= 1
                # dependent pivots: row rr has u[piv] ^= M[rr][fc]
                for col, rr in piv.items():
                    if M[rr][fc]:
                        u[col] ^= 1
        out.append(u)
    return out

# DFS Hensel lift mod 2^8
x0 = [0] * l
stack = [x0]
sols = []
for j in range(7):
    newstack = []
    for part in stack:
        r = [h[i] - sum(A[i][t] * part[t] for t in range(l)) for i in range(k)]
        if any(v % (2 ** j) for v in r):
            continue
        rhs = [(v >> j) & 1 for v in r]
        for u in all_solutions(rhs):
            newstack.append([part[t] + (2 ** j) * u[t] for t in range(l)])
    stack = newstack
    print("level", j, "partials", len(stack), flush=True)
# final lift j=7: single solution u=particular (free=0); first consistent partial wins
sols = []
for part in stack:
    r = [h[i] - sum(A[i][t] * part[t] for t in range(l)) for i in range(k)]
    if any(v % 128 for v in r):
        continue
    rhs = [(v >> 7) & 1 for v in r]
    ss = all_solutions(rhs)
    if not ss:
        continue
    cand = [part[t] + 128 * ss[0][t] for t in range(l)]
    if all(sum(A[i][t] * cand[t] for t in range(l)) % 256 == h[i] for i in range(k)):
        sols.append(cand)
        break
assert sols
x0 = sols[0]
print("num full solutions mod256:", len(sols))
import json
json.dump(x0, open("xp.json", "w"))
print("xp ok, max", max(x0))
