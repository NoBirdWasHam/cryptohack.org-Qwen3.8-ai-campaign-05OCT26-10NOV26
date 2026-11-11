# dual_masters solve: recover n = int(flag[7:-1]) from (E, P_a, Q_a, E_A, phi(Q_a)).
# Attack: ker(hat_phi) = phi(E[2^216]) = <phi(Q_a)> since phi(P_a) = -n*phi(Q_a).
# Build hat_phi as a 216-step Vélu chain from E_A, dualize step-by-step (with
# twist-identifications pinned by hat^ o hat = [2]), get phi = hat_phi^, evaluate
# phi(P_a) = k*phi(Q_a), solve the 2-adic DLP, n = -k mod 2^216.
import re
from isog_lib import F, EC, recover_n

txt = open("output.txt").read()
P = int(re.search(r"size (\d+)\^2", txt).group(1))
assert P == 2**216 * 3**137 - 1

def parse_point(s):
    ms = re.findall(r"(\d+)\*i \+ (\d+)", s)
    assert len(ms) == 2
    return ((int(ms[0][1]) % P, int(ms[0][0]) % P),
            (int(ms[1][1]) % P, int(ms[1][0]) % P))

Pa = Qa = Qp = None
for line in txt.splitlines():
    if line.startswith("P_a = "):        Pa = parse_point(line)
    if line.startswith("Q_a = "):        Qa = parse_point(line)
    if line.startswith("phi_a(Q_b) = "): Qp = parse_point(line)
mA = re.search(r"x\^3 \+ \((\d+)\*i\+(\d+)\)\*x \+ \((\d+)\*i\+(\d+)\)", txt)
aA = (int(mA.group(2)) % P, int(mA.group(1)) % P)
bA = (int(mA.group(4)) % P, int(mA.group(3)) % P)

Fp2 = F(P)
E  = EC(Fp2, Fp2.zero(), Fp2.one())
EA = EC(Fp2, aA, bA)
assert E.on(Pa) and E.on(Qa) and EA.on(Qp)
assert EA.mul(Qp, 2**216) is None and EA.mul(Qp, 2**215) is not None
print("input parsed; ord(Qp) = 2^216")

n = recover_n(Fp2, EA, Pa, Qa, Qp, 216)
fb = n.to_bytes(27, "big")
print("n =", n)
print("flag bytes:", fb)
flag = "crypto{" + fb.decode("ascii") + "}"
print("FLAG:", flag)
open("flag_dual_masters.txt", "w").write(flag + "\n")
