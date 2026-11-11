# probe6_drift.py 2026-11-02: cheap drift check per AAR "cheapest next move".
# 3 sessions, ONE connection each (reveal -> read stream -> compute -> guess
# on the SAME socket, like solve3.run_once), msb branch alternates 0,1,0.
# Captures full live I/O fingerprint (bytes, lines, Nope count, number-line
# positions, first line). Any win => vulnerable build is back.
import socket, time, json, os, sys, re
import solve3

HERE = os.path.dirname(os.path.abspath(__file__))
HOST, PORT = solve3.HOST, solve3.PORT

def session(msb, deadline=25):
    ss = socket.create_connection((HOST, PORT), timeout=10)
    ss.settimeout(10)
    t0 = time.time()
    ss.sendall(b"1396\n1792\n")
    buf = b""
    lines = []
    while time.time() - t0 < deadline:
        try:
            b = ss.recv(65536)
        except socket.timeout:
            break
        if not b:
            break
        buf += b
        lines = buf.decode(errors="replace").splitlines()
        if len(lines) >= 2020:
            break
    nums = [int(l) for l in lines if l.strip().isdigit()]
    num_lines = [i + 1 for i, l in enumerate(lines) if l.strip().isdigit()]
    fp = {"t": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "bytes": len(buf),
          "nlines": len(lines), "nnope": sum(1 for l in lines if l == "Nope!"),
          "first": lines[0] if lines else None, "nums": nums,
          "num_lines": num_lines, "msb": msb}
    if len(nums) == 2:
        g = solve3.solve_target(nums[1], nums[0], msb)  # nums[0]=idx1396, nums[1]=idx1792
        fp["guess"] = g
        ss.sendall(f"{g}\n".encode())
        rest = b""
        try:
            while True:
                b = ss.recv(65536)
                if not b:
                    break
                rest += b
        except socket.timeout:
            pass
        tail = rest.decode(errors="replace")
        fp["tail"] = tail[:200]
        # 2026-11-05 fix: wrong guess => empty tail; server prints NOTHING else.
        # Any non-empty tail after the guess = flag printed (format is TetCTF{...}).
        fp["win"] = bool(tail.strip())
    else:
        fp["win"] = False
    ss.close()
    return fp

def main():
    print("host:", HOST, PORT, flush=True)
    log = []
    for k in range(3):  # msb alternates 0,1,0 per AAR drift-check recipe
        fp = session(msb=k % 2)
        log.append(fp)
        print("session", k, "msb=", fp["msb"],
              "bytes=", fp["bytes"], "lines=", fp["nlines"],
              "nope=", fp["nnope"], "num_lines=", fp["num_lines"],
              "win=", fp["win"], flush=True)
        if fp["win"]:
            m = re.search(r"[A-Za-z][A-Za-z0-9_]*\{[^}\n]+\}", fp.get("tail", ""))
            print("VULNERABLE BUILD BACK. FLAG:", m.group(0) if m else "?")
            json.dump(log, open(os.path.join(HERE, "probe6_drift.json"), "w"), indent=1)
            if m:
                open(os.path.join(HERE, "flag_2020-tetctf2020.txt"), "w").write(m.group(0))
            sys.exit(7)
        time.sleep(1.0)
    json.dump(log, open(os.path.join(HERE, "probe6_drift.json"), "w"), indent=1)
    print("drift-check done: 0/3 alternating sessions -> verdict depends on fingerprint diff")

main()
