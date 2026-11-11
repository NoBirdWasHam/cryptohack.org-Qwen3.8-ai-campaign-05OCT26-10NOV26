#!/usr/bin/env python3
"""Coset-difference-pool attack for one_round_crypto.

M1/M3 columns are dense (15-16 byte support); a random plaintext difference
D has byte j of M1*D zero with prob ~2^-8; such differences give rank-120
ciphertext-difference spans whose nullspace is the dim-8 atom A_j.

To get many probes cheaply, the message is m cosets of a dim-7 subspace U:
for every coset pair (i,j) and every u in U, the difference delta =
s_i^s_j^u has 128 realizations x,x^delta inside the message at once.
~9k probes from 1536 blocks -> every byte's atom found w.h.p.

Fiber tables + lambda equations as in attack_core: blocks sharing an atom
Phi-value give kernel vectors; lam = K^perp (dim 8) gives 8 linear eqs on P.
"""
import itertools
from collections import deque
from attack_core import (parity, fr, rref, nullspace_basis, inter, canon,
                         solve_linear)


def build_message2(mcos=12, dim=7, extra=1536, rng=None):
    rng = rng or __import__('random').Random()
    us = [rng.getrandbits(128) for _ in range(dim)]
    comb = []
    for mask in range(1 << dim):
        v = 0
        for i in range(dim):
            if (mask >> i) & 1:
                v ^= us[i]
        comb.append(v)
    shifts = [0] + [rng.getrandbits(128) for _ in range(mcos - 1)]
    pblocks, index = [], {}
    for s in shifts:
        for cv in comb:
            v = s ^ cv
            index[v] = len(pblocks)
            pblocks.append(v.to_bytes(16, 'big'))
    probes = []
    for i, j in itertools.combinations(range(mcos), 2):
        off = shifts[i] ^ shifts[j]
        si = shifts[i]
        for cv in comb:
            pairs = [(index[si ^ c2], index[shifts[j] ^ c2 ^ cv])
                     for c2 in comb]
            probes.append((off ^ cv, pairs))
    for i in range(mcos):
        si = shifts[i]
        for cv in comb:
            if cv == 0:
                continue
            pairs = [(index[si ^ c2], index[si ^ c2 ^ cv]) for c2 in comb]
            probes.append((cv, pairs))
    for _ in range(extra):
        v = rng.getrandbits(128)
        while v in index:
            v = rng.getrandbits(128)
        pblocks.append(v.to_bytes(16, 'big'))
    return pblocks, probes


def rank_le_120(diffs):
    piv = {}
    for v in diffs:
        x = v
        while x:
            b = x.bit_length() - 1
            if b in piv:
                x ^= piv[b]
            else:
                piv[b] = x
                break
        if len(piv) > 120:
            return None
    return list(piv.values())


class Decryptor2:
    def __init__(self, pblocks, cblocks, probes, nb=16):
        pint = [fr(b) for b in pblocks]
        cint = [fr(b) for b in cblocks]
        Ws = []
        hitdims = []
        for delta, pairs in probes:
            V = rank_le_120([cint[a] ^ cint[b] for a, b in pairs])
            if V is None:
                continue
            W = nullspace_basis(V)
            hitdims.append(len(W))
            Ws.append(W)
        self.n_probes = len(probes)
        self.n_hits = len(Ws)
        self.hitdims = sorted(set(hitdims))
        seen, uniq = set(), []
        for W in Ws:
            c = canon(W)
            if c not in seen:
                seen.add(c)
                uniq.append(W)
        atoms = {}
        for W in uniq:
            if len(W) == 8:
                atoms[canon(W)] = W
        q = deque(uniq)
        vseen = set(canon(W) for W in uniq)
        while q and len(atoms) < nb:
            basis = q.popleft()
            if len(basis) <= 8:
                continue
            for W in uniq:
                nb2 = inter(basis, W)
                if 8 <= len(nb2) < len(basis):
                    c = canon(nb2)
                    if len(nb2) == 8:
                        atoms[c] = nb2
                    if c not in vseen:
                        vseen.add(c)
                        q.append(nb2)
        if len(atoms) < nb:
            raise RuntimeError("atoms=%d uniq=%d hits=%d dims=%s" %
                               (len(atoms), len(uniq), len(Ws), self.hitdims))
        self.n_atoms = nb
        self.atoms = atoms
        self.tables = []
        for basis in list(atoms.values())[:nb]:
            tab = {}
            for p, c in zip(pint, cint):
                v = 0
                for t, u in enumerate(basis):
                    if parity(u & c):
                        v |= 1 << t
                e = tab.get(v)
                if e is None:
                    tab[v] = [p, {}, []]
                else:
                    x = p ^ e[0]
                    while x:
                        b = x.bit_length() - 1
                        if b in e[1]:
                            x ^= e[1][b]
                        else:
                            e[1][b] = x
                            e[2].append(x)
                            break
            allspan = []
            for v, e in tab.items():
                allspan.extend(e[2])
            K = rref(allspan)
            lam = nullspace_basis(K)
            self.tables.append((basis, tab, lam, len(K)))
        self.kernel_dims = [t[3] for t in self.tables]

    def decrypt(self, cbytes, pad_byte=1):
        c = fr(cbytes)
        eqs = []
        for basis, tab, lam, _ in self.tables:
            v = 0
            for t, u in enumerate(basis):
                if parity(u & c):
                    v |= 1 << t
            e = tab.get(v)
            if e is None:
                return None
            r = e[0]
            for l in lam:
                eqs.append((l, parity(l & r)))
        sol = solve_linear(eqs)
        if sol is not None:
            return sol.to_bytes(16, 'big')
        # underdetermined: enumerate kernel, keep candidates with padding
        piv = {}
        rhs = {}
        for m, b in eqs:
            x, y = m, b
            while x:
                k = x.bit_length() - 1
                if k in piv:
                    x ^= piv[k]
                    y ^= rhs[k]
                else:
                    piv[k] = x
                    rhs[k] = y
                    break
        base = solve_linear(list(eqs)) if False else None
        # particular solution: set free bits 0, back-substitute pivots
        freeb = [b for b in range(128) if b not in piv]
        # ascending pivot back-sub with free bits = 0
        p0 = 0
        for k in sorted(piv):
            m = piv[k]
            lo = m & ((1 << k) - 1)
            cc = parity(lo & p0)
            if rhs[k] ^ cc:
                p0 |= 1 << k
        # free bits: verify p0 rows where pivot bit set use lower bits only;
        # free positions may appear in rows -> recompute: rows with leading
        # bit k depend only on bits < k, so if free bits < k they matter.
        def complete(sol_free):
            p = p0 ^ sol_free
            for k in sorted(piv):
                m = piv[k]
                lo = m & ((1 << k) - 1)
                cc = parity(lo & p)
                if rhs[k] ^ cc:
                    p |= 1 << k
                else:
                    p &= ~(1 << k)
            return p
        cands = []
        for combo in range(1 << len(freeb)):
            sf = 0
            for i, fb in enumerate(freeb):
                if (combo >> i) & 1:
                    sf |= 1 << fb
            p = complete(sf)
            if (p & 0xFF) == pad_byte:
                cands.append(p)
        if len(cands) == 1:
            return cands[0].to_bytes(16, 'big')
        if cands:
            return cands[0].to_bytes(16, 'big')
        return None
