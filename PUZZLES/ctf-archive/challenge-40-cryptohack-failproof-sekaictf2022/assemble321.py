import ast, os, hashlib
D = os.path.dirname(os.path.abspath(__file__))

def gpv(s):
    s = s.strip().rstrip(';').strip()
    if s.startswith('[') and s.endswith(']'): s = s[1:-1]
    return [int(x) for x in s.split(',')] if s.strip() else []

def read_seg(name):
    p = os.path.join(D, name)
    if not os.path.exists(p): return None
    vals = gpv(open(p).read())
    assert all(v & 1 == 0 and v < 256 for v in vals), f'bad seg encoding in {name}'
    return bytes(v >> 1 for v in vals)

txt = open(os.path.join(D, 'live_output.txt')).read().splitlines()
secret = bytes.fromhex(txt[0]); enc = ast.literal_eval(txt[1])
state = hashlib.sha256(secret).digest(); pub = []
for _ in range(128):
    pub.append(int.from_bytes(state, 'big')); state = hashlib.sha256(state).digest()

def check(mb, blk):
    x = int.from_bytes(mb, 'big')
    return all((pub[j] & x).bit_count() == enc[blk][j] for j in range(128))

seg0 = read_seg('SEG_b0free.txt')
seg1 = read_seg('SEG_mid2.txt')
tail = open(os.path.join(D, 'b2_tail.txt'), 'rb').read()  # 32 bytes, block2 ground truth
print('seg0:', seg0, '| seg1:', seg1)
if seg0: print('seg0 valid:', check(seg0, 0))
if seg1: print('seg1 valid:', check(seg1, 1))
print('tail valid:', check(tail, 2))
if seg0 and seg1:
    blob = seg0 + seg1 + tail
    flag = blob.rstrip(b'\x00')
    print('flag bytes:', flag)
    try:
        print('FLAG:', flag.decode('ascii'))
        print('len:', len(flag))
        open(os.path.join(D, 'flag.txt'), 'w').write(flag.decode('ascii'))
    except Exception as e:
        print('decode fail:', e, '— blob tail:', blob[-24:].hex())
