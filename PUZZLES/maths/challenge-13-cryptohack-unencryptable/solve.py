# Unencryptable (#95): encrypt() printed "RSA broken!?" because m==m^e mod N for DATA.
# A FIXED POINT m (m^e == m mod N) => m^(e-1) == 1 mod N, i.e. m^65536 == 1 (mod N).
# Descend the 2^k-chain from 65536: the first a != 1 with a^2 == 1 is a NONTRIVIAL
# square root of 1, and gcd(a-1, N) (or gcd(a+1,N)) factors N. Then decrypt c with p,q.
import math
from Crypto.Util.number import long_to_bytes, inverse
N  = 89820998365358013473897522178239129504456795742012047145284663770709932773990122507570315308220128739656230032209252739482850153821841585443253284474483254217510876146854423759901130591536438014306597399390867386257374956301247066160070998068007088716177575177441106230294270738703222381930945708365089958721
e  = 65537
DATA = bytes.fromhex("372f0e88f6f7189da7c06ed49e87e0664b988ecbee583586dfd1c6af99bf20345ae7442012c6807b3493d8936f5b48e553f614754deb3da6230fa1e16a8d5953a94c886699fc2bf409556264d5dced76a1780a90fd22f3701fdbcb183ddab4046affdc4dc6379090f79f4cd50673b24d0b08458cdbe509d60a4ad88a7b4e2921")
c  = 0x5233da71cc1dc1c5f21039f51eb51c80657e1af217d563aa25a8104a4e84a42379040ecdfdd5afa191156ccb40b6f188f4ad96c58922428c4c0bc17fd5384456853e139afde40c3f95988879629297f48d0efa6b335716a4c24bfee36f714d34a4e810a9689e93a0af8502528844ae578100b0188a2790518c695c095c9d677b
m = int.from_bytes(DATA, "big")
assert pow(m, e, N) == m, "DATA is a fixed point"
assert pow(m, e-1, N) == 1
exp = e-1; a = 1
while exp > 1:
    exp //= 2
    a = pow(m, exp, N)
    if a != 1:
        break
# a is a nontrivial square root of 1
g = math.gcd(a-1, N)
p_, q_ = (g, N//g) if 1 < g < N else (math.gcd(a+1, N), None)
assert p_*q_ == N
phi = (p_-1)*(q_-1); d = inverse(e, phi)
pt = pow(c, d, N).to_bytes(128, "big").lstrip(b"\x00")
print("PT:", pt.decode())
