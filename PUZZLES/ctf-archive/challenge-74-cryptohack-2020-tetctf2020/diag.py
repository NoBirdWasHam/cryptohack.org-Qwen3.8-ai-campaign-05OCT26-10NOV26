import solve3, socket, time, re, sys

HOST, PORT = solve3.HOST, solve3.PORT

def full_session(lines_to_send):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(12)
    ss.sendall(("\n".join(lines_to_send) + "\n").encode())
    buf = b""
    t0 = time.time()
    nlines = 0
    while nlines < 2020 and time.time() - t0 < 25:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
        nlines = len(buf.decode(errors="replace").splitlines())
    return ss, buf.decode(errors="replace"), nlines

# Session A: reveals 1792,1396; read all; send msb=0 guess; capture tail
ss, txt, n = full_session(["1792", "1396"])
L = txt.splitlines()
pos = [(i, l) for i, l in enumerate(L) if l.isdigit()]
print("nlines:", n, "number positions:", pos)
nums = [int(l) for _, l in pos]
g0 = solve3.solve_target(nums[1], nums[0], 0)
g1 = solve3.solve_target(nums[1], nums[0], 1)
print("g0,g1 differ only in bit30:", (g0 ^ g1) == (1 << 30))
ss.sendall(f"{g0}\n".encode())
time.sleep(1.5)
try:
    ss.settimeout(5)
    tail = ss.recv(65536).decode(errors="replace")
except socket.timeout:
    tail = "<timeout>"
ss.close()
print("tail after guess:", repr(tail))
print("g0 win:", bool(tail.strip()))  # 2026-11-05 fix: flag format is TetCTF{...}, not crypto{...}
print("WINSESSION g0") if tail.strip() else None
