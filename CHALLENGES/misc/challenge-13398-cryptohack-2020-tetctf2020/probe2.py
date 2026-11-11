import socket, re

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
    return data.decode(errors="replace")

# P1: out-of-range indices + extra line (checks nIndices==2: guess would be "7")
d = session(["2019", "2020", "7"])
print("P1 nums:", re.findall(r'^(\d+)$', d, re.M), "lines:", len(d.splitlines()))

# P2: three index lines (if live reveals 3, nIndices>2)
d = session(["0", "1", "2"])
print("P2 nums:", re.findall(r'^(\d+)$', d, re.M), "lines:", len(d.splitlines()))

# P3: single line "0 1" (if live splits on spaces, reveals 2; source crashes)
d = session(["0 1"])
print("P3 nums:", re.findall(r'^(\d+)$', d, re.M), "lines:", len(d.splitlines()))

# P4: blank second line (source: int('') crash)
d = session(["0", ""])
print("P4 nums:", re.findall(r'^(\d+)$', d, re.M), "lines:", len(d.splitlines()))
