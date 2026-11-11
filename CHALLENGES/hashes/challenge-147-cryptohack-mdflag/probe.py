import socket, json, sys

PORT = 13407

def connect():
    s = socket.create_connection(("socket.cryptohack.org", PORT), timeout=30)
    s.settimeout(25)
    return s

def next_obj(s, buf=b""):
    for _ in range(600):
        b = buf.find(b"{")
        if b >= 0:
            try:
                obj, i = json.JSONDecoder().raw_decode(buf[b:].decode())
                return obj, buf[b+i:]
            except json.JSONDecodeError:
                pass
        d = s.recv(65536)
        if not d:
            break
        buf += d
    raise RuntimeError("no obj: " + repr(buf[:200]))

def send(s, obj):
    s.sendall((json.dumps(obj) + "\n").encode())

s = connect()
# greeting may be plain text; read whatever comes first
buf = b""
try:
    s.settimeout(5)
    buf = s.recv(65536)
except Exception:
    pass
print("FIRST RECV:", repr(buf[:300]))
s.settimeout(25)

# try a message option
send(s, {"option": "message", "data": "41" * 100})
obj, buf = next_obj(s, buf)
print("RESP1:", obj)

# length probe: find minimal n that returns a hash
for n in [1, 8, 16, 24, 32, 36, 38, 40, 42, 44, 45, 46, 48, 50, 55, 56, 64]:
    send(s, {"option": "message", "data": "00" * n})
    obj, buf = next_obj(s, buf)
    print(n, "->", obj)

# weird options
for opt in ["flag", "get_flag", "admin", "debug", ""]:
    send(s, {"option": opt})
    obj, buf = next_obj(s, buf)
    print("opt", repr(opt), "->", obj)
s.close()
