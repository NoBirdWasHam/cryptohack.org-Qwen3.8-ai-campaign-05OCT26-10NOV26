import socket, sys, time, subprocess, blake3, os

HERE = os.path.dirname(os.path.abspath(__file__))

def start_lookup(table):
    p = subprocess.Popen([os.path.join(HERE, 'rb2.exe'), 'serve', table],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, cwd=HERE)
    while True:
        ln = p.stderr.readline()
        if not ln or ln.startswith(b'ready'):
            break
    print('lookup server ready', flush=True)
    return p

def lookup(p, t0hex):
    p.stdin.write((t0hex + '\n').encode())
    p.stdin.flush()
    r = p.stdout.readline().decode().strip()
    return None if r == 'MISS' else r

def recv_until(sock, buf, marker, timeout=12.0):
    sock.settimeout(timeout)
    while marker not in buf:
        d = sock.recv(4096)
        if not d:
            raise EOFError(buf)
        buf += d
    return buf

def attempt(p, host, port, verbose=True):
    s = socket.create_connection((host, port), timeout=10)
    buf = b''
    try:
        buf = recv_until(s, buf, b'challenge_client = ')
        t0 = time.time()
        s.sendall(b'00' * 16 + b'\n')
        buf = recv_until(s, buf, b'response_client = ')
        txt = buf.decode(errors='replace')
        rs = cs = None
        for ln in txt.splitlines():
            if 'response_server = ' in ln:
                rs = ln.split('response_server = ')[1].split()[0]
            if 'challenge_server = ' in ln:
                cs = bytes.fromhex(ln.split('challenge_server = ')[1].split()[0])
        if rs is None:
            return None, txt
        pw = lookup(p, rs)
        if pw is None:
            if verbose: print(f'  miss in {time.time()-t0:.2f}s, reconnect', flush=True)
            return None, 'miss'
        rc = blake3.blake3(pw.encode() + b'HANDSHAKE_FROM_CLIENT' + cs).hexdigest()
        s.sendall(rc.encode() + b'\n')
        s.settimeout(8)
        out = b''
        while True:
            d = s.recv(4096)
            if not d: break
            out += d
            if b'Congrats' in out or b'Error' in out: break
        if verbose:
            print(f'  attempt {time.time()-t0:.2f}s ->', out.decode(errors='replace').strip(), flush=True)
        return pw, out.decode(errors='replace')
    finally:
        s.close()

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='archive.cryptohack.org')
    ap.add_argument('--port', type=int, default=40156)
    ap.add_argument('--table', default=os.path.join(HERE, 'rb3.bin'))
    ap.add_argument('--tries', type=int, default=25)
    args = ap.parse_args()
    p = start_lookup(args.table)
    flag = None
    for i in range(args.tries):
        print(f'--- attempt {i}', flush=True)
        try:
            pw, info = attempt(p, args.host, args.port)
        except Exception as e:
            print('  conn error:', repr(e), flush=True)
            time.sleep(1.0)
            continue
        if pw is not None and 'Congrats' in info:
            print('PASSWORD =', pw)
            print('FLAGLINE =', info.strip())
            flag = info.strip()
            break
        time.sleep(0.4)
    if flag:
        open(os.path.join(HERE, 'auth_flag.txt'), 'w').write(flag + '\n')
    p.stdin.close()
    p.terminate()
