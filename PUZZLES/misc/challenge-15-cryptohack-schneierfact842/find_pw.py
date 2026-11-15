# schneierfact842: numpy int64 product overflow -> find password with prime sum AND
# prime (overflowed) product. Server: 64-bit Linux numpy int64 wraparound.
import numpy as np, random, string, sys
try:
    from Crypto.Util.number import isPrime
except ImportError:
    from sympy import isprime as isPrime

def ok(pw):
    a = np.array(list(map(ord, pw)))
    s = int(a.sum()); pr = int(a.prod())
    return isPrime(s) and isPrime(pr)

chars = string.ascii_letters + string.digits
random.seed()
found = []
tries = 0
while len(found) < 5:
    tries += 1
    L = random.choice([12, 13, 14, 15, 16, 18, 20, 24, 30])
    pw = ''.join(random.choice(chars) for _ in range(L))
    if not (any(c.isdigit() for c in pw) and any(c.isupper() for c in pw) and any(c.islower() for c in pw)):
        continue
    a = np.array(list(map(ord, pw)))
    s = int(a.sum())
    if not isPrime(s):
        continue
    pr = int(a.prod())
    if pr > 0 and isPrime(pr):
        found.append(pw)
        print("FOUND:", pw, "sum", s, "prod", pr, "(tries", tries, ")", flush=True)
print(found[0])
