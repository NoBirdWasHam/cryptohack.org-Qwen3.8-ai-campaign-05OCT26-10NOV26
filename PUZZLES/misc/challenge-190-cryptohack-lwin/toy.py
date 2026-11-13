import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
def gen(flag, T):
    s = list(map(int, "{:0384b}".format(bytes_to_long(flag))))
    def clock():
        b = s[0]
        c = 0
        for t in T: c ^= s[t]
        s[:] = s[1:] + [c]
        return b
    for _ in range(768): clock()
    return "".join(str(clock()) for _ in range(2048))
random.seed(1)
for trial in range(3):
    flag = b"crypto{" + bytes(random.choice(range(32,127)) for _ in range(40)) + b"}"
    assert len(flag)==48
    T = sorted(random.sample(range(384),4))
    out = gen(flag, T)
    open("_toy_out.txt","w").write(out)
    import subprocess
    r = subprocess.run(["python3","solve.py","_toy"],capture_output=True,text=True)
    print("trial",trial,"T=",T,"->",r.stdout.strip().splitlines()[-1])
