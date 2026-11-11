import socket, json, sys

def recv_avail(s, t=4.0):
    s.settimeout(t)
    data = b""
    try:
        while True:
            b = s.recv(4096)
            if not b: break
            data += b
    except socket.timeout:
        pass
    return data

s = socket.create_connection(("socket.cryptohack.org", 13384), timeout=10)
print("BANNER:", recv_avail(s, 4).decode(errors="replace"))
msg = json.dumps({"x": 6, "y": "0x1"}) + "\n"
s.sendall(msg.encode())
print("SENT:", msg.strip())
print("RESP1:", recv_avail(s, 5).decode(errors="replace"))
# try another submission in same session
s.sendall((json.dumps({"x": 6, "y": "0x2"}) + "\n").encode())
print("RESP2:", recv_avail(s, 5).decode(errors="replace"))
s.close()
