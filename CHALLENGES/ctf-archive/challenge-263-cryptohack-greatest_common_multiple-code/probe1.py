import socket, re, hashlib, sys, time
s = socket.create_connection(("archive.cryptohack.org", 2762), timeout=20)
s.settimeout(8)
def recv_avail(t=3):
    s.settimeout(t); buf=b""
    try:
        while True:
            d=s.recv(4096)
            if not d: break
            buf+=d
    except Exception: pass
    return buf
def clean(b): return re.sub(rb'\x1b\[[0-9;]*m', b'', b)
buf=b""
while b"hexdigest()" not in buf: buf+=recv_avail(5)
m=re.search(rb'hexdigest\(\) = ([0-9a-f]{32})', buf)
salt=re.search(rb'md5\(str\(n\)\.encode\(\) \+ b\'([^\']+)\'\)', buf).group(1)
h=m.group(1).decode()
n=0
while True:
    if hashlib.md5(str(n).encode()+salt).hexdigest()==h: break
    n+=1
print("pow n=",n, flush=True)
s.sendall((str(n)+"\n").encode())
time.sleep(1)
first=recv_avail(4)
print("AFTER POW:", clean(first), flush=True)
s.sendall(b"tag\n")
t0=recv_avail(3)
print("TAGRESP:", clean(t0), flush=True)
tag=re.search(rb'tag: ([0-9a-f]{32})', t0)
s.sendall(b"\n")
mid=recv_avail(3)
print("MID:", clean(mid), flush=True)
s.sendall((tag.group(1)+b"\n") if tag else b"\n")
last=recv_avail(5)
print("LAST:", clean(last), flush=True)
s.close()
