import socket, time, select, re
def conn():
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
    return s,f,rd
def get_n():
    s,f,rd=conn()
    init=rd(lambda d:b"friends?" in d,30)
    n=int(re.search(rb"n = (\d+)",init).group(1))
    e=int(re.search(rb"e = (\d+)",init).group(1))
    f.write(b"2\n"); f.flush(); rd(lambda d:b"> " in d,12)
    f.write(b"3\n"); f.flush()
    bye=rd(lambda d:b"bye" in d.lower(),10)
    m=re.search(rb"take with you!\n(\d+)",bye)
    ct=int(m.group(1)) if m else None
    s.close()
    return n,e,ct
n1,e1,ct1=get_n(); time.sleep(1)
n2,e2,ct2=get_n()
print("n1 == n2:", n1==n2)
print("ct1 == ct2:", ct1==ct2)
open("n_live2.txt","w").write(str(n2))
