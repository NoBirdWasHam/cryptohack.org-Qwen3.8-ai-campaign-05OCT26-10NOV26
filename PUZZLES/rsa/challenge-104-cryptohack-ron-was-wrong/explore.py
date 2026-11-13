import os, glob
from Crypto.PublicKey import RSA
from Crypto.Util.number import long_to_bytes
d="extracted/keys_and_messages"
keys={}
cts={}
for f in glob.glob(d+"/*.pem"):
    num=int(os.path.basename(f).split('.')[0])
    k=RSA.import_key(open(f).read())
    keys[num]=(k.n,k.e)
    print(f"{num}.pem: n bits={k.n.bit_length()} e={k.e}")
# look for relations
nums=sorted(keys)
import math
for i in range(len(nums)):
    for j in range(i+1,len(nums)):
        a,b=keys[nums[i]][0],keys[nums[b] if False else nums[j]][0]
        g=math.gcd(a,b)
        if g>1:
            print(f"SHARED FACTOR {nums[i]} & {nums[j]}: gcd bits {g.bit_length()}")
        if a%b==0 or b%a==0:
            print(f"DIVIDES: {nums[i]} vs {nums[j]}")
        # close?
        if abs(a-b).bit_length()<200 and a!=b:
            print(f"CLOSE: {nums[i]} & {nums[j]} diff bits {abs(a-b).bit_length()}")
