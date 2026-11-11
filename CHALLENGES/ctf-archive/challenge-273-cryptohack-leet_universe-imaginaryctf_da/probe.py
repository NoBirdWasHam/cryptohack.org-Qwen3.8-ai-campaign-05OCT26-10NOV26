import socket, sys
def sess(x, timeout=20):
    s=socket.create_connection(("archive.cryptohack.org",3721),timeout)
    s.settimeout(timeout)
    pre=b""
    try: pre=s.recv(4096)
    except Exception: pass
    s.sendall((str(x)+"\n").encode())
    out=b""
    try:
        while True:
            d=s.recv(4096)
            if not d: break
            out+=d
    except Exception: pass
    s.close()
    return pre,out
for x in (0,-42,1337):
    pre,out=sess(x)
    print(repr(x),"pre:",pre[:80],"out:",out[:120])
