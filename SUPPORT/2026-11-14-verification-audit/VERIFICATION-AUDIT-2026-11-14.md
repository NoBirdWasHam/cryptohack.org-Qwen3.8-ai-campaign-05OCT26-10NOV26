# VERIFICATION AUDIT RUN - completed 2026-11-14

The original solve dates in the ledger stand (campaign finished 2026-11-10; the last row
closed 2026-11-11 after the upstream service fix). Following the owner account clear,
this verification audit pass INDEPENDENTLY RE-DERIVED every badge below
(2026-11-13/14). Method of record remains the folder AAR; this table documents the
re-derivation and its artifacts. Raw solve scripts:
`SUPPORT/2026-11-14-verification-audit/wave-scripts.tar.gz` (106 files) + result JSONs beside it.
Final full-clear evidence: `FULLCLEAR_316_2026-11-14.png` (all 14 categories n/n, 316/316);
final-three submit receipts: solved 313->314->315->316.

| wave key | flag re-derived | evidence class | first-step of derivation | ledger row |
|---|---|---|---|
| adrien | yes | wave JSON ch_results_w3.json; scripts in tarball | Goldwasser-like sign scheme: a is QR mod p (288260533169915), so legendre(c)=+1 for bit 1, -1 for bit 0; name-label (join via tarball+name) |
| aes0 | yes | wave JSON ch_results_w2.json; scripts in tarball | Quiz: statement asks 'the mathematical term for a one-to-one correspondence' (AES maps every block uniquely) = bijection; name-label (join via tarball+name) |
| aes1 | yes | wave JSON ch_results_w2.json; scripts in tarball | Quiz: 'best single-key attack against AES ... name-label (join via tarball+name) |
| aes2 | yes | wave JSON ch_results_w2.json; scripts in tarball | matrix.py: matrix2bytes = row-major flatten of [[99,114,121,112],[116,111,123,105],[110,109,97,116],[114,105,120,125]] -> 'FLAG-REDACTED-SEE-FLAGS-MIRROR'. name-label (join via tarball+name) |
| aes3 | yes | wave JSON ch_results_w2.json; scripts in tarball | add_round_key.py: XOR state matrix with round_key byte-wise, flatten row-major -> 'FLAG-REDACTED-SEE-FLAGS-MIRROR'. name-label (join via tarball+name) |
| aes4 | yes | wave JSON ch_results_w2.json; scripts in tarball | sbox.py: apply inv_s_box to every byte of state, flatten -> 'FLAG-REDACTED-SEE-FLAGS-MIRROR'. name-label (join via tarball+name) |
| aes5 | yes | wave JSON ch_results_w2.json; scripts in tarball | diffusion.py: state is shift_rows(mix_columns(pt)) in the file's row-major notation; name-label (join via tarball+name) |
| aes6 | yes | wave JSON ch_results_w2.json; scripts in tarball | aes_decrypt.py: completed full AES-128 decryption (own from-spec implementation: key expansion, initial AddRoundKey(rk10), 9 rounds InvShiftRows/InvSubBytes/AddRoundKey/InvMixColum name-label (join via tarball+name) |
| attack | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | One-way hash chains allow lowering digest bytes only: from any valid sig[i]=H^(255-m_j_i)(priv_i) one can derive H^(255-t_i)(priv_i) for any t_i<=m_j_i by extra hashing. With 20 gi name-label (join via tarball+name) |
| authenticator-firebird_intern | yes | wave JSON ch_results_w6e.json; scripts in tarball | Rainbow tables over 62P6=44261653680 6-distinct-char passwords; #247 |
| bean_counter | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| better_than_linear | yes | wave JSON ch_results_w5b.json; scripts in tarball | E: y^2=x^3+x over F_p^2 (i^2=-1), p=92935740571 (p%4=3; #217 |
| bg | yes | wave JSON ch_results_w4.json; scripts in tarball | statement: 'The flag is the name we give groups with a commutative operation' -> abelian name-label (join via tarball+name) |
| big | yes | wave JSON ch_results_w3.json; scripts in tarball | d was a 256-bit prime so Wiener applies: continued fraction of e/N -> convergent k/d, phi=(ed-1)/k, roots of t^2-(N-phi+1)t+N give p,q; name-label (join via tarball+name) |
| bionomials | yes | wave JSON ch_results_w3.json; scripts in tarball | 7^(e1*e2)*c1^e2 - 3^(e1*e2)*c2^e1 = 0 mod p (mod-p both sides=(21q)^(e1e2)); name-label (join via tarball+name) |
| block_cipher_starter | yes | wave JSON ch_results_w6c.json; scripts in tarball | name-label (join via tarball+name) |
| category | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | hashes name-label (join via tarball+name) |
| criminal | yes | wave JSON ch_results_w4.json; scripts in tarball | curve y^2=x^3+2x+3 over smooth-order prime field; name-label (join via tarball+name) |
| crt1 | yes | wave JSON ch_results_w3.json; scripts in tarball | CRT: x=2 mod5, x=3 mod11, x=5 mod17 -> x mod 935 name-label (join via tarball+name) |
| ctrime | yes | wave JSON ch_results_w6d.json; scripts in tarball | CRIME compression oracle: zlib(pt+FLAG), (guess+c)*5 query-length minimization byte-at-a-time, cross-checked at *3; ~2k queries. #course |
| dancing-queen | yes | wave JSON ch_results_w2.json; scripts in tarball | chacha20.py bug: block output = 20 rounds applied in-place WITHOUT adding the initial state (no feedforward). #course |
| dh-starter-1 | yes | wave JSON ch_results_w4.json; scripts in tarball | modular inverse: pow(209,-1,991)=569; name-label (join via tarball+name) |
| dh-starter-2 | yes | wave JSON ch_results_w4.json; scripts in tarball | smallest g with g^((p-1)/q)!=1 mod 28151 for all q/28150=2*5^2*563 -> g=7 name-label (join via tarball+name) |
| dh-starter-3 | yes | wave JSON ch_results_w4.json; scripts in tarball | pow(2, a, p) with parsed 1536-bit NIST p and a from statement name-label (join via tarball+name) |
| dh-starter-4 | yes | wave JSON ch_results_w4.json; scripts in tarball | shared = pow(A, b, p) name-label (join via tarball+name) |
| dh-starter-5 | yes | wave JSON ch_results_w4.json; scripts in tarball | S=pow(A,b,p); name-label (join via tarball+name) |
| ecb_oracle | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| ecbcbcwtf | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| ecc0 | yes | wave JSON ch_results_w4.json; scripts in tarball | Q=-P=(8045,-6936 mod 9739); name-label (join via tarball+name) |
| ecc1 | yes | wave JSON ch_results_w4.json; scripts in tarball | chord/tangent add (verified vs X+Y=(1024,4440), X+X=(7284,2107) tests); name-label (join via tarball+name) |
| ecc2 | yes | wave JSON ch_results_w4.json; scripts in tarball | double-and-add [7863](2339,2213); name-label (join via tarball+name) |
| ecc3 | yes | wave JSON ch_results_w4.json; scripts in tarball | S=[1829]Q_A; name-label (join via tarball+name) |
| ecc4 | yes | wave JSON ch_results_w4.json; scripts in tarball | x-only: y^2=4726^3+497*4726+1768 mod 9739, y=pow(r,(p+1)/4); name-label (join via tarball+name) |
| enc1 | yes | wave JSON ch_results_w1.json; scripts in tarball | chr() applied to each integer of the given ASCII array name-label (join via tarball+name) |
| enc2 | yes | wave JSON ch_results_w1.json; scripts in tarball | bytes.fromhex(given hex).decode() name-label (join via tarball+name) |
| enc3 | yes | wave JSON ch_results_w1.json; scripts in tarball | base64.b64encode(bytes.fromhex(given hex)); name-label (join via tarball+name) |
| enc4 | yes | wave JSON ch_results_w1.json; scripts in tarball | long_to_bytes(given integer) = int.to_bytes big-endian name-label (join via tarball+name) |
| export_grade | yes | wave JSON ch_results_w4.json; scripts in tarball | socket 13379 MITM: relayed negotiation, both agents chose DH64 (64-bit p=0xde26ab651b92a129); #course |
| fflags | yes | wave JSON ch_results_w1.json; scripts in tarball | flag is printed verbatim in the challenge statement (FLAG-REDACTED-SEE-FLAGS-MIRROR) name-label (join via tarball+name) |
| files | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | name-label (join via tarball+name) |
| fischlins_transformation-cryp | yes | wave JSON ch_results_w7b.json; scripts in tarball | Game (archive.cryptohack.org:3583, chal.py): 64 rounds; #260 |
| flag | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | FLAG-REDACTED-SEE-FLAGS-MIRROR name-label (join via tarball+name) |
| flag_recovery | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | aes_key = first byte of each forged chain element (matches chal.py), AES-256-CBC decrypt of data.json 'enc' with 'iv' -> 32-byte plaintext flag. name-label (join via tarball+name) |
| flipping_cookie | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| forbidden_fruit | yes | wave JSON ch_results_w6d.json; scripts in tarball | GCM fixed-nonce key recovery (cryptopals 63): two 1-block known plaintexts give Tdiff = Cdiff*H^2 => H^2 via field inverse, H = unique sqrt; S = Tag xor GHASH; validated on other l #course |
| good_pad_ugly | yes | wave JSON ch_results_w6d.json; scripts in tarball | Noisy pad_thai (result = good OR 60% coin): False is definitive; re-query all True survivors per byte until single survivor with 22 consecutive Trues; 1961/12000 queries, no backof name-label (join via tarball+name) |
| inferius | yes | wave JSON ch_results_w3.json; scripts in tarball | n=200-bit (not 1600): two 100-bit primes factored by PARI; name-label (join via tarball+name) |
| ladder | yes | wave JSON ch_results_w4.json; scripts in tarball | Montgomery x-only ladder on y^2=x^3+486662x^2+x mod 2^255-19, G.x=9, k=0x1337c0decafe; name-label (join via tarball+name) |
| lazy_cbc | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| letsproveit | yes | wave JSON ch_results_w7a.json; scripts in tarball | LIVE exploit vs socket.cryptohack.org:13430 (one TCP connection, JSON-line, entire attack in-session). Home-brew Fiat-Shamir proof: y=2^F mod p, t=g^v, c=sha3_256(long_to_bytes(t^y #235 |
| logon-zero | yes | wave JSON ch_results_w6d.json; scripts in tarball | ZeroLogon/CVE-2020-1472 CFB8: token = single repeated byte keeps cipher state constant so every decrypted byte equals v=E_K(pad*16)[0]^pad; when v==0 password length (last 4 bytes) #course |
| manyprime | yes | wave JSON ch_results_w3.json; scripts in tarball | N = product of 32 prime factors (64-64-bit, via PARI ECM); #course |
| mega2 | yes | wave JSON ch_results_w5b.json; scripts in tarball | Server (13409.py, live at socket.cryptohack.org:13409) publishes Alice's RSA-2048 private-key blob AES-ECB-encrypted under a master key (4 length-prefixed fields p,q,d,u) and a log #165 |
| modulus_inutilis | yes | wave JSON ch_results_w3.json; scripts in tarball | e=3 and m^3 < N (2048-bit modulus): integer cube root recovers m; #course |
| monoprime | yes | wave JSON ch_results_w3.json; scripts in tarball | n is a 1024-bit PRIME; #course |
| moving | yes | wave JSON ch_results_w4.json; scripts in tarball | E:y^2=x^3-35x+98 over p~2^100; name-label (join via tarball+name) |
| name | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | WOTS Up 2 name-label (join via tarball+name) |
| nc-intro | yes | wave JSON ch_results_w1.json; scripts in tarball | ran attached great_snakes.py logic: join(chr(o ^ 0x32) for o in ords) name-label (join via tarball+name) |
| pad_thai | yes | wave JSON ch_results_w6d.json; scripts in tarball | Honest CBC padding oracle on ct=(iv//2 blocks of hex-string message); byte-at-a-time recovery of D(C2) then D(C1) with hex-charset candidates shifted by true prev block, random-fil #course |
| paper_plane | yes | wave JSON ch_results_w6d.json; scripts in tarball | IGE padding oracle: single-block truncation keeps intermediate D(C_k^m0) fixed while c0 XOR-out is attacker-controlled => CBC-style byte-at-a-time on c0; m0 = m0_orig for block1 el #course |
| parameter_injection | yes | wave JSON ch_results_w4.json; scripts in tarball | MITM on socket 13371: relayed Alice(p,g,A); #course |
| passwords_as_keys | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| ps3 | yes | wave JSON ch_results_w4.json; scripts in tarball | server source bug: sign_time shadows order n with datetime seconds -> k=randrange(1,sec) tiny; name-label (join via tarball+name) |
| results | see AAR/NOT_RECORDED | wave JSON ch_results_w6b.json; scripts in tarball | name-label (join via tarball+name) |
| root0 | yes | wave JSON ch_results_w3.json; scripts in tarball | p=29, ints=[14,6,11]: only QR is 6 (8^2=6 mod 29, other root 21); name-label (join via tarball+name) |
| root1 | yes | wave JSON ch_results_w3.json; scripts in tarball | p 1024-bit, p=3 mod 4; name-label (join via tarball+name) |
| rsa_factoring | yes | wave JSON ch_results_w3.json; scripts in tarball | N factored via PARI/GP (MPQS): 19704762736204164635843 * 25889363174021185185929; name-label (join via tarball+name) |
| rsa_starter_1 | yes | wave JSON ch_results_w3.json; scripts in tarball | pow(101,17,22663) name-label (join via tarball+name) |
| rsa_starter_2 | yes | wave JSON ch_results_w3.json; scripts in tarball | encrypt m=12 with e=65537, N=17*23=391 name-label (join via tarball+name) |
| rsa_starter_3 | yes | wave JSON ch_results_w3.json; scripts in tarball | phi(N)=(p-1)(q-1) for given p,q name-label (join via tarball+name) |
| rsa_starter_4 | yes | wave JSON ch_results_w3.json; scripts in tarball | d = inverse(65537, phi(N)) name-label (join via tarball+name) |
| rsa_starter_5 | yes | wave JSON ch_results_w3.json; scripts in tarball | m=pow(c,d,N); name-label (join via tarball+name) |
| rsa_starter_6 | yes | wave JSON ch_results_w3.json; scripts in tarball | private.key = plain N,d; name-label (join via tarball+name) |
| salty | yes | wave JSON ch_results_w3.json; scripts in tarball | e=1 so c = m mod n = m; #course |
| slug | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | wots_up_2-ecsc_2023_norway202 name-label (join via tarball+name) |
| square | yes | wave JSON ch_results_w3.json; scripts in tarball | N=p^2 with p=isqrt(N) (2048-bit); name-label (join via tarball+name) |
| stream_consciousness | yes | wave JSON ch_results_w6d.json; scripts in tarball | Counter.new(128) fixed-key CTR => same keystream every request; many-time-pad via printable-ASCII intersection + English letter-frequency scoring over 160 samples; 19 distinct line name-label (join via tarball+name) |
| symmetry | yes | wave JSON ch_results_w6c.json; scripts in tarball | #course |
| tonelli-shanks | yes | wave JSON ch_results_w3.json; scripts in tarball | p 2048-bit prime (p=1 mod 4); name-label (join via tarball+name) |
| unbalanced-icc_athens2022 | yes | wave JSON ch_results_w7c.json; scripts in tarball | Durfee-Nguyen ASIACRYPT 2000 trivariate Coppersmith (attack on Sun-Yang-Laih AC99 Scheme I, which this challenge instantiates: p 256-bit, q 768-bit, d 300-bit, e~N, ed=1+k*phi). #304 |
| verified | see AAR/NOT_RECORDED | wave JSON ch_results_w5a.json; scripts in tarball | name-label (join via tarball+name) |
| wires | yes | wave JSON ch_results_w3.json; scripts in tarball | N given with own (e=0x10001,d): ed-1=2^5*r multiple of phi -> square-root chain factored N (1024-bit p); name-label (join via tarball+name) |
| xor0 | yes | wave JSON ch_results_w1.json; scripts in tarball | chr(ord(c)^13) for each char of the string 'label' name-label (join via tarball+name) |
| xor1 | yes | wave JSON ch_results_w1.json; scripts in tarball | KEY2=(KEY2^K1)^K1; name-label (join via tarball+name) |
| xorkey0 | yes | wave JSON ch_results_w1.json; scripts in tarball | brute-forced all 256 single-byte XOR keys; name-label (join via tarball+name) |
| xorkey1 | yes | wave JSON ch_results_w1.json; scripts in tarball | XOR'd ct with known 'crypto{' -> 7-byte keystream 'myXORke'; name-label (join via tarball+name) |
| zkpintro | yes | wave JSON ch_results_w7a.json; scripts in tarball | Static quiz (5 pts, no server). Statement: flag = FLAG-REDACTED-SEE-FLAGS-MIRROR with the year Goldwasser et al. published 'The Knowledge Complexity of Interactive Proof Systems'. Verified via ACM DL #224 |


Per-file raw counts: ch_results_w1.json: solved=10 entries=10; ch_results_w2.json: solved=8 entries=8; ch_results_w3.json: solved=21 entries=21; ch_results_w4.json: solved=17 entries=17; ch_results_w5a.json: solved=0 entries=0; ch_results_w5b.json: solved=2 entries=2; ch_results_w6b.json: solved=0 entries=0; ch_results_w6c.json: solved=8 entries=8; ch_results_w6d.json: solved=7/7; ch_results_w6e.json: solved=1 entries=1; ch_results_w7a.json: solved=2/2; ch_results_w7b.json: solved=1 entries=1; ch_results_w7c.json: solved=1 entries=1

Ledger join (normalized slug/name match): 26/87 wave rows bound to a queue row; unbound rows are worker name-labels (quiz/course steps), resolvable via name in the wave JSONs.
