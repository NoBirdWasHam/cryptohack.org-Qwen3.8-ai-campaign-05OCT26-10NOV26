import ec2 as E
import json, re

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
p = E.p; m = p + 1

ct = json.load(open("output.txt"))
def pt_from(entry):
    x = (entry["x"][0] % p, entry["x"][1] % p)
    y = (entry["y"][0] % p, entry["y"][1] % p)
    return (x, y)

A = pt_from(ct[0]["P"]); B = pt_from(ct[0]["Q"])
print("A == P (trivial isogeny)?", E.ec_eq(A, P))
print("B == Q (trivial isogeny)?", E.ec_eq(B, Q))
print("A on domain E?", E.ec_on_curve(A))
print("B on domain E?", E.ec_on_curve(B))

# order of P + kQ for a few k
def ord_of(R, tag, bound):
    from sympy import factorint
    fac = factorint(bound)
    primes = sorted(fac)
    o = 1
    for l in primes:
        proj = bound // (l ** fac[l])
        Rl = E.ec_mul(proj, R)
        e = 0; cur = Rl; cap = fac[l] + 2
        while cur is not E.O and e < cap:
            cur = E.ec_mul(l, cur); e += 1
        if cur is not E.O:
            print(f"  WARNING {tag}: l={l} did not converge (order not dividing {bound})")
        o *= l ** e
    print(f"{tag} order bits: {o.bit_length()}, order==m? {o==m}, divides m? {m % o == 0}")
    return o

print("computing ord(P+Q)...")
ord_of(E.ec_add(P, E.ec_mul(1, Q)), "P+Q", m)
print("computing ord(P+2Q)...")
ord_of(E.ec_add(P, E.ec_mul(2, Q)), "P+2Q", m)
