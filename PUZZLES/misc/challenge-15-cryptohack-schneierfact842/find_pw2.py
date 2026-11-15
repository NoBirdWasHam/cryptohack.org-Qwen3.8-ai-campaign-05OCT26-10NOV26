# schneierfact842 v2: emulate Linux int64 product wrap explicitly (Windows numpy = int32!)
import random, string
from Crypto.Util.number import isPrime

M = 1 << 64
def prod64(ords):
    p = 1
    for o in ords:
        p = (p * o) & (M - 1)
    return p - M if p >= (1 << 63) else p

chars = string.ascii_letters + string.digits
found = []
tries = 0
while len(found) < 4:
    tries += 1
    L = random.choice([12, 13, 14, 15, 16, 18, 20])
    pw = ''.join(random.choice(chars) for _ in range(L))
    if not (any(c.isdigit() for c in pw) and any(c.isupper() for c in pw) and any(c.islower() for c in pw)):
        continue
    ords = [ord(c) for c in pw]
    if not isPrime(sum(ords)):
        continue
    pr = prod64(ords)
    if pr > 0 and isPrime(pr):
        found.append(pw)
        print("FOUND:", pw, "sum", sum(ords), "prod64", pr, "(tries", tries, ")", flush=True)
