#!/usr/bin/env python3
# Local relay: run fisd/fischlin_chal.py as a subprocess per connection, bridge socket<->stdio
import socket, subprocess, threading, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 13583

def pump(src, dst):
    try:
        while True:
            d = src.read1(65536)
            if not d: break
            dst.write(d); dst.flush()
    except Exception:
        pass
    try: dst.close()
    except Exception: pass

def handle(conn):
    try:
        env = dict(os.environ); env["FLAG"] = "FLAG-REDACTED-SEE-FLAGS-MIRROR"
        p = subprocess.Popen([sys.executable, "-u", "fischlin_chal.py"],
                             cwd=os.path.join(HERE, "fisd"), stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=open(os.path.join(HERE, "relay_child.err"), "ab"), env=env)
    except Exception:
        import traceback; traceback.print_exc()
        conn.close(); return
    t1 = threading.Thread(target=pump, args=(conn.makefile("rb"), p.stdin), daemon=True)
    t2 = threading.Thread(target=pump, args=(p.stdout, conn.makefile("wb")), daemon=True)
    t1.start(); t2.start()
    t2.join(); 
    try: conn.close()
    except Exception: pass
    try: p.terminate()
    except Exception: pass

s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", PORT)); s.listen(8)
print(f"relay on {PORT}", flush=True)
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
