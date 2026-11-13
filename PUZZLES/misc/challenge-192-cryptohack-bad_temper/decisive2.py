import random
U=0x80000000; L=0x7fffffff; MA=0x9908b0df
def f(y): return (y>>1)^(MA if y&1 else 0)
def my_twist(O):
    mt=list(O)
    for i in range(624):
        y=(mt[i]&U)|(mt[(i+1)%624]&L)
        mt[i]=mt[(i+397)%624]^f(y)
    return mt

base=[random.getrandbits(32) for _ in range(624)]
A1_base=my_twist(base)

# Perturb A0[0] low 31 bits only (keep bit31)
pert=list(base)
pert[0]=base[0]^0x00000001   # flip bit 0
A1_pert=my_twist(pert)
print("perturb A0[0] bit0 -> A1 changed:", A1_base!=A1_pert)

# Perturb A0[0] more low bits
pert2=list(base); pert2[0]=base[0]^0x00ffffff
A1_pert2=my_twist(pert2)
print("perturb A0[0] bits0-23 -> A1 changed:", A1_base!=A1_pert2)

# Perturb A0[0] bit31 (top)
pert3=list(base); pert3[0]=base[0]^0x80000000
A1_pert3=my_twist(pert3)
print("perturb A0[0] bit31 -> A1 changed:", A1_base!=A1_pert3)

# So which bits of A0[0] affect A1?
affect=[]
for bit in range(32):
    p=list(base); p[0]=base[0]^(1<<bit)
    if my_twist(p)!=A1_base: affect.append(bit)
print("A0[0] bits that affect A1:", affect)
