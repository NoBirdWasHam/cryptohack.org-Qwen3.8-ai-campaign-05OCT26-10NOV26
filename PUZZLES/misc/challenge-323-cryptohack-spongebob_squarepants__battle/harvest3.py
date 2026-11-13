# harvest3: found_PROD_<n>.txt -> rebuild 3-block messages -> verify with reference python H -> submit
#
# FILE-NAMING SAFETY RULE: this script consumes ONLY files matching found_PROD*.txt given
# explicitly as argv[1]; it never globs or falls back to bare found*.txt, so self-test
# artifacts (which live under ./selftest/) can never trigger a live harvest/submit.
#
# walker3 (mode 0) fires on a capacity-after-block-2 collision of two 16-byte prefixes
# y_a = b1a||b2a, y_b = b1b||b2b (little-endian uint64 words, same C convention as harvest.py):
#   a = b1a||b2a||0^8,  b = b1b||b2b||(r2a ^ r2b),  r2x = H(prefix)[0:8]
# Collision identity: H(u||x) = H(v||y) iff c2(u)==c2(v) and y = x ^ r2(u) ^ r2(v).
import subprocess, sys, socket, time
from spongebob import H

def main():
    if len(sys.argv) < 2 or "found_PROD" not in sys.argv[1]:
        print("usage: harvest3.py found_PROD_<n>.txt  (refusing any other input - safety rule)")
        return 2
    line = open(sys.argv[1]).read().split()
    ya1, ya2, yb1, yb2 = [int(x, 16) for x in line[:4]]
    pa = ya1.to_bytes(8, "little") + ya2.to_bytes(8, "little")
    pb = yb1.to_bytes(8, "little") + yb2.to_bytes(8, "little")
    sa, sb = H(pa), H(pb)                     # post-block-2 mid-states
    assert sa != sb and pa != pb
    assert sa[8:] == sb[8:], "cap2 mismatch: %s vs %s" % (sa[8:].hex(), sb[8:].hex())
    d = bytes(x ^ y for x, y in zip(sa[:8], sb[:8]))
    a = pa + bytes(8)
    b = pb + d
    assert a != b and len(a) % 8 == 0 and len(b) % 8 == 0
    ha, hb = H(a), H(b)
    print("a =", a.hex()); print("b =", b.hex())
    print("H(a) =", ha.hex()); print("H(b) =", hb.hex())
    assert ha == hb, "NOT a collision!"
    print("3-block collision verified locally")

    for attempt in range(3):
        try:
            s = socket.create_connection(("archive.cryptohack.org", 37916), timeout=20)
            s.settimeout(20)
            s.recv(4096)                                   # prompt
            s.sendall(a.hex().encode() + b"\n")
            time.sleep(0.5)
            s.sendall(b.hex().encode() + b"\n")
            time.sleep(2.0)
            data = b""
            while True:
                try:
                    chunk = s.recv(4096)
                except Exception:
                    break
                if not chunk: break
                data += chunk
                if any(k in data for k in (b"crypto{", b"CHTB{")): break
            s.close()
            txt = data.decode(errors="replace")
            print("server said:", txt.strip())
            flag = None
            for _pat in ("crypto{", "CHTB{"):
                if _pat in txt:
                    flag = txt[txt.index(_pat): txt.index("}", txt.index(_pat)) + 1]
                    break
            if flag:
                print("FLAG:", flag)
                open("flag.txt", "w").write(flag + "\n")
                r = subprocess.run([sys.executable, "../submit_flag.py", "spongebob_squarepants__battle", flag],
                                   capture_output=True, text=True, cwd="..")
                print("submit rc =", r.returncode)
                print(r.stdout[-800:]); print(r.stderr[-400:])
                return 0
        except Exception as e:
            print("attempt", attempt, "failed:", repr(e))
            time.sleep(5)
    print("NO FLAG")
    return 1

if __name__ == "__main__":
    sys.exit(main())
