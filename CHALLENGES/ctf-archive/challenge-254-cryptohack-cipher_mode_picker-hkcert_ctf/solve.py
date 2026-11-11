# Mode-confusion: CFB(seg128) with all-zero plaintext == OFB keystream recursion.
# cfb 00*80 -> KS; ofb flag -> ct; flag = ct ^ KS.
import sys, socket

def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))

def solve_local():
    import subprocess, os
    env = dict(os.environ, FLAG="hkcert21{" + "A" * 70 + "}")
    p = subprocess.Popen([sys.executable, "chall.py"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
    def cmd(line):
        # prompt '> ' has no newline, so it glues to the hex line: take last token
        p.stdin.write((line + "\n").encode()); p.stdin.flush()
        return bytes.fromhex(p.stdout.readline().decode().split()[-1])
    ks = cmd("cfb data " + "00" * 80)
    ct = cmd("ofb flag")
    return xor(ct, ks)

def solve_remote(host="archive.cryptohack.org", port=2951):
    s = socket.create_connection((host, port), timeout=30); s.settimeout(25)
    buf = b""
    def readline():
        nonlocal buf
        while b"\n" not in buf:
            d = s.recv(65536)
            if not d: break
            buf += d
        i = buf.index(b"\n"); line, buf = buf[:i], buf[i+1:]
        return line.decode().strip()
    def cmd(line):
        # prompt '> ' has no newline: it glues to the following hex line
        s.sendall((line + "\n").encode())
        return bytes.fromhex(readline().split()[-1])
    ks = cmd("cfb data " + "00" * 80)
    ct = cmd("ofb flag")
    return xor(ct, ks)

if __name__ == "__main__":
    flag = solve_local() if "--local" in sys.argv else solve_remote()
    print("FLAG:", flag.decode(errors="replace"))
