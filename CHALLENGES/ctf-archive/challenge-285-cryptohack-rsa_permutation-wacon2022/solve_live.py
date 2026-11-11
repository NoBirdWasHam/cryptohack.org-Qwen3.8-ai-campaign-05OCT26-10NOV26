# Live solver: archive.cryptohack.org:45400 rsa_permutation-wacon2022
import socket, hashlib, string, subprocess, sys, time, os, re

HOST, PORT = 'archive.cryptohack.org', 45400

def rd(f, timeout=10):
    f.settimeout(timeout)
    try:
        return f.recv(65536).decode(errors='replace')
    except socket.timeout:
        return ''

def main():
    s = socket.create_connection((HOST, PORT), timeout=20)
    f = s.makefile('rb')
    def rdline(t=10):
        f.settimeout(t)
        try:
            return f.readline().decode(errors='replace')
        except socket.timeout:
            return ''
    print("banner:", rdline().strip())   # "Solve PoW plz"
    chal = rdline().strip()
    print("pow challenge:", chal)
    t0 = time.time()
    ans = 0
    while True:
        a = string.digits + string.ascii_lowercase
        cand = str(ans)
        if hashlib.sha256((chal + cand).encode()).hexdigest()[:6] == '000000':
            break
        ans += 1
        if ans % 2000000 == 0:
            ans2 = ''.join(__import__('random').choice(a) for _ in range(12))
            if hashlib.sha256((chal + ans2).encode()).hexdigest()[:6] == '000000':
                cand = ans2; break
            continue
        if time.time() - t0 > 240:
            print("pow timeout"); sys.exit(1)
    print("pow answer:", cand, f"({time.time()-t0:.1f}s)")
    s.sendall((cand + '\n').encode())
    n = int(rdline(15).strip())
    sp = rdline(15).strip()
    sq = rdline(15).strip()
    print("n bits:", n.bit_length(), "len sp,sq:", len(sp), len(sq))
    assert len(sp) == 256 and len(sq) == 256
    open('live_instance.txt', 'w').write(str(n) + '\n' + sp + '\n' + sq + '\n')
    print("running DP...")
    t0 = time.time()
    r = subprocess.run(['./dp4.exe', 'live_instance.txt'], capture_output=True, text=True, timeout=550, cwd=os.getcwd())
    out = r.stdout
    print("dp done in", time.time() - t0, "s; solutions:", out.count('SOLUTION'))
    m = re.search(r'p=([0-9a-f]+)', out)
    if not m:
        print("NO SOLUTION:", r.stderr[-500:]); sys.exit(2)
    p = int(m.group(1), 16)
    assert n % p == 0, "p does not divide n!"
    q = n // p
    print("factored ok; sending u,v")
    s.sendall((str(p) + '\n').encode())
    s.sendall((str(q) + '\n').encode())
    time.sleep(2)
    resp = rdline(20) + rdline(5)
    print("RESPONSE:", resp.strip())
    open('flag_raw.txt', 'w').write(resp)
    s.close()

main()
