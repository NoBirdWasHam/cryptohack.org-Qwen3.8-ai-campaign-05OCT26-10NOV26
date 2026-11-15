# probe4.py 2026-11-01 drift re-probe: byte-exact live-vs-local compare +
# alternating g0/g1 oracle with FULL raw tail capture (stderr tracebacks via
# socat EXEC would show here — new oracle vs the 10-28 win/miss-only probing).
import socket, time, re, sys, subprocess, os
import solve3

HOST, PORT = solve3.HOST, solve3.PORT
HERE = os.path.dirname(os.path.abspath(__file__))

def live_session(reveals, guess=None, read_deadline=20):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(10)
    ss.sendall(("\n".join(str(x) for x in reveals) + "\n").encode())
    buf = b""
    t0 = time.time()
    while time.time() - t0 < read_deadline:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
        if len(buf.decode(errors="replace").splitlines()) >= 2020:
            time.sleep(0.3)
            try:
                ss.settimeout(1.5)
                buf += ss.recv(65536)
            except socket.timeout:
                pass
            break
    head = buf
    tail = b""
    if guess is not None:
        ss.settimeout(10)
        ss.sendall(f"{guess}\n".encode())
        try:
            while True:
                b = ss.recv(65536)
                if not b: break
                tail += b
        except socket.timeout:
            pass
    ss.close()
    return head, tail

# --- local reference run of the posted file ---
proc = subprocess.run(
    [sys.executable, os.path.join(HERE, "2020.py")],
    input=b"1396\n1792\n0\n", capture_output=True, timeout=30,
    env={**os.environ, "FLAG": "[flag value withheld — real-flag strings live only under FLAGS/]"})
loc = proc.stdout.decode(errors="replace")
print("LOCAL first-line:", repr(loc.splitlines()[0] if loc else ""))
print("LOCAL nlines:", len(loc.splitlines()), "stderr:", repr(proc.stderr[:200]))

# --- live session 1: fingerprint only (guess=0 sentinel) ---
head, tail = live_session([1396, 1792], guess=0)
live = head.decode(errors="replace")
L = live.splitlines()
print("LIVE first-line:", repr(L[0] if L else ""))
print("LIVE nlines:", len(L))
nums = [(i, l) for i, l in enumerate(L) if l.strip().isdigit()]
print("LIVE number positions:", nums)
print("LIVE tail repr:", repr(tail[:300]))
print("LIVE tail after last line:", repr(live[-40:]))
greet_match = (L[0] if L else "") == (loc.splitlines()[0] if loc else "")
print("greeting byte-equal:", greet_match)
if len(nums) == 2:
    n1396, n1792 = int(nums[0][1]), int(nums[1][1])
    g0 = solve3.solve_target(n1792, n1396, 0)
    g1 = solve3.solve_target(n1792, n1396, 1)
    # --- alternating oracle, incl. this session's data reused for one side ---
    wins = 0
    trials = [(g0, "g0"), (g1, "g1"), (g0, "g0"), (g1, "g1"), (g0, "g0"), (g1, "g1")]
    for gi, name in trials:
        h, t = live_session([1396, 1792], guess=gi)
        txt = t.decode(errors="replace")
        win = ("crypto{" in txt) or ("TetCTF{" in txt)  # 2026-11-05 fix: live flag format is TetCTF{...}
        trace = "Traceback" in txt or "Error" in txt
        print(f"trial {name}: win={win} trace={trace} tail={repr(txt[:160])}")
        if win:
            m = re.search(r"crypto\{[^}\n]*\}", txt)
            print("FLAG:", m.group(0))
            open(os.path.join(HERE, "flag_2020-tetctf2020.txt"), "w").write(m.group(0))
            sys.exit(0)
        if trace:
            print("!! server emitted traceback on guess — stderr reaches socket")
        time.sleep(0.5)
    print("alternating oracle: 0/6 wins")
