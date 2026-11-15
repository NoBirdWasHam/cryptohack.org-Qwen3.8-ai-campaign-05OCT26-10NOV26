import socket, time, select, re
s=socket.create_connection(("archive.cryptohack.org",33824),timeout=40)
f=s.makefile("rwb",buffering=0)
def rd(stop,t=25):
    d=b"";end=time.time()+t
    while time.time()<end:
        r,_,_=select.select([f],[],[],max(0.05,end-time.time()))
        if not r:break
        ch=f.read(1)
        if not ch:break
        d+=ch
        if stop(d):break
    return d
init=rd(lambda d:b"friends?" in d,30)
n=int(re.search(rb"n = (\d+)",init).group(1))
e=int(re.search(rb"e = (\d+)",init).group(1))
open("sess_n.txt","w").write(str(n))
f.write(b"2\n"); f.flush(); rd(lambda d:b"> " in d,12)
f.write(b"3\n"); f.flush()
bye=rd(lambda d: re.search(rb"you!\n\d{100,}", d) is not None, 25)
m=re.search(rb"you!\n(\d+)",bye)
ct=int(m.group(1))
open("sess_ct.txt","w").write(str(ct))
print("n bits:", n.bit_length(), "ct bits:", ct.bit_length())
import gmpy2
for ee in (3,5,7,11,13,65537):
    r = gmpy2.iroot(ct, ee)
    if bool(r[1]): print("PERFECT", ee, "-th power, root bits:", int(r[0]).bit_length())
print("ct % small primes:", [ct % p for p in (2,3,5,7,11,13,17,19,23)])
g = gmpy2.gcd(ct, n)
print("gcd(ct,n):", g)
