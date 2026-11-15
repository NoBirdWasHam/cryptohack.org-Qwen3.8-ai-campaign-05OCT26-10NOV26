from sympy import isprime, mod_inverse
a=[588,665,216,113,642,4,836,114,851,492,819,237]
sols=[]
for p in range(101,1000):
    if not isprime(p): continue
    if any(v%p==0 for v in a):  # ratio undefined if any term ==0 mod p
        continue
    ratios=set()
    ok=True
    for i in range(len(a)-1):
        try: r=(a[i+1]*mod_inverse(a[i],p))%p
        except Exception: ok=False;break
        ratios.add(r)
    if ok and len(ratios)==1:
        sols.append((p,ratios.pop()))
print("solutions (p,x):", sols)
