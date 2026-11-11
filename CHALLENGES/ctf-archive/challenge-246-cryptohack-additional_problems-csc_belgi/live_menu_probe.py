import socket, time

HOST, PORT = "archive.cryptohack.org", 21970
s = socket.create_connection((HOST, PORT), timeout=15)
s.settimeout(6)

def drain(label):
    got = b""
    try:
        while True:
            c = s.recv(4096)
            if not c:
                return got + b"<<EOF>>"
            got += c
    except socket.timeout:
        return got + b"<<TIMEOUT>>"
    except Exception as e:
        return got + f"<<ERR {type(e).__name__}>>".encode()

banner = drain("banner")
print(f"[banner] {len(banner)} bytes (strip markers): tail={banner[-40:]!r}")

# Hypothesis under test: server is waiting on input / menu is buffered. Push menu choices.
for choice in [b"1\n", b"128\n", b"41414141\n", b"3\n", b"2\n", b"\n", b"3\n"]:
    s.sendall(choice)
    resp = drain("after " + choice.decode().strip())
    print(f"[sent {choice!r}] resp={resp!r}")

print("RESULT: any menu response to input?",
      any(k in b"".join([]) for k in [b"Choose N", b"Decrypted", b"What do you"]))
try:
    s.close()
except Exception:
    pass
