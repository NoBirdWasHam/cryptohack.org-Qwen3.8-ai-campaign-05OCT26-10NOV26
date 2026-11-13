#!/usr/bin/env python3
# degenerate: check base-point / pubkey orders in Edwards group; if smooth -> PH for shared secret.
from Crypto.Util.number import inverse
p = 110791754886372871786646216601736686131457908663834453133932404548926481065303
order = 27697938721593217946661554150434171532902064063497989437820057596877054011573
d = 14053231445764110580607042223819107680391416143200240368020924470807783733946
CE = 110791754886372871786646216601736686131170149361165602787891589423789760286950  # #E
FACT = [2, 3, 3, 5, 5, 1417949130779803207, 19819617105149183461, 8760704198978927479670471850452175473]

def recover_x(xbit, y):
    xsqr = (y**2 - 1) * inverse(1 + d*y*y, p) % p
    x = pow(xsqr, (p + 1)//4, p)
    if x**2 == xsqr:
        if x & 1 != xbit: return p - x
        return x
    return 0

def add(P1, P2):
    x1, y1 = P1; x2, y2 = P2
    C = x1*x2 % p; D = y1*y2 % p
    E = d*C*D
    x3 = (1 - E)*((x1 + y1)*(x2 + y2) - C - D) % p
    y3 = (1 + E)*(D + C) % p
    z3 = 1 - E**2 % p
    z3inv = inverse(z3, p)
    return (x3*z3inv % p, y3*z3inv % p)

def mul(n, P):
    if n == 0: return (0, 1)
    R = P
    for i in range(n.bit_length()-2, -1, -1):
        R = add(R, R)
        if (n >> i) & 1: R = add(R, P)
    return R

B = (recover_x(1, 11), 11)
print("B on curve:", (-B[0]**2 + B[1]**2 - 1 - d*B[0]**2*B[1]**2) % p == 0)
print("#E*B == O:", mul(CE, B) == (0, 1))
# strip factors: find ord(B)
m = CE
for q in sorted(FACT, reverse=True):
    while m % q == 0:
        cand = mul(m // q, B)
        if cand == (0, 1): m //= q
        else: break
print("ord(B) =", m, "bits", m.bit_length())
sm = 2*9*25*1417949130779803207*19819617105149183461
print("ord(B) divides smooth part?", sm % m == 0)
# pubkeys from output.txt
Pa = (0, 109790246752332785586117900442206937983841168568097606235725839233151034058387)
Pb = (0, 45290526009220141417047094490842138744068991614521518736097631206718264930032)
Pa = (recover_x(*Pa), Pa[1]); Pb = (recover_x(*Pb), Pb[1])
print("Pa on curve:", (-Pa[0]**2 + Pa[1]**2 - 1 - d*Pa[0]**2*Pa[1]**2) % p == 0)
print("Pb on curve:", (-Pb[0]**2 + Pb[1]**2 - 1 - d*Pb[0]**2*Pb[1]**2) % p == 0)
for name, P in [("Pa", Pa), ("Pb", Pb)]:
    mm = CE
    for q in sorted(FACT, reverse=True):
        while mm % q == 0:
            if mul(mm // q, P) == (0, 1): mm //= q
            else: break
    print(f"ord({name}) =", mm, "bits", mm.bit_length())
