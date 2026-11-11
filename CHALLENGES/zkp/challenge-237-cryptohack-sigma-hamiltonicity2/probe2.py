# Probe2: tiny payloads; find when server prints non-prompt output (build ID, numrounds, bits)
import json, socket, sys, time
HOST, PORT = "archive.cryptohack.org", 34597
s = socket.create_connection((HOST, PORT), timeout=8)
f = s.makefile("rwb")
def recv_till(timeout=6):
    s.settimeout(timeout); data = b""
    try:
        while True:
            c = f.read(1)
            if not c: break
            data += c
    except Exception as e:
        data += b"<TIMEOUT>"
    return data
print("GREET:", recv_till().decode(errors="replace"))
small = {"A": [[1]*5 for _ in range(5)], "z": []}
line = (json.dumps(small) + "\n").encode()
for i in range(130):
    f.write(line); f.flush()
    r = recv_till(5)
    if b"send fiat shamir proof" not in r or b"computing" in r or r == b"" or b"TIMEOUT" in r:
        print(f"round {i}: resp={r!r}")
        if r == b"": print("EOF at round", i); break
        if b"computing" in r:
            print("FULL:", recv_till(8).decode(errors="replace"))
            break
s.close()
