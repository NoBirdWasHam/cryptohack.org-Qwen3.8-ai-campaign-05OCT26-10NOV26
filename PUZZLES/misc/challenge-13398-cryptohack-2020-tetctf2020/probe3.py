import socket, re, time

HOST, PORT = "archive.cryptohack.org", 63222

def session(lines, timeout=15):
    s = socket.create_connection((HOST, PORT), timeout=10)
    s.settimeout(timeout)
    s.sendall(("\n".join(lines) + "\n").encode())
    data = b""
    try:
        while True:
            b = s.recv(65536)
            if not b: break
            data += b
    except socket.timeout:
        pass
    s.close()
    return re.findall(r'^(\d+)$', data.decode(errors="replace"), re.M)

# T1: stream consistency WITHIN a session-pair of connections? (tests shared process/stream)
a = session(["0"])
b = session(["1"])
c = session(["0", "1"])
print("idx0==idx1?", a and b and a[0]==b[0])
print("pair(0,1)[0]==single0?", a and c and a[0]==c[0], "pair[1]==single1?", b and c and b[0]==c[1])
# T2: determinism across time (time-based seed would repeat values at ~same second)
vals = []
for t in range(6):
    v = session(["0"])
    vals.append(v[0] if v else None)
    time.sleep(0.3)
print("idx0 across 6 fresh sessions:", vals)
print("dups:", len(vals)-len(set(vals)))
