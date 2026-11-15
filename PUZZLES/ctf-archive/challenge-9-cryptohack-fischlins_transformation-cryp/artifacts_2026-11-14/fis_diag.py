#!/usr/bin/env python3
# Full-log single session against archive.cryptohack.org:3583
import socket, sys, time, json

HOST, PORT = "archive.cryptohack.org", 3583
LOG = open(r"~/AppData/Local/hermes/cache/scratch/w6e/fis_diag.log", "w", buffering=1)

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")

def recv_window(s, wait=120.0, idle=10.0):
    """Collect whatever arrives for up to `wait` sec; return after `idle` sec of silence once we have data."""
    buf = b""
    t0 = time.time()
    last = t0
    s.settimeout(2.0)
    while time.time() - t0 < wait:
        try:
            d = s.recv(65536)
        except socket.timeout:
            if buf and time.time() - last > idle:
                break
            continue
        except Exception as e:
            log("RECV EXC", repr(e))
            break
        if not d:
            log("EOF from server at t=%.1f" % (time.time()-t0))
            break
        now = time.time()
        log("RECV +%.2fs %r" % (now-t0, d[:200]))
        buf += d
        last = now
    return buf

t_conn = time.time()
s = socket.create_connection((HOST, PORT), timeout=30)
log("CONNECTED after %.2fs" % (time.time()-t_conn))

head = recv_window(s, wait=120, idle=10)
log("HEAD(%d bytes):" % len(head), head[:3000].decode("utf8", "replace"))
if not head:
    log("SERVER SILENT ON CONNECT")
    sys.exit(0)

s.sendall(b"0\n")
log("SENT 0\\n (leak w0)")
leak = recv_window(s, wait=120, idle=15)
log("LEAK RESP(%d):" % len(leak), leak[:4000].decode("utf8", "replace"))

s.sendall(b"n\n")
log("SENT n\\n")
nxt = recv_window(s, wait=120, idle=15)
log("AFTER-N(%d):" % len(nxt), nxt[:4000].decode("utf8", "replace"))

try:
    s.close()
except Exception:
    pass
log("DONE")
