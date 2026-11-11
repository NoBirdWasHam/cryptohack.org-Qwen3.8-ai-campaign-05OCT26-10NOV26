import socket, time, sys

def recv_avail(s, t=3.0):
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
print("BANNER:", recv_avail(s, 4))
# send nothing yet, see if more comes
print("MORE:", recv_avail(s, 2))
s.close()
