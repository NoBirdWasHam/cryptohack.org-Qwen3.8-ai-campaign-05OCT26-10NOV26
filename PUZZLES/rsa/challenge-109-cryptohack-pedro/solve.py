#!/usr/bin/env python
# pedro (150): server returns FLAG if pow(vote, e=3, N).split(b'\x00')[-1] == b'VOTE FOR PEDRO'.
# We ARE given N,e (alice.key). Build vote whose cube (no wrap, <N) ends with \x00+target.
# Hensel-lift x^3 == V (mod 2^120), V=bytes_to_long(target). x^3<2^360<N => last 15 bytes are target.
import sys; sys.set_int_max_str_digits(100000)
from Crypto.Util.number import long_to_bytes, bytes_to_long
N=22266616657574989868109324252160663470925207690694094953312891282341426880506924648525181014287214350136557941201445475540830225059514652125310445352175047408966028497316806142156338927162621004774769949534239479839334209147097793526879762417526445739552772039876568156469224491682030314994880247983332964121759307658270083947005466578077153185206199759569902810832114058818478518470715726064960617482910172035743003538122402440142861494899725720505181663738931151677884218457824676140190841393217857683627886497104915390385283364971133316672332846071665082777884028170668140862010444247560019193505999704028222347577
e=3
target=b'VOTE FOR PEDRO'; V=bytes_to_long(target)
def cube_root_2k(V,k=120):
    x=None;m=8
    for x0 in (1,3,5,7):
        if pow(x0,3,m)==V%m: x=x0
    m=8
    while m < (1<<k):
        for d in (0,1):
            c=(x+d*m)
            if pow(c,3,m*2)==V%(m*2): x=c%(m*2); break
        m*=2
    return x%(1<<k)
vote=cube_root_2k(V,120)
assert pow(vote,e)<N
dec=long_to_bytes(pow(vote,e,N)).split(b'\x00')[-1]
assert dec==target
VOTEHEX=hex(vote)
print("VOTE=",VOTEHEX)
import socket,json
s=socket.create_connection(("socket.cryptohack.org",13375),timeout=60);s.settimeout(30)
s.recv(65536)
s.sendall((json.dumps({"option":"vote","vote":VOTEHEX[2:]})+"\n").encode())
buf=b""
while b'flag' not in buf and b'error' not in buf:
    d=s.recv(65536)
    if not d:break
    buf+=d
print(buf.decode())
s.close()
