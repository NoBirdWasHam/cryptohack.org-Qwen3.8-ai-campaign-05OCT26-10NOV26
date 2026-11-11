#!/usr/bin/env python3
"""Core break of one_round_crypto: C = M3 * sigma * M1.

Enabling weakness (verified): every column of M1 (and M3) has byte-support
exactly 9/16, key-independent. Hence for a single-bit plaintext difference
d = M1*e, the ciphertext difference sigma(x)^sigma(x^d) has the same byte
support (a byte difference is 0 iff d_j=0, the additive S-box key cancels
nothing but preserves zeros), so pairs (P, P^bit) give data spanning
V = M3(9-byte space), dim 72. Nullspace W = M3^-T(complement), dim 56.
Intersections of the 16 W_i give dim-8 atoms A_j = M3^-T(B_j).

Decryption without knowing sigma:
  Phi_j(P) := (parity(u_t & f(P)))_t for atom basis u = gamma(sigma_j(l_j(P)))
  with l_j = byte-j row map of M1. Fibers of Phi_j are affine cosets of a
  dim-120 kernel. Challenge C: v_j = Phi-value of C; observed data gives a
  rep r_j(v_j) and kernel => 8 linear equations P^r in K_j. 16 atoms =>
  unique P. Unknown bijection gamma absorbed by fiber membership.
"""

def parity(x):
    return bin(x).count('1') & 1

def fr(b):
    return int.from_bytes(b, 'big')

def rref(vecs):
    piv = {}
    for v in vecs:
        x = v
        while x:
            b = x.bit_length() - 1
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    return list(piv.values())

def nullspace_basis(vecs, n=128):
    piv = {}
    for v in vecs:
        x = v
        while x:
            b = x.bit_length() - 1
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    free = [b for b in range(n) if b not in piv]
    piv2 = dict(piv)
    for b in sorted(piv2, reverse=True):
        for b2 in list(piv2):
            if b != b2 and (piv2[b2] >> b) & 1: piv2[b2] ^= piv2[b]
    ns = []
    for f in free:
        u = 1 << f
        for b, r in piv2.items():
            if (r >> f) & 1: u ^= (1 << b)
        ns.append(u)
    return ns

def inter(basisA, basisB):
    """span(basisA) ∩ span(basisB) via annihilators: (A^perp + B^perp)^perp."""
    return nullspace_basis(nullspace_basis(basisA) + nullspace_basis(basisB))

def canon(basis):
    piv = {}
    for v in basis:
        x = v
        while x:
            b = x.bit_length() - 1
            if b in piv: x ^= piv[b]
            else: piv[b] = x; break
    for b in sorted(piv, reverse=True):
        for b2 in list(piv):
            if b != b2 and (piv[b2] >> b) & 1: piv[b2] ^= piv[b]
    return tuple(sorted(piv.values()))

def find_atoms(Ws):
    from collections import deque
    seen = {}
    atoms = {}
    q = deque()
    for i, W in enumerate(Ws):
        c = canon(W)
        if c not in seen:
            seen[c] = W; q.append((1 << i, W))
    while q:
        key, basis = q.popleft()
        d = len(basis)
        if d == 8:
            atoms[canon(basis)] = basis
            continue
        if d < 8:
            continue
        for k in range(len(Ws)):
            if (key >> k) & 1: continue
            nb = inter(basis, Ws[k])
            if len(nb) < 8: continue
            c = canon(nb)
            if c in seen: continue
            seen[c] = nb; q.append((key | (1 << k), nb))
    return list(atoms.values())

def solve_linear(eqs):
    """eqs: list of (mask, rhs). Returns solution mask or None."""
    piv = {}
    for m, b in eqs:
        x, y = m, b
        while x:
            k = x.bit_length() - 1
            if k in piv:
                pm, pb = piv[k]; x ^= pm; y ^= pb
            else:
                piv[k] = (x, y); break
        else:
            if y: return None
    if len(piv) < 128:
        return None  # underdetermined
    # pivot row for k has leading bit k: P_k = rhs ^ sum(lower bits of row . sol)
    sol = 0
    for k in sorted(piv):
        m, b = piv[k]
        lo = m & ((1 << k) - 1)
        cc = parity(lo & sol)
        if b ^ cc: sol |= 1 << k
    return sol

