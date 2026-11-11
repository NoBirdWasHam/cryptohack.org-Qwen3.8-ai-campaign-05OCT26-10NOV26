import socket
s = socket.create_connection(('archive.cryptohack.org', 14846), timeout=25)
s.settimeout(10)
def rd(n=65536):
    try: return s.recv(n)
    except Exception as e: return b'<TO>'
buf = b''
for _ in range(3):
    d = rd()
    if d == b'<TO>' or d == b'': buf += d; break
    buf += d
print('BANNER len', len(buf))
print('REPR head', repr(buf[:60]))
print('REPR tail', repr(buf[-80:]))
print('lines:', [l[:30] for l in buf.split(b'\n') if l][:10])
s.sendall(b'0\n')
print('after1:', rd()[:200])
s.sendall(b''.join(b'%d\n' % i for i in range(1,20)))
print('after20:', rd()[:400])
s.sendall(b'0\n')
print('afterguess:', rd()[:200])
s.close()
