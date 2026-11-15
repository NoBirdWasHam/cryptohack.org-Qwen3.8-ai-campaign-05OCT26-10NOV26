import socket, time, select, re
s=socket.create_connection(("archive.cryptohack.org",33824),timeout=40)
f=s.makefile("rwb",buffering=0)
def rd(stop,t=20):
    d=b"";end=time.time()+t
    while time.time()<end:
        r,_,_=select.select([f],[],[],max(0.05,end-time.time()))
        if not r:break
        ch=f.read(1)
        if not ch:break
        d+=ch
        if stop(d):break
    return d
init=rd(lambda d:b"friends?" in d,25)
n=int(re.search(rb"n = (\d+)",init).group(1)); e=65537
f.write(b"1\n"); f.flush(); a=rd(lambda d:b"> " in d,12)
yours=int(re.search(rb"part: (\d+)",a).group(1))
def dec(c):
    f.write(b"1\n"); f.flush(); rd(lambda d:b"Ciphertext" in d,6)
    f.write(f"{c}\n".encode()); f.flush()
    p=rd(lambda d:b"> " in d,30)
    body=p.split(b"friends!")[1]
    vals=[int(x) for x in re.findall(rb"\d+", body.split(b"Select")[0])]
    tot=pow(c,yours,n)
    for v in vals: tot=tot*v%n
    return tot
for c in (2, 123456789123456789):
    tot=dec(c)
    print("c=",c," (c^d)^e==c:", pow(tot,e,n)==c, " tot<inv?", None)
# tot for c=2: is it 2^d? check tot^e==2 already above
# also: is tot maybe small?
tot=dec(2)
print("tot bits:", tot.bit_length())
s.close()
