import socket, json, sys, time
HOST, PORT = "archive.cryptohack.org", 39003

def recv_some(s, t=8.0, idle=2.5):
    s.settimeout(idle)
    buf = b""
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            d = s.recv(4096)
        except socket.timeout:
            if buf:
                break
            continue
        except OSError:
            break
        if not d:
            break
        buf += d
    return buf

def main():
    out = {"t": time.strftime("%Y%m%d_%H%M%S")}
    s = socket.create_connection((HOST, PORT), timeout=15)
    hello = recv_some(s)
    out["hello"] = hello.decode(errors="replace")
    lines = out["hello"].split("\n")
    hexline = None
    for ln in lines:
        ln = ln.strip()
        if ln and all(c in "0123456789abcdef" for c in ln) and len(ln) >= 64:
            hexline = ln
    out["hexline"] = hexline
    # two zero queries of 112 bytes
    resp = []
    for i in range(2):
        s.sendall(b"00" * 112 + b"\n")
        r = recv_some(s, 8)
        resp.append(r.decode(errors="replace").strip())
    # one split probe: 56 + 56
    s.sendall(b"00" * 56 + b"\n")
    r1 = recv_some(s, 6).decode(errors="replace").strip()
    s.sendall(b"00" * 56 + b"\n")
    r2 = recv_some(s, 6).decode(errors="replace").strip()
    # a couple more full blocks for f-recovery (more samples)
    more = []
    for i in range(3):
        s.sendall(b"00" * 112 + b"\n")
        more.append(recv_some(s, 6).decode(errors="replace").strip())
    s.close()
    out["q112"] = resp
    out["split56a"] = r1
    out["split56b"] = r2
    out["more"] = more
    json.dump(out, open("probe1.json", "w"), indent=1)
    for k, v in out.items():
        s2 = str(v)
        print(k, ":", s2[:120])

main()
