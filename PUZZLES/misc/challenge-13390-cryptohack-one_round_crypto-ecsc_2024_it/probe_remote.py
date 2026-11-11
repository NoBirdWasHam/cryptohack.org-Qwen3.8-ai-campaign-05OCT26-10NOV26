#!/usr/bin/env python3
"""Probe remote structure: small message, cache response, analyze offline."""
import socket, sys, time, random, json
from attack_core import build_message, nullspace_basis, inter, canon, rref

HOST, PORT = 'archive.cryptohack.org', 62821
T = 40

def payload(line):
    s = line.decode(errors='replace').strip()
    if s.startswith('>'): s = s[1:].strip()
    if not s or set(s) == {'='}: return None
    return s

def main():
    t0 = time.time()
    rng = random.Random()
    pblocks = build_message(T=T, extra=256, rng=rng)
    msg = ''.join(b.hex() for b in pblocks).encode()
    print("blocks", len(pblocks), flush=True)
    sock = socket.create_connection((HOST, PORT), timeout=180)
    rf = sock.makefile('rb')
    sock.sendall(msg + b"\n")
    line = rf.readline()
    big = payload(line)
    print("response %.1fs len %d" % (time.time()-t0, len(big)), flush=True)
    json.dump({'T': T, 'p': [b.hex() for b in pblocks],
               'c': [big[32*i:32*i+32] for i in range(len(pblocks))]},
              open('probe_cache.json', 'w'))
    # don't continue game; analyze now
    sock.close()
    analyze(pblocks, [bytes.fromhex(big[32*i:32*i+32]) for i in range(len(pblocks))])

def analyze(pblocks, cblocks, T=T):
    pint = [int.from_bytes(b, 'big') for b in pblocks]
    cint = [int.from_bytes(b, 'big') for b in cblocks]
    Ws = []
    dims = []
    for k in range(128):
        diffs = []
        for t in range(T):
            i0 = 2*(k*T+t); i1 = i0+1
            diffs.append(cint[i0] ^ cint[i1])
        V = rref(diffs)
        dims.append(len(V))
        Ws.append(nullspace_basis(V))
    from collections import Counter
    print('V dims:', Counter(dims))
    seen = set(); uniq = []
    for W in Ws:
        c = canon(W)
        if c not in seen:
            seen.add(c); uniq.append(W)
    print('uniq W:', len(uniq), 'Wdims:', Counter(len(w) for w in uniq))
    import itertools
    idim = Counter()
    atoms8 = {}
    for a, b in itertools.combinations(range(len(uniq)), 2):
        d = len(inter(uniq[a], uniq[b]))
        idim[d] += 1
        if d == 8: atoms8[canon(uniq[a] and uniq[a])] = 0
    print('pairwise inter dims:', dict(sorted(idim.items())))
    # byte-alignment test: pick smallest-dim W; is it M3-free byte-aligned? test:
    # dim-8 spaces found at higher-order intersections?
    mind = min(len(w) for w in uniq)
    cur = [w for w in uniq if len(w) == mind][:3]
    for a in range(len(uniq)):
        for b in range(a+1, len(uniq)):
            I = inter(uniq[a], uniq[b])
            if 0 < len(I) <= 16:
                for c2 in range(len(uniq)):
                    J = inter(I, uniq[c2])
                    if 0 < len(J) < len(I):
                        pass
    # exhaustive: minimal nonzero intersections over triples
    print('time %.1f' % 0)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'offline':
        d = json.load(open('probe_cache.json'))
        T = d['T']
        analyze([bytes.fromhex(b) for b in d['p']], [bytes.fromhex(b) for b in d['c']], T)
    else:
        main()
