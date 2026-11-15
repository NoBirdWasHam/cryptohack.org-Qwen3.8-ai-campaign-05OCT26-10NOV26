"""Append 150 more reset+get_sample samples to samples.jsonl (need pairs at j=5, j=26)."""
import json
import socket

HOST, PORT = "socket.cryptohack.org", 13390
N = 150

s = socket.create_connection((HOST, PORT), timeout=60)
s.settimeout(60)
s.recv(65536)

buf = b""
dec = json.JSONDecoder()

def recv_obj():
    global buf
    while True:
        i = buf.find(b"{")
        if i >= 0:
            try:
                obj, end = dec.raw_decode(buf[i:].decode("utf-8"))
                buf = buf[i + end:]
                return obj
            except json.JSONDecodeError:
                pass
        d = s.recv(65536)
        if not d:
            raise RuntimeError("EOF")
        buf += d

def send_obj(o):
    s.sendall((json.dumps(o) + "\n").encode())

with open("samples.jsonl", "a") as f:
    for k in range(N):
        send_obj({"option": "reset"})
        r = recv_obj()
        assert r.get("success"), r
        send_obj({"option": "get_sample"})
        r = recv_obj()
        assert "a" in r and "b" in r, r
        f.write(json.dumps({"a": r["a"], "b": r["b"]}) + "\n")
print("appended", N)