class Decryptor:
    def __init__(self, pblocks, cblocks, T, nb=16, nbits=128):
        pint = [fr(b) for b in pblocks]
        cint = [fr(b) for b in cblocks]
        self.dims = []
        Ws = []
        for k in range(nbits):
            diffs = []
            for t in range(T):
                i0 = 2 * (k * T + t); i1 = i0 + 1
                diffs.append(cint[i0] ^ cint[i1])
            V = rref(diffs)
            self.dims.append(len(V))
            Ws.append(nullspace_basis(V))
        # atoms: dim-8 subspaces of the intersection lattice.
        seen = set()
        uniq = []
        for W in Ws:
            c = canon(W)
            if c not in seen:
                seen.add(c); uniq.append(W)
        self.n_uniq = len(uniq)
        atoms = {}
        # pairwise first (fast, and the common case)
        import itertools as _it
        for a, b in _it.combinations(range(len(uniq)), 2):
            nb = inter(uniq[a], uniq[b])
            if len(nb) == 8:
                atoms[canon(nb)] = nb
        if len(atoms) < nb:
            # BFS over higher-order intersections
            from collections import deque
            q = deque()
            vseen = set()
            for a in range(len(uniq)):
                c = canon(uniq[a])
                if c not in vseen:
                    vseen.add(c); q.append(uniq[a])
            while q:
                basis = q.popleft()
                if len(basis) == 8:
                    atoms[canon(basis)] = basis
                    continue
                if len(basis) < 8:
                    continue
                for W in uniq:
                    nb2 = inter(basis, W)
                    if 8 <= len(nb2) < len(basis):
                        c = canon(nb2)
                        if c not in vseen:
                            vseen.add(c); q.append(nb2)
        if len(atoms) != nb:
            raise RuntimeError("atoms=%d uniq=%d dims=%s" % (len(atoms), len(uniq), sorted(set(self.dims))))
        self.n_atoms = len(atoms)
        self.atoms = atoms
        self.tables = []   # per atom: (basis, fiberdict v->[rep, pivdict, list])
        for basis in atoms:
            tab = {}
            for p, c in zip(pint, cint):
                v = 0
                for t, u in enumerate(basis):
                    if parity(u & c): v |= 1 << t
                e = tab.get(v)
                if e is None:
                    tab[v] = [p, {}, []]
                else:
                    d = p ^ e[0]
                    x = d
                    while x:
                        b = x.bit_length() - 1
                        if b in e[1]: x ^= e[1][b]
                        else: e[1][b] = x; e[2].append(x); break
            # kernel span = union over fibers
            allspan = []
            for v, e in tab.items():
                allspan.extend(e[2])
            K = rref(allspan)
            lam = nullspace_basis(K)   # dim-8 row space of lambda_j
            self.tables.append((basis, tab, lam, len(K)))
        self.kernel_dims = [t[3] for t in self.tables]

    def decrypt(self, cbytes):
        c = fr(cbytes)
        eqs = []
        for basis, tab, lam, _ in self.tables:
            v = 0
            for t, u in enumerate(basis):
                if parity(u & c): v |= 1 << t
            e = tab.get(v)
            if e is None:
                return None
            r = e[0]
            for l in lam:
                eqs.append((l, parity(l & r)))
        sol = solve_linear(eqs)
        if sol is None:
            return None
        return sol.to_bytes(16, 'big')

def build_message(T=80, nbits=128, extra=256, rng=None):
    rng = rng or __import__('random').Random()
    pblocks = []
    for b in range(nbits):
        for t in range(T):
            R = rng.getrandbits(128)
            pblocks.append(R.to_bytes(16, 'big'))
            pblocks.append((R ^ (1 << b)).to_bytes(16, 'big'))
    for _ in range(extra):
        pblocks.append(rng.getrandbits(128).to_bytes(16, 'big'))
    return pblocks
