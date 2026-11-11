#!/usr/bin/env python3
"""Raw recorder — no verdict, no interpretation. Records exactly what the
server sends. You read it; nothing here tells you what to think."""
import socket, time, hashlib, json, datetime

HOST, PORT = "archive.cryptohack.org", 21970

def recv_now(s, secs):
    s.settimeout(secs); buf = b""
    try:
        while True:
            c = s.recv(4096)
            if not c:
                buf += b"<server-closed>"
                break
            buf += c
            s.settimeout(1.0)
    except socket.timeout:
        pass
    return buf

log = {"host": HOST, "port": PORT,
       "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "events": []}

s = socket.create_connection((HOST, PORT), timeout=10)

b = recv_now(s, 6)
log["events"].append({"after": "connect", "bytes": len(b),
                      "sha256": hashlib.sha256(b).hexdigest(), "raw": repr(b)})
print(f"after connect      -> {len(b)} bytes")
print(repr(b)); print()

for i, step in enumerate([b"128\n", b"00\n", b"3\n"], 1):
    s.sendall(step)
    r = recv_now(s, 8)
    log["events"].append({"after": f"sent {step!r}", "bytes": len(r),
                          "sha256": hashlib.sha256(r).hexdigest(), "raw": repr(r)})
    print(f"after sending {step!r:<8} -> {len(r)} bytes")
    print(repr(r)); print()

s.close()
fname = f"manual_capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
json.dump(log, open(fname, "w"), indent=1)
print(f"saved: {fname}")
print("no verdict included; compare bytes yourself against AAR.md captures.")
