# Stage 2: compute S3 = [i(ITERS+k) for k in range(1337)] mod p via 21x21 matrix exponentiation.
# g,h,i recurrences from functional.sage with len(COEFFS)=20 (from bm_out.json L=20).
import json, math
p = 2**142 - 111
assert json.load(open('bm_out.json'))['L'] == 20
L = 20
cg = [int(10000*math.log10(2+i)) % p for i in range(6)]
ch = [int(10000*math.log10(1337+i)) % p for i in range(4)]
ci = [int(10000*math.log10(31337+i)) % p for i in range(5)]
g0 = [int(10000*math.sin(L+n)) % p for n in range(6)]
h0 = [int(10000*math.sin(L+6+n)) % p for n in range(3)]
i0 = [int(10000*math.sin(L+9+n)) % p for n in range(3)]

# --- sequential reference (small n) ---
def sequential(NMAX):
    G = g0[:]; H = h0[:]; I = i0[:]
    for n in range(3, NMAX+1):
        # i(n)
        if n >= 3:
            iv = (ci[0]*I[n-2] + ci[1]*G[n-3] + ci[2]*H[n-3] + ci[3]*H[n-1] + ci[4]*I[n-1] + 1) % p
            I.append(iv)
        if n >= 3:
            hv = (ch[0]*H[n-3] + ch[1]*I[n-1] + ch[2]*G[n-2] + ch[3]*H[n-1] + (n % p)) % p
            H.append(hv)
        if n >= 6:
            gv = (cg[0]*G[n-6] + cg[1]*H[n-2] + cg[2]*I[n-3] + cg[3]*G[n-3] + cg[4]*H[n-4] + cg[5]*I[n]
                  + (2*(n**3) + 42) % p) % p
            G.append(gv)
    return G, H, I

# NOTE gating: H/G lists only populated from their own start indices. Fix by explicit dict build:
def sequential2(NMAX):
    G = {n: g0[n] for n in range(6)}
    H = {n: h0[n] for n in range(3)}
    I = {n: i0[n] for n in range(3)}
    for n in range(3, NMAX+1):
        I[n] = (ci[0]*I[n-2] + ci[1]*G[n-3] + ci[2]*H[n-3] + ci[3]*H[n-1] + ci[4]*I[n-1] + 1) % p
        H[n] = (ch[0]*H[n-3] + ch[1]*I[n-1] + ch[2]*G[n-2] + ch[3]*H[n-1] + (n % p)) % p
        if n >= 6:
            G[n] = (cg[0]*G[n-6] + cg[1]*H[n-2] + cg[2]*I[n-3] + cg[3]*G[n-3] + cg[4]*H[n-4] + cg[5]*I[n]
                    + (2*(n**3) + 42) % p) % p
    return G, H, I

