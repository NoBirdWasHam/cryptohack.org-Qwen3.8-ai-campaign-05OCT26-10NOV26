# Probe4: tail of 128-small-payload run + line-size survival test
import json, socket, time
HOST, PORT = "archive.cryptohack.org", 34597

def conn():
    s = socket.create_connection((HOST, PORT), timeout=10); s.settimeout(3)
    time.sleep(0.5); g = s.recv(65536); return s, g

def alive(s, wait=3):
    s.settimeout(wait)
    try:
        d = s.recv(65536)
        return ("EOF" if d == b"" else "DATA:%r" % d[:60])
    except socket.timeout:
        return "ALIVE(timeout)"
    except Exception as e:
        return "ERR:%s" % e

# (1) full 128 small payloads, print tail
s, g = conn()
small = {"A": [[1]*5 for _ in range(5)], "z": []}
line = (json.dumps(small) + "\n").encode()
for i in range(128):
    s.sendall(line); time.sleep(0.01)
time.sleep(1)
out = b""
t0 = time.time()
while time.time()-t0 < 20:
    try: d = s.recv(65536)
    except socket.timeout: continue
    except Exception: break
    if not d: out += b"<EOF>"; break
    out += d
print("NPROMPTS:", out.count(b"send fiat shamir"))
print("TAIL:", out[-1500:].decode(errors="replace"))
s.close()

# (2) size survival: pad z with junk ints to reach byte sizes
print("="*30)
for target in [1000, 4000, 8000, 16000, 20000]:
    s, g = conn()
    pad = "9" * max(10, target - 60)
    pay = {"A": [[1]*5 for _ in range(5)], "z": [pad]}
    ln = (json.dumps(pay) + "\n").encode()
    s.sendall(ln); time.sleep(2)
    r = alive(s, 3)
    print("size %6d -> %s" % (len(ln), r))
    s.close()
