# Real probe: PoW + spy guard semantics + auth behavior
import socket, base64, hashlib, time, sys

HOST, PORT = "archive.cryptohack.org", 60192

s = None
for i in range(10):
    try:
        s = socket.create_connection((HOST, PORT), timeout=10); s.settimeout(10)
        buf = b""
        while b"\xf0\x9f\x94\xa9" not in buf:   # wait for prompt
            d = s.recv(4096)
            if not d: break
            buf += d
        if buf[:4] == b"\xf0\x9f\x94\xa7":
            print("connected try", i, repr(buf), flush=True); break
    except Exception as e:
        print(i, type(e).__name__, flush=True)
    s = None; time.sleep(3)
if not s: raise SystemExit("no connect")

state = {"buf": buf}
def getline():
    b = state["buf"]
    while not (b.endswith(b"\n") or b.endswith(b"\xf0\x9f\x94\xa9 ") or b.endswith(b" ")):
        d = s.recv(4096)
        if not d: return None
        b += d
    state["buf"] = b""
    return b.decode(errors="replace").rstrip("\n")

chal = base64.b64decode(getline().split()[1])
t0 = time.time(); r = 0
while not hashlib.sha256(chal + r.to_bytes(4, "big")).digest().startswith(b"\x00\x00\x00"):
    r += 1
print("pow", r, "%.1fs" % (time.time()-t0), flush=True)
s.sendall(base64.b64encode(r.to_bytes(4, "big")) + b"\n")
print("postpow:", repr(getline()), flush=True)

def spy(pbox):
    s.sendall("\U0001f575\ufe0f\n".encode())
    s.sendall(("[%s]\n" % ",".join(map(str, pbox))).encode())
    s.sendall(b"QUFB\n")
    o = getline()
    if o is None: return "<EOF>"
    if not o.startswith("\U0001f511"):
        o2 = getline()
        return (o2 if o2 else o)[:60]
    return o[:60]

def cmd(c):
    s.sendall(c.encode()); return getline()

print("id21:", repr(spy(list(range(21)))), flush=True)
print("id20:", repr(spy(list(range(20)))), flush=True)
print("NEG20..-1:", repr(spy(list(range(-20, 0)))), flush=True)
print("NEG id21:", repr(spy(list(range(-21, 0)))), flush=True)
print("DUP30:", repr(spy(list(range(21)) + list(range(21)))), flush=True)
print("auth(garbage):", repr(cmd("\U0001f5a5\ufe0f\n")), flush=True)
print("auth pbox line:", repr(getline()), flush=True)
print("auth salt line:", repr(getline()), flush=True)
s.sendall(("0"*64+"\n").encode())
print("auth resp:", repr(getline()), flush=True)
print("cmd prompt:", repr(getline()), flush=True)
# second auth round -> compare pbox/salt
cmd("\U0001f5a5\ufe0f\n")
p2 = getline(); sal2 = getline()
print("auth2 pbox:", repr(p2), flush=True)
s.sendall(("0"*64+"\n").encode()); getline()
open("probe_sem.txt","w").write("done")
s.close()
