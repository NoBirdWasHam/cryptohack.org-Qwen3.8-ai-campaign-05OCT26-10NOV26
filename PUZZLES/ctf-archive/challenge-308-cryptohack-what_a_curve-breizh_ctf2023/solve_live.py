import socket, json, struct, time, random, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
import cantor2 as K7
import frecov as FR
import attack as ATK

P7 = 17585255163044402023
K7.set_p(P7)
random.seed(os.getpid())
HOST, PORT = "archive.cryptohack.org", 39003

def recv_some(s, t=8.0, idle=2.5):
    s.settimeout(idle)
    buf = b""; t0 = time.time()
    while time.time() - t0 < t:
        try:
            d = s.recv(4096)
        except socket.timeout:
            if buf: break
            continue
        except OSError:
            break
        if not d: break
        buf += d
    return buf

def get_hex(buf):
    for ln in buf.decode(errors="replace").split("\n"):
        ln = ln.strip()
        if ln and len(ln) >= 16 and all(c in "0123456789abcdef" for c in ln):
            return ln
    return None

def query(s, msg):
    s.sendall(msg.hex().encode() + b"\n")
    return bytes.fromhex(get_hex(recv_some(s)))

def touv(b):
    return ([x % P7 for x in b[:7]] + [1], [x % P7 for x in b[7:14]])

def solve_connection():
    s = socket.create_connection((HOST, PORT), timeout=15)
    C = bytes.fromhex(get_hex(recv_some(s, 10)))
    print("C:", len(C), "bytes")
    zs = []
    f = None
    for i in range(6):
        r = query(s, b"\x00" * 112)
        zs.append(struct.unpack('<14Q', r))
        part, basis = FR.solve_f_from_samples([touv(b) for b in zs[:3]])
        if basis:
            continue
        cand = part
        # validate with all collected
        if all(K7.is_reduced(touv(b), cand) for b in zs):
            f = cand
            break
    print("f recovered with", len(zs), "samples")
    s.close()
    if f is None:
        return None, None, None
    C112 = C[:112]
    cands = ATK.attack(C112, f)
    print("candidates:", len(cands))
    return C, f, cands

if __name__ == "__main__":
    for attempt in range(3):
        try:
            C, f, cands = solve_connection()
        except Exception as e:
            print("attempt", attempt, "err", e)
            time.sleep(3)
            continue
        if f is None:
            print("f fail attempt", attempt); continue
        for u, fl in cands:
            print("CAND:", fl)
        if len(cands) == 1:
            fl = cands[0][1]
            full = bytes.fromhex(C.hex()[:0] + "")  # placeholder
            # full flag if C longer than 112: extra bytes unknown keystream
            open("flag_candidate.bin", "wb").write(fl)
            json.dump({"C": C.hex(), "f": f, "flag": fl.decode(errors="replace"),
                       "u": list(cands[0][0])}, open("solved1.json", "w"))
            print("FLAG:", fl.decode())
            break
        elif len(cands) > 1:
            print("multiple — need more filtering")
            json.dump({"C": C.hex(), "f": f,
                       "cands": [[list(u), fl.decode(errors='replace')] for u, fl in cands]},
                      open("solved_multi.json", "w"))
            break
