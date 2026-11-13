#!/usr/bin/env python3
# Local replica: TCP-forward stdin/stdout of a fresh server.py child per connection.
import socket, subprocess, threading, sys, os

def handle(c):
    env = dict(os.environ); env["FLAG"] = "crypto{local_replica_not_real}"
    pr = subprocess.Popen([sys.executable, "-u", "_server_local.py"], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, env=env)
    def pump(src, dst):
        try:
            while True:
                b = src.read(1)
                if not b: break
                dst.write(b); dst.flush()
        except Exception:
            pass
        finally:
            try: dst.close()
            except Exception: pass
    t1 = threading.Thread(target=pump, args=(c.makefile("rb"), pr.stdin))
    t2 = threading.Thread(target=pump, args=(pr.stdout, c.makefile("wb")))
    t1.start(); t2.start(); t1.join(); t2.join()
    c.close()

s = socket.socket(); s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 12801)); s.listen(5)
print("local listener up on 12801", flush=True)
while True:
    c, _ = s.accept()
    threading.Thread(target=handle, args=(c,), daemon=True).start()
