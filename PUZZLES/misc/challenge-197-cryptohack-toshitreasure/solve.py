import socket, json, re

P = (1 << 521) - 1
TARGET = int("8b09cfc4696b91a1cc43372ac66ca36556a41499b495f28cc7ab193e32eadd30", 16)

def recv_avail(s, t=5.0):
    s.settimeout(t)
    data = b""
    try:
        while True:
            b = s.recv(65536)
            if not b: break
            data += b
    except socket.timeout:
        pass
    return data

s = socket.create_connection(("socket.cryptohack.org", 13384), timeout=10)
banner = recv_avail(s, 4)
print("banner bytes:", len(banner))
ym = re.search(rb'"sender": "your_share", "x": 6, "y":"(0x[0-9a-fA-F]+)"', banner)
assert ym, "no your_share in banner"
Y_REAL = int(ym.group(1), 16)

# Step 1: fake share y=0 -> learn C (combined secret with y=0)
s.sendall((json.dumps({"x": 6, "y": "0x0"}) + "\n").encode())
r1 = recv_avail(s, 5).decode(errors="replace")
print("RESP1:", r1[:400])
m = re.search(r'"privkey": "([0-9a-fA-F]+)"', r1)
assert m, "no privkey in resp1"
s1 = int(m.group(1), 16)
C = (s1 - 5 * 0) % P

# Step 2: craft share so combined secret == our own privkey
y_star = (TARGET - C) * pow(5, -1, P) % P
s.sendall((json.dumps({"x": 6, "y": hex(y_star)}) + "\n").encode())
r2 = recv_avail(s, 6).decode(errors="replace")
print("RESP2:", r2)
if "send me a JSON key" in r2:
    REAL = (C + 5 * Y_REAL) % P
    print("real secret hex:", "%x" % REAL, "bits:", REAL.bit_length())
    s.sendall((json.dumps({"privkey": "%064x" % REAL}) + "\n").encode())
    r3 = recv_avail(s, 6).decode(errors="replace")
    print("RESP3:", r3)
    fm = re.search(r"crypto\{[^\"'\s}]+\}", r3)
    if fm:
        print("FLAG:", fm.group(0))
        open("flag_toshitreasure.txt", "w").write(fm.group(0))
s.close()
