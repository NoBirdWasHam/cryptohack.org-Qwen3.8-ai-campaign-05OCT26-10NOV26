import os, socket, sys, time
host = os.environ.get("CH_HOST", "archive.cryptohack.org")
port = int(os.environ.get("CH_PORT", "16189"))
s = socket.create_connection((host, port), timeout=30)
f = s.makefile("rwb")

def readline_now(t=8):
    s.settimeout(t)
    try:
        line = f.readline()
    except socket.timeout:
        return "<TIMEOUT>"
    if not line:
        return "<EOF>"
    return line.decode(errors="replace").strip()

def send(g):
    s.sendall((g + "\n").encode())

def drain_until_prompt(maxlines=6):
    lines = []
    for _ in range(maxlines):
        l = readline_now()
        lines.append(l)
        if "guess" in l.lower():
            break
        if l in ("<EOF>", "<TIMEOUT>"):
            break
    return lines

# initial prompt
print("INIT:", drain_until_prompt())
tests = ["0", "0.5", "0.12345678901234567", "1.1102230246251565e-16", "0", "0.25"]
for t in tests:
    t0 = time.time()
    send(t)
    got = []
    for _ in range(4):
        l = readline_now()
        got.append(l)
        if "total score" in l or "Error" in l or l in ("<EOF>", "<TIMEOUT>"):
            break
    print("GUESS %-24r %.2fs -> %r" % (t, time.time() - t0, got))
    if any("Error" in g or g in ("<EOF>", "<TIMEOUT>") for g in got):
        print("DIED at guess", repr(t)); break
