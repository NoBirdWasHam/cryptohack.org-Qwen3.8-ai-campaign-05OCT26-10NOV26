import socket, json, sys

def recv_line(s, timeout=25):
    buf = b''
    s.settimeout(timeout)
    while not buf.endswith(b'> '):
        c = s.recv(4096)
        if not c:
            break
        buf += c
    return buf

def main():
    s = socket.create_connection(('archive.cryptohack.org', 36161), timeout=20)
    banner = recv_line(s)
    out = {'banner': banner.decode(errors='replace')}
    def q(line):
        s.sendall((line + '\n').encode())
        r = recv_line(s)
        return r.decode(errors='replace').strip()
    out['ark_sec'] = q('ark secret')
    out['sb_zero'] = q('sb data ' + '00'*16)
    out['sb_sec'] = q('sb secret')
    out['mc_zero'] = q('mc data ' + '00'*16)
    out['mc_sec'] = q('mc secret')
    out['sr_zero'] = q('sr data ' + '00'*16)
    out['sr_sec'] = q('sr secret')
    s.close()
    json.dump(out, open('collect.json', 'w'), indent=1)
    for k, v in out.items():
        print(k, v[:120])

if __name__ == '__main__':
    main()