# --- matrix: state at index n ---
# pos 0..6: g(n..n-6); 7..13: h(n..n-6); 14..16: i(n),i(n-1),i(n-2); 17..20: 1,n,n^2,n^3
SZ = 21
def Tmat():
    T = [[0]*SZ for _ in range(SZ)]
    # i(n+1) = ci0*i(n-1)+ci1*g(n-2)+ci2*h(n-2)+ci3*h(n)+ci4*i(n) + 1   -> row 14
    T[14][15] = ci[0]; T[14][2] = ci[1]; T[14][9] = ci[2]; T[14][7] = ci[3]; T[14][14] = ci[4]; T[14][17] = 1
    # h(n+1) = ch0*h(n-2)+ch1*i(n-1)+ch2*g(n-2)+ch3*h(n-1) + (n+1)     -> row 7 ; h(n-2)=pos9,i(n-1)=15,g(n-2)=2,h(n-1)=8
    T[7][9] = ch[0]; T[7][14] = ch[1]; T[7][1] = ch[2]; T[7][7] = ch[3]; T[7][18] = 1; T[7][17] = 1
    # precompute i(n+1) into row 20 temp: g(n+1) uses it. Compose by substituting row14 into row0.
    # g(n+1) = cg0*g(n-5)+cg1*h(n-1)+cg2*i(n-2)+cg3*g(n-2)+cg4*h(n-3)+cg5*i(n+1) + 2(n+1)^3+42
    # = ... g(n-5)=pos5,h(n-1)=pos8,i(n-2)=pos16,g(n-2)=pos2,h(n-3)=pos10 ; 2(n+1)^3+42 = 2n^3+6n^2+6n+44
    r14 = T[14]
    T[0][5] = cg[0]; T[0][8] = cg[1]; T[0][16] = cg[2]; T[0][2] = cg[3]; T[0][10] = cg[4]
    T[0][18] = 6; T[0][17] = 44; T[0][19] = 6; T[0][20] = 2
    for c in range(SZ):
        T[0][c] = (T[0][c] + cg[5]*r14[c]) % p
    # shifts
    for k in range(1, 7):   T[k][k-1+1] = 0  # placeholder
    # g shifts: g(n-k) at pos k comes from g(n-(k-1)) pos k-1 of X(n)? pos k of X(n+1)=g(n+1-k)=pos k-1 of X(n)
    for k in range(1, 7):
        T[k] = [0]*SZ; T[k][k-1] = 1
    for k in range(1, 7):
        T[7+k] = [0]*SZ; T[7+k][7+k-1] = 1
    for k in range(1, 3):
        T[14+k] = [0]*SZ; T[14+k][14+k-1] = 1
    # monomials: 1'=1 ; (n+1)=n+1 ; (n+1)^2=n^2+2n+1 ; (n+1)^3=n^3+3n^2+3n+1
    T[17] = [0]*SZ; T[17][17] = 1
    T[18] = [0]*SZ; T[18][18] = 1; T[18][17] = 1
    T[19] = [0]*SZ; T[19][19] = 1; T[19][18] = 2; T[19][17] = 1
    T[20] = [0]*SZ; T[20][20] = 1; T[20][19] = 3; T[20][18] = 3; T[20][17] = 1
    return T

T = Tmat()

def matvec(A, v):
    return [sum(A[r][c]*v[c] for c in range(SZ)) % p for r in range(SZ)]

def matmul(A, B):
    return [[sum(A[r][k]*B[k][c] for k in range(SZ)) % p for c in range(SZ)] for r in range(SZ)]

def state_at(n):
    v = ([Gseq[n-k] for k in range(7)] + [Hseq[n-k] for k in range(7)] +
         [Iseq[n], Iseq[n-1], Iseq[n-2]] + [1, n % p, (n*n) % p, (n*n*n) % p])
    return v

def matpow_apply(Tm, e, v):
    while e:
        if e & 1: v = matvec(Tm, v)
        Tm = matmul(Tm, Tm); e >>= 1
    return v

N0 = 12
Gseq, Hseq, Iseq = sequential2(N0)
# sanity: matrix step matches sequential at N0+1, N0+2
v = state_at(N0)
v1 = matvec(T, v)
Gseq2, Hseq2, Iseq2 = sequential2(N0+2)
assert v1[0] == Gseq2[N0+1] and v1[7] == Hseq2[N0+1] and v1[14] == Iseq2[N0+1], "T mismatch small"
v2 = matvec(T, v1)
assert v2[0] == Gseq2[N0+2] and v2[14] == Iseq2[N0+2], "T mismatch small 2"
print("transition matrix verified vs sequential")

ITERS = json.load(open('iters.json'))['ITERS']
X = matpow_apply(T, ITERS - N0, state_at(N0))
S3 = []
for k in range(1337):
    S3.append(X[14])
    X = matvec(T, X)
json.dump(S3, open('s3.json', 'w'))
print("S3[0..3]:", S3[:4])
print("S3 len:", len(S3))
