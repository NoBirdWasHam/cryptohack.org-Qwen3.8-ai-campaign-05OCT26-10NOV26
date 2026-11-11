import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hamiltonicity import comm_params, pedersen_open
P,q,h1,h2 = comm_params
print('P bits:', P.bit_length())
print('open(1.0,0,0):', pedersen_open(1.0,0,0))
for m,r in [(1,0),(1,5),(0,7)]:
    try:
        print(f'open(1.0,{m},{r}):', pedersen_open(1.0,m,r))
    except Exception as e:
        print(f'open(1.0,{m},{r}) EXC:', type(e).__name__, e)
I1 = pow(h1,-1,P)
print('I1 bits', I1.bit_length(), '> floatmax?', I1 > 1.7976931348623157e308)
# float-convertible threshold
import math
print('floatmax bits ~', math.log2(1.7976931348623157e308))
# how many r give I2=h2^-r mod P below floatmax? sample
cnt=0
import random
for _ in range(20):
    r = random.randrange(q)
    I2 = pow(h2,-r,P)
    if I2 < 1.7976931348623157e308: cnt+=1
print('convertible I2 sample:', cnt, '/20')
