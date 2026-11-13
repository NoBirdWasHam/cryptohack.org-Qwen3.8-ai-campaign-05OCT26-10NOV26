import random, subprocess
from Crypto.Util.number import bytes_to_long
random.seed(1)
for trial in range(3):
    flag = b"crypto{" + bytes(random.choice(range(32,127)) for _ in range(40)) + b"}"
    T = sorted(random.sample(range(384),4))
    st = list(map(int,"{:0384b}".format(bytes_to_long(flag))))
    out=[]
    for _ in range(2816):
        out.append(st[0]); c=0
        for t in T: c^=st[t]
        st=st[1:]+[c]
    open("_toy_out.txt","w").write("".join(map(str,out[768:2816])))
    r = subprocess.run(["python3","solve2.py","_toy_out.txt"],capture_output=True,text=True)
    last=[l for l in r.stdout.splitlines() if l.startswith("FLAG") or "bytes" in l or "taps" in l or "rank" in l or "forward" in l]
    print("trial",trial,"true T=",T,"true flag=",flag)
    print("  ", " | ".join(last))
