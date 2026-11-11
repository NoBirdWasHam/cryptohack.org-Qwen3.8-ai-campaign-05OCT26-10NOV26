from py_ecc.optimized_bn128 import pairing, multiply
from py_ecc.fields.optimized_bn128_FQ import FQ1
from py_ecc.fields.optimized_bn128_FQ2 import FQ2
from py_ecc.fields.optimized_bn128_FQ6 import FQ6
from py_ecc.fields.optimized_bn128_FQ12 import FQ12
import sys
line=open(r"~\Practice_runs\cryptohack_org\challenge-229-cryptohack-pairingbased\output.txt").readline().strip()
xG,yG,zG=eval(line)
xG=[FQ1(c) for c in xG]
yG=[FQ2((FQ1(c[0][0]),FQ1(c[0][1]))) for c in yG]
def to_fq12(z):
    fq2=lambda a,b: FQ2((FQ1(a),FQ1(b)))
    c0,f0,f1=fq2(z[0],z[1]),fq2(z[2],z[3]),fq2(z[4],z[5])
    c1,f2,f3=fq2(z[6],z[7]),fq2(z[8],z[9]),fq2(z[10],z[11])
    return FQ12((FQ6(c0,f0,f1),FQ6(c1,f2,f3)))
E=pairing(yG,xG)
z12=to_fq12(zG)
print("E type:",type(E))
print("E==z12 ?", E==z12)
print("E.num==z12.num ?", E.num==z12.num)
b=7
zG2=pairing(yG, multiply(xG,b))
print("E vs e(yG,7xG) equal? (should differ) :", E==zG2)
