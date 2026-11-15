# Firebird internal CTF "lack of entropy" (Mystiz): q = int(gmpy2.digits(p,3)).
# p -> f(p) is strictly increasing (base-3 digits read as decimal preserves
# order), hence n = p*f(p) is strictly increasing -> binary search for p.
import gmpy2

n = 12189464288007059657184858632825479990912616419482466046617619319388181010121359489739982536798361842485210016303524715395474637570227926791570158634811951043352789232959763417380155972853016696908995809240738171081946517881643416715486249
e = 65537
c = 10093874086170276546167955043813453195412484673031739173390677430603113063707524122014352886564777373620029541666833142412009063988439640569778321681605225404251519582850624600712844557011512775502356036366115295154408488005375252950048742

def f(p):
    return int(gmpy2.digits(p, 3))

def g(p):
    return p * f(p)

# sanity: f is strictly increasing spot check
for t in (2, 3, 8, 9, 10**5, 3**40 - 1, 3**40):
    assert f(t) < f(t + 1), t

lo, hi = 1, 1 << 300
assert g(lo) <= n <= g(hi)
while lo < hi:
    mid = (lo + hi + 1) // 2
    if g(mid) <= n:
        lo = mid
    else:
        hi = mid - 1
p = lo
q = f(p)
assert p * q == n, "factor mismatch"
assert gmpy2.is_prime(p) and gmpy2.is_prime(q)

phi = (p - 1) * (q - 1)
d = int(gmpy2.invert(e, phi))
m = pow(c, d, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print("p =", p, p.bit_length(), "bits")
print("q =", q, q.bit_length(), "bits")
print("flag bytes:", flag)
print("flag:", flag.decode())
