# generate A.gp (256x512 binary), cvecs.gp (7 c-vectors) from live session output
import ast, hashlib, os
d = os.path.dirname(os.path.abspath(__file__))
txt = open(os.path.join(d, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha512(secret).digest(); pub = []
for _ in range(256):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha512(state).digest()
rows = []
for j in range(256):
    x = pub[j]
    rows.append(','.join(str((x >> (511 - k)) & 1) for k in range(512)))
open(os.path.join(d, 'A.gp'), 'w').write('A = [' + ';'.join(rows) + '];\n')
lines = []
for bi, blk in enumerate(enc, 1):
    lines.append(f'c{bi} = [' + ','.join(str(v) for v in blk) + '];')
open(os.path.join(d, 'cvecs.gp'), 'w').write('\n'.join(lines) + f'\nNB = {len(enc)};\n')
print('wrote A.gp', len(rows), 'x512; blocks', len(enc))
