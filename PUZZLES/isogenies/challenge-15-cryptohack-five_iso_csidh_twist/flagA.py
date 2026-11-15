from velu_engine import *
p = 419

def montgomery_A(E):
    a = E["a"]; b = E["b"]
    Aset = set()
    for v in [x for x in range(p) if (x*x*x + a*x + b) % p == 0]:
        c2 = (3*v*v + a) % p
        w = sqrt_p(c2, p)
        if w is None:
            continue
        A = (3*v) * pow(w, -1, p) % p
        got, cnt = montgomery_verify(E, A)
        if got is not None:
            Aset.add(A)
    assert len(Aset) == 1, f"ambiguous A: {Aset}"
    return Aset.pop()

# (a) twist backward curve G: y^2 = x^3 + 398 x + 94 (from solve_twist.py run)
EG = make_ec(p, 398, 94)
AG = montgomery_A(EG)
print(f"(a) twist-curve G (j={j_short(398,94,p)}): #E = {EG['count']}(), A = {AG}")

# (b) forward 1-step curve E1: y^2 = x^3 + 182 x + 64 (PARI-verified in TEST3)
E1 = make_ec(p, 182, 64)
A1 = montgomery_A(E1)
print(f"(b) forward-1 curve E1 (j={j_short(182,64,p)}): #E = {E1['count']()}, A = {A1}")

assert AG == A1, "MISMATCH between twist-backward and forward-1 Montgomery A"
print(f"\nFLAG = {AG}")
