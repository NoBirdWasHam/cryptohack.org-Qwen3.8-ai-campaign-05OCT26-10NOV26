#!/usr/bin/env python
"""matrix (75 pts) — 50x50 matrix M over GF(2); ciphertext C = M^31337.

Recovery without knowing ord(M): the exponent of GL(50,2) is
L = lcm(2^1-1, ..., 2^50-1).  Since r = ord(M) | L, choose k with
E*t0 = 1 + k*L (k = -L^{-1} mod E, E=31337 prime); then
E*t0 == 1 (mod r), so M = C^{t0}.  One fast GF(2) matrix exponentiation.

Rows are packed as 50-bit ints; mul = 2500 ANDs + parity.
"""
from math import gcd

N = 50
E = 31337

# --- load C from flag.enc (rows of '0'/'1') ---
rows = [list(map(int, row)) for row in open("flag.provided").read().strip().splitlines()]
assert len(rows) == N and all(len(r) == N for r in rows)
C = [sum(b << (N - 1 - j) for j, b in enumerate(row)) for row in rows]


def mat_mul(A, B):
    # A*B over GF(2), rows packed MSB-first
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


# --- L = exponent of GL(50,2) = lcm(2^d-1, 1<=d<=50) * 2^ceil(log2(50)) ---
# (the 2-part comes from unipotent/Jordan blocks; each 2^d-1 is odd)
L = 1
for i in range(1, N + 1):
    L = L * (2**i - 1) // gcd(L, 2**i - 1)
L *= 2 ** ((N - 1).bit_length())  # 2^6 for N=50
print(f"L bit_length: {L.bit_length()}")

# t0 with E*t0 = 1 + k*L
k = (-pow(L % E, -1, E)) % E
t0 = (1 + k * L) // E
assert (t0 * E - 1) % L == 0
print(f"t0 bit_length: {t0.bit_length()}")

M = mat_pow(C, t0)

# verify M^E == C
check = mat_pow(M, E)
print("M^E == C:", check == C)
assert check == C

# msg -> matrix:  rows = [msg[i::N] for i in range(N)]  =>  M[i][j] = msg[i + j*N]
# so msg[k] = M[k % N][k // N]  ->  recover msg column-by-column
bits = []
for j in range(N):          # msg block j: positions j*N .. j*N + N - 1
    for i in range(N):      # M row i, column j
        bits.append((M[i] >> (N - 1 - j)) & 1)
flag_bits = bits[:272]  # 34 chars = 272 bits
flag_bytes = bytes(int("".join(map(str, flag_bits[i:i + 8])), 2) for i in range(0, 272, 8))
print("FLAG:", flag_bytes.decode())
