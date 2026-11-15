#!/usr/bin/env python
"""Debug: verify GF(2) matrix arithmetic + group exponent of GL(50,2). Self-contained."""
import random
from math import gcd

N = 50

def mat_mul(A, B):
    Bcols = [sum((((B[i] >> (N - 1 - j)) & 1) << (N - 1 - i)) for i in range(N)) for j in range(N)]
    out = []
    for i in range(N):
        ai = A[i]
        row = 0
        for j in range(N):
            row = (row << 1) | ((ai & Bcols[j]).bit_count() & 1)
        out.append(row)
    return out

def mat_pow(A, e):
    result = [1 << (N - 1 - i) for i in range(N)]  # identity
    base = A[:]
    while e:
        if e & 1:
            result = mat_mul(base, result)
        base = mat_mul(base, base)
        e >>= 1
    return result

def naive_mul(A, B):
    C = [[0]*N for _ in range(N)]
    for i in range(N):
        for k in range(N):
            if A[i][k]:
                for j in range(N):
                    C[i][j] ^= B[k][j]
    return C

def rows_to_lists(rows):
    return [[(row >> (N-1-j)) & 1 for j in range(N)] for row in rows]

def lists_to_rows(m):
    return [sum(v << (N-1-j) for j, v in enumerate(row)) for row in m]

random.seed(1)
for trial in range(5):
    A = [random.getrandbits(N) for _ in range(N)]
    B = [random.getrandbits(N) for _ in range(N)]
    assert mat_mul(A, B) == lists_to_rows(naive_mul(rows_to_lists(A), rows_to_lists(B))), f"mul mismatch trial {trial}"
print("mat_mul OK (5/5 vs naive)")

A = [random.getrandbits(N) for _ in range(N)]
A_L = rows_to_lists(A)
I_L = [[int(i == j) for j in range(N)] for i in range(N)]
naive = I_L
for _ in range(137):
    naive = naive_mul(naive, A_L)
assert mat_pow(A, 137) == lists_to_rows(naive)
print("mat_pow OK (137 multiplications vs naive)")

def is_inv(rows):
    M = [r for r in rows]
    rank = 0
    for c in range(N):
        piv = None
        for r in range(rank, N):
            if (M[r] >> (N-1-c)) & 1:
                piv = r; break
        if piv is None: continue
        M[rank], M[piv] = M[piv], M[rank]
        for r in range(N):
            if r != rank and ((M[r] >> (N-1-c)) & 1):
                M[r] ^= M[rank]
        rank += 1
    return rank == N

L = 1
for i in range(1, N + 1):
    L = L * (2**i - 1) // gcd(L, 2**i - 1)
L *= 2 ** ((N - 1).bit_length())
print("L' bit_length:", L.bit_length())

I = [1 << (N - 1 - i) for i in range(N)]
for trial in range(3):
    while True:
        M = [random.getrandbits(N) for _ in range(N)]
        if is_inv(M):
            break
    P = mat_pow(M, L)
    print(f"trial {trial}: M^L' == I ?", P == I)
