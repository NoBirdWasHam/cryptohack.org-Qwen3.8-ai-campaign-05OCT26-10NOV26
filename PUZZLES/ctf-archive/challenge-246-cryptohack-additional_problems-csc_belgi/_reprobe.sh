#!/bin/bash
# bounded re-probe: 3 probes, ~10 min apart; appends to reprobe_log.txt
cd "$(dirname "$0")"
for i in 1 2 3; do
  python3 - >> reprobe_log.txt 2>&1 <<'PY'
import socket, time, datetime
ts = datetime.datetime.now().isoformat(timespec="seconds")
try:
    s = socket.create_connection(("archive.cryptohack.org", 21970), timeout=15)
    s.settimeout(20)
    data = b""
    try:
        while True:
            ch = s.recv(4096)
            if not ch: break
            data += ch
            if b"Now you get to encrypt" in data: break
    except socket.timeout:
        pass
    s.close()
    ok = b"Now you get to encrypt" in data
    print(f"[{ts}] probe bytes={len(data)} ALIVE={ok} tail={data[-60:]!r}")
except Exception as e:
    print(f"[{ts}] FAIL {type(e).__name__}: {e}")
PY
  [ $i -lt 3 ] && sleep 600
done
echo "REPROBE_DONE" >> reprobe_log.txt
