import socket, sys, time

def talk(payloads, host="archive.cryptohack.org", port=37916, wait=2.0):
    s = socket.create_connection((host, port), timeout=15)
    s.settimeout(6)
    out = []
    try:
        try:
            out.append(("prompt", s.recv(4096).decode(errors="replace")))
        except Exception as e:
            out.append(("prompt-err", repr(e)))
        for p in payloads:
            s.sendall((p + "\n").encode())
            time.sleep(wait)
            try:
                d = s.recv(4096).decode(errors="replace")
            except Exception as e:
                d = "<<recv-timeout " + repr(e) + ">>"
            out.append((p, d))
    finally:
        s.close()
    return out

mode = sys.argv[1] if len(sys.argv) > 1 else "probe"
if mode == "probe":
    for k, v in talk(["61", "6162"]):   # 1-byte vs 2-byte msgs (0 blocks each if zip-truncation accepted)
        print(f"--- {k!r}:\n{v}")
elif mode == "short2":
    # two DIFFERENT sub-8-byte messages: both -> zero blocks -> H=INIT if no assert
    for k, v in talk(["616263", "64"]):
        print(f"--- {k!r}:\n{v}")
