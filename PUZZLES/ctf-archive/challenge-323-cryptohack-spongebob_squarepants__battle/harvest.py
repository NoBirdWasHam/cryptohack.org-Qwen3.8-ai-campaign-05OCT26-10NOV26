# harvest: found.txt -> verify collision with python H -> socket exchange -> flag -> submit
import subprocess, sys, socket, time
from spongebob import H

def main():
    line = open("found.txt").read().split()
    m1 = int(line[0], 16); m2 = int(line[1], 16)
    # C walker convention: m bytes = little-endian (m[i] = byte i of uint64); C cap == H(msg)[8:] byte-for-byte
    b1 = m1.to_bytes(8, "little"); b2 = m2.to_bytes(8, "little")
    s1 = H(b1); s2 = H(b2)   # 1-block hashes = post-block-1 states
    assert s1[8:] == s2[8:], "capacity mismatch: %s vs %s" % (s1[8:].hex(), s2[8:].hex())
    d = bytes(x ^ y for x, y in zip(s1[:8], s2[:8]))
    a = b1 + bytes(8)
    b = b2 + d
    assert a != b and len(a) % 8 == 0 and len(b) % 8 == 0
    ha, hb = H(a), H(b)
    print("a =", a.hex()); print("b =", b.hex())
    print("H(a)=", ha.hex()); print("H(b)=", hb.hex())
    assert ha == hb, "NOT a collision!"
    print("collision verified locally")

    # live exchange
    for attempt in range(3):
        try:
            s = socket.create_connection(("archive.cryptohack.org", 37916), timeout=20)
            s.settimeout(20)
            prompt = s.recv(4096)
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
                if b"crypto{" in data: break
            s.close()
            txt = data.decode(errors="replace")
            print("server said:", txt.strip())
            if "crypto{" in txt:
                flag = txt[txt.index("crypto{"): txt.index("}") + 1]
                print("FLAG:", flag)
                open("flag.txt", "w").write(flag + "\n")
                r = subprocess.run([sys.executable, "../submit_flag.py", "spongebob_squarepants__battle", flag],
                                   capture_output=True, text=True, cwd="..")
                print("submit rc=", r.returncode)
                print(r.stdout[-800:]); print(r.stderr[-400:])
                return 0
        except Exception as e:
            print("attempt", attempt, "failed:", repr(e))
            time.sleep(5)
    print("NO FLAG")
    return 1

if __name__ == "__main__":
    sys.exit(main())
