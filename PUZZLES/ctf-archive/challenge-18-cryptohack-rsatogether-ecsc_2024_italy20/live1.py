import socket, time, select, re, sys
s=socket.create_connection(("archive.cryptohack.org",33824),timeout=40)
f=s.makefile("rwb",buffering=0)
def rd(stop,t=15):
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
n=int(re.search(rb"n = (\d+)",init).group(1)); e=int(re.search(rb"e = (\d+)",init).group(1))
open("n_live.txt","w").write(str(n))
f.write(b"1\n"); f.flush(); rd(lambda d:b"> " in d,12)
def decrypt(m, c):
    f.write(b"2\n"); f.flush(); rd(lambda d:b"friends?" in d,8)
    f.write(f"{m-1}\n".encode()); f.flush()
    a=rd(lambda d:b"> " in d,12)
    if b"part:" not in a: print("RAW:", a[:300]); sys.exit(1)
    yours=int(re.search(rb"part: (\d+)",a).group(1))
    f.write(b"1\n"); f.flush(); rd(lambda d:b"Ciphertext" in d,6)
    f.write(f"{c}\n".encode()); f.flush()
    p=rd(lambda d:b"> " in d,40)
    body=p.split(b"friends!")[1]
    vals=[int(x) for x in re.findall(rb"\d+", body.split(b"Select")[0])]
    tot=pow(c,yours,n)
    for v in vals: tot=tot*v%n
    return len(vals), tot, yours
c=pow(2,e,n)
for m in (2,3,5):
    cnt,tot,y=decrypt(m,c)
    print(f"m={m} friends={cnt} product==2: {tot==2}", flush=True)
for m in (101,102):
    cnt,tot,y=decrypt(m,c)
    print(f"m={m} friends={cnt} product==2:",tot==2, flush=True)
s.close()
