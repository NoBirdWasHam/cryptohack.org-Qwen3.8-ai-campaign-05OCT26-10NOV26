# Stage 3 prep: build P,Q for Bostan-Mori on j(n); probe digit-sum identity; test small BM.
import json, math
p = 2**142 - 111
S3 = json.load(open('s3.json')); assert len(S3) == 1337
a = [int(10000*math.log(31337+i)) % p for i in range(100)]
J = []
for n in range(10000):
    if n == 0: J.append(0)              # ZZ(0).digits(1337) == []
    elif n < 1337: J.append(S3[n] % p)  # single digit
    else: J.append((S3[n % 1337] + S3[n // 1337]) % p)

# identity probe: does digit-sum form satisfy the recurrence?
fails = 0
ext = J[:]
for n in range(10000, 10500):
    v = sum(a[i]*ext[n-9900-i] for i in range(100)) % p
    ext.append(v)
    ds = (S3[n % 1337] + S3[n // 1337]) % p
    if v != ds: fails += 1
print("identity probe fails in first 500:", fails > 0)

# P = (J * Q) mod x^10000, Q = 1 - sum a_i x^{9900+i}
Q = [0]*10000; Q[0] = 1
for i in range(100): Q[9900+i] = (-a[i]) % p
P = J[:]
for k in range(9900, 10000):
    P[k] = (J[k] - sum(a[i]*J[k-9900-i] for i in range(0, k-9899))) % p
json.dump({'P': P, 'Q': Q}, open('pq_full.json','w'))
print("P,Q built; degQ =", 9999)

# small-order BM sanity (Fibonacci) using same BM math in python
def bm_coeff(Pp, Qq, n):
    Pp = Pp[:]; Qq = Qq[:]
    while n:
        Qm = [ (c if e%2==0 else (-c)%FIB) for e,c in enumerate(Qq)]
        d = len(Pp)+len(Qq)-1
        S = [0]*d
        for e2,c2 in enumerate(Qm):
            if c2:
                for j,c in enumerate(Pp):
                    if c: S[j+e2] = (S[j+e2] + c*c2) % FIB
        st = 0 if n%2==0 else 1
        Pp = S[st::2]
        d2 = 2*len(Qq)-1
        S2 = [0]*d2
        for e1,c1 in enumerate(Qq):
            if c1:
                for e2,c2 in enumerate(Qm):
                    if c2 and (e1+e2)%2==0:
                        S2[(e1+e2)//2] = (S2[(e1+e2)//2] + c1*c2) % FIB
        Qq = S2
        n >>= 1
    return Pp[0]*pow(Qq[0], FIB-2, FIB) % FIB
FIB = 10**9+7
# fib: P=x, Q=1-x-x^2
f=[0,1]
for k in range(2,1200): f.append((f[-1]+f[-2])%FIB)
print("BM fib(10) =", bm_coeff([0,1],[1,FIB-1,FIB-1],10), "expect", f[10])
print("BM fib(1000) =", bm_coeff([0,1],[1,FIB-1,FIB-1],1000), "expect", f[1000])
