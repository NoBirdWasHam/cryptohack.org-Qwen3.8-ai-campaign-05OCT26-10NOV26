import socket, sys, time

HOST, PORT = "archive.cryptohack.org", 21970
try:
    s = socket.create_connection((HOST, PORT), timeout=20)
except Exception as e:
    print(f"CONNECT-FAIL {type(e).__name__}: {e}")
    sys.exit(2)

s.settimeout(20)
buf = b""
t0 = time.time()
# read whatever the server sends without us doing anything (banner + flag block, or crash)
try:
    while time.time() - t0 < 20:
        c = s.recv(4096)
        if not c:
            print("--- server closed connection (EOF) ---")
            break
        buf += c
        if b"Now you get to encrypt" in buf:
            print("--- server reached interactive menu ---")
            break
except socket.timeout:
    print("--- recv timeout ---")
except Exception as e:
    print(f"--- recv error {type(e).__name__}: {e} ---")

print(f"bytes received: {len(buf)}")
print("=== RAW (first 1200) ===")
print(buf[:1200].decode(errors="replace"))
print("=== END ===")
try:
    s.close()
except Exception:
    pass
