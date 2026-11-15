import socket, time
for i in range(12):
    try:
        t0=time.time()
        s=socket.create_connection(("archive.cryptohack.org",60192),timeout=8); s.settimeout(8)
        b=b""
        while time.time()-t0<10:
            d=s.recv(4096)
            if not d: break
            b+=d
            if b.endswith(b"\n"): break
        print(i, "%.1fs"%(time.time()-t0), repr(b[:40]))
    except Exception as e:
        print(i, "ERR", type(e).__name__)
    s.close(); time.sleep(2)
