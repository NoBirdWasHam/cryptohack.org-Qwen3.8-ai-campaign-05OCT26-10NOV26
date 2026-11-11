# Probe3: send 128 small payloads, then wait; also try extra-newline flush
import json, socket, time, sys
HOST, PORT = "archive.cryptohack.org", 34597
small = {"A": [[1]*5 for _ in range(5)], "z": []}
line = (json.dumps(small) + "\n").encode()

def run(extra_nl):
    s = socket.create_connection((HOST, PORT), timeout=10)
    s.settimeout(3)
    time.sleep(1)
    greet = s.recv(65536)
    print("GREET:", greet[:80])
    for i in range(128):
        s.sendall(line)
        time.sleep(0.02)
    if extra_nl:
        s.sendall(b"\n")
    time.sleep(2)
    out = b""
    t0 = time.time()
    while time.time() - t0 < 45:
        try:
            d = s.recv(65536)
        except socket.timeout:
            continue
        except Exception as e:
            out += b"<ERR %s>" % str(e).encode(); break
        if not d:
            out += b"<EOF>"; break
        out += d
    print("extra_nl=%s got %d bytes:" % (extra_nl, len(out)))
    print(out[:2000].decode(errors="replace"))
    s.close()

run(False)
print("="*40)
run(True)
