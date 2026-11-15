import os, re, json, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import solve as S
D = S.D
conn = S.Local()
n = S.grab_int(conn.line()); g = S.grab_int(conn.line())
print('n bits', n.bit_length(), 'g bits', g.bit_length())
n2 = n*n
c0 = S.grab_int(conn.line())
print('c0 bits', c0.bit_length())
for (K, t) in D['qs'][:4]:
    delta = (K << 1024) | t
    conn.send(str(c0 * pow(pow(g, delta, n2), -1, n2) % n2))
for _ in range(4):
    print('resp:', repr(conn.line()))
conn.close()
