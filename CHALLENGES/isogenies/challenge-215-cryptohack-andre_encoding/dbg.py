import ec2 as E
import re

src = open("source.sage").read()
def parse_pt(var):
    m = re.search(var + r" = E\((.+?), 1\)", src, re.S)
    parts = m.group(1).split(",")
    def coeff(part):
        mm = re.match(r"\s*(\d+)\*i \+ (\d+)\s*$", part)
        im_c, re_c = int(mm.group(1)), int(mm.group(2))
        return (re_c % E.p, im_c % E.p)
    return (coeff(parts[0]), coeff(parts[1]))
P = parse_pt("P"); Q = parse_pt("Q")

# field sanity: i^2 = -1
i = (0,1)
print("i*i should be (-1,0):", E.fmul(i,i))
print("1/i should be (0,-1):", E.fdiv((1,0), i))
# (1+i)^2 = 2i
print("(1+i)^2 should be (0,2):", E.fsq((1,1)))
# norm check: a * a_bar = N
a = (3,5)
print("a*conj(a) should be (34,0):", E.fmul(a, E.fneg(a)))

def t(name, cond):
    print(f"{name}: {cond}")
t("P on curve", E.ec_on_curve(P))
t("Q on curve", E.ec_on_curve(Q))
t("P+(-P)==O", E.ec_eq(E.ec_add(P, E.ec_neg(P)), E.O))
t("(P+Q)-P==Q", E.ec_eq(E.ec_add(E.ec_add(P,Q), E.ec_neg(P)), Q))
t("(P+Q)-Q==P", E.ec_eq(E.ec_add(E.ec_add(P,Q), E.ec_neg(Q)), P))
t("2P-P==P", E.ec_eq(E.ec_add(E.ec_mul(2,P), E.ec_neg(P)), P))
t("P+Q on curve", E.ec_on_curve(E.ec_add(P,Q)))
t("2P on curve", E.ec_on_curve(E.ec_add(P,P)))
t("P+P == mul(2,P)", E.ec_eq(E.ec_add(P,P), E.ec_mul(2,P)))
t("3P via add == mul(3,P)", E.ec_eq(E.ec_add(E.ec_add(P,P),P), E.ec_mul(3,P)))
# associativity: (P+Q)+Q == P+(Q+Q)
t("assoc (P+Q)+Q==P+(Q+Q)", E.ec_eq(E.ec_add(E.ec_add(P,Q),Q), E.ec_add(P, E.ec_add(Q,Q))))
# 2P+2P == 4P
t("2P+2P==4P", E.ec_eq(E.ec_add(E.ec_mul(2,P),E.ec_mul(2,P)), E.ec_mul(4,P)))
