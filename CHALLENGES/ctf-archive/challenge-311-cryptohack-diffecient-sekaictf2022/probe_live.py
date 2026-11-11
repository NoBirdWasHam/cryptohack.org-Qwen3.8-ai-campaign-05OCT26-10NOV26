import socket, time

def conn():
    s = socket.create_connection(("archive.cryptohack.org", 29201), timeout=20)
    s.settimeout(15)
    return s

def rd(s):
    buf = b""
    s.settimeout(8)
    while True:
        try:
            d = s.recv(4096)
        except socket.timeout:
            return buf
        if not d:
            return buf
        buf += d
        if buf.rstrip().endswith(b"option:") or b"flag" in buf or b"DB" in buf or b"Added" in buf or b"Added" in buf or b"wrong" in buf or b"restricted" in buf or b"atleast" in buf or b"quota" in buf or b"successfully" in buf:
            return buf

c = conn(); print("WELCOME:", rd(c)[:0])
# option 1 with random key
import os, random
key = os.urandom(40)
c.sendall(b"1\n" + key.hex().encode() + b"\n"); print("opt1:", rd(c))
# option 2 add small key 'A'
c.sendall(b"2\n41\n"); print("opt2 add A:", rd(c))
# option 2 again -> quota?
c.sendall(b"2\n42\n"); print("opt2 again:", rd(c))
# option 3 fail regex
c.sendall(b"3\n414141\n"); print("opt3 short:", rd(c))
# option 3 regex-fail no digit
c.sendall(b"3\n" + b"a"*32 + b"\n"); print("opt3 nodigit:", rd(c))
# option 3 regex-fail all-lower-32 (needs upper/digit/special)
c.sendall(b"3\n" + b"41"*40 + b"\n"); print("opt3 lower:", rd(c))
# option 3 valid regex random key
kb = bytes(random.randrange(256) for _ in range(40))
c.sendall(b"3\n" + kb.hex().encode() + b"\n"); print("opt3 valid:", rd(c))
c.close()
# persistence test: new conn, add same 'A' key
c2 = conn(); print("banner2:", rd(c2)[:0])
c2.sendall(b"2\n41\n"); print("opt2 'A' fresh conn:", rd(c2))
c2.close()
print("done")
