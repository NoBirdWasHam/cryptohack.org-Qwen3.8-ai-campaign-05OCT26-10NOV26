# Live solve: M0 = sum mu_k u_k is an exact multiple of phi -> factor n -> decrypt flag ct.
import json, re, sys
sys.set_int_max_str_digits(10**6)
from Crypto.Util.number import long_to_bytes
from factor_from_phi_multiple import factor_from_multiple

D = json.load(open("live_data.json"))
K = json.load(open("kernel.json"))
n, e, ct = int(D["n"]), int(D["e"]), int(D["ct"])
u = {int(k): int(v) for k, v in D["u"].items()}
mu = [int(v) for v in K["mu"]]
assert len(u) == 101 and all(v < n for v in u.values())

M0 = sum(mu[k-1] * u[k] for k in range(1, 102))
print("M0 bits:", abs(M0).bit_length(), "nonzero:", M0 != 0)
p, q = factor_from_multiple(n, M0)
print("factored:", p * q == n)
phi = (p-1) * (q-1)
d = pow(e, -1, phi)
pt = long_to_bytes(pow(ct, d, n))
m = re.search(rb"ECSC\{[^}]*\}", pt)
print("FLAG:", m.group(0).decode() if m else "RAW TAIL: " + pt[-60:].decode("latin1"))
