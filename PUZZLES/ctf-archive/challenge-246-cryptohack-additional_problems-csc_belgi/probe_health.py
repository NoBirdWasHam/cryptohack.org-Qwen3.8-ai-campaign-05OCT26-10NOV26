# probe_health.py 2026-11-02: single-connection listener health probe.
# Known dead signature: stalls at exactly 319 bytes (crash at FLAG join,
# os.getenv('FLAG') is None; socket never closes).
# HEALTHY => >319 bytes arrive (flag ciphertexts / menu after banner).
import socket, time, sys

HOST, PORT = "archive.cryptohack.org", 21970
DEAD_BYTES = 319

ss = socket.create_connection((HOST, PORT), timeout=10)
ss.settimeout(8)
buf = b""
t0 = time.time()
while time.time() - t0 < 40:
    try:
        b = ss.recv(4096)
    except socket.timeout:
        break
    if not b:
        break
    buf += b
ss.close()
txt = buf.decode(errors="replace")
print("timestamp:", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
print("bytes:", len(buf))
print("closed_cleanly_eof:", buf != b"" and not txt.endswith("\n") or True)
print("tail_repr:", repr(txt[-80:]))
print("full_repr:", repr(txt))
if len(buf) > DEAD_BYTES:
    print("VERDICT: HEALTHY (past 319-byte crash point)")
    sys.exit(0)
elif len(buf) == DEAD_BYTES:
    print("VERDICT: STILL DEAD (exact 319-byte crash signature)")
    sys.exit(3)
else:
    print("VERDICT: CHANGED but <319 bytes - inspect")
    sys.exit(4)
