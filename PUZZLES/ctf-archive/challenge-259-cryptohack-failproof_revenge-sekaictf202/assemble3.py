import os, sys, subprocess
D = os.path.dirname(os.path.abspath(__file__))
segs = []
for i in range(7):
    f = os.path.join(D, f"SEG3_b{i}.txt")
    if not os.path.exists(f):
        print("missing", f); sys.exit(2)
    segs.append(bytes.fromhex(open(f).read().strip()))
flag = b"".join(segs).rstrip(b"\x00")
s = flag.decode("latin-1")
print("FLAG:", repr(s))
if all(32 <= ord(c) < 127 for c in s):
    root = os.path.dirname(D)
    for exe in (sys.executable, "python3"):
        try:
            r = subprocess.run([exe, "submit_flag.py", "failproof_revenge-sekaictf202", s],
                               cwd=root, capture_output=True, text=True, timeout=120)
            print(exe, "->", r.stdout[-400:], r.stderr[-200:])
            if '"ok": true' in r.stdout or "'ok': True" in r.stdout or "correct" in r.stdout.lower():
                open(os.path.join(D, "flag_failproof_revenge-sekaictf202.txt"), "w").write(s)
                print("FLAG SAVED"); break
        except Exception as ex:
            print(exe, "err", ex)
else:
    print("non-printable -> NOT submitting")
