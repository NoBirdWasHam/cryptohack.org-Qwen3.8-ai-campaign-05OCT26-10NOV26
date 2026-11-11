default(parisize, "6g");
read("params.gp");
F = ffinit(PVAL, 2);
W = ffgen(F, 'W);
o1 = W^0; z0 = W*0;
ffsqrt_ts(r) = { local(q, e, mm, z, c, x, t, i, b); if(r == 0, return(z0)); q = PVAL^2; if(r^((q-1)>>1) != o1, return(-1)); e = valuation(q-1, 2); mm = (q-1) >> e; z = W; while(z^((q-1)>>1) == o1, z = z+1); c = z^mm; x = r^((mm+1)>>1); t = r^mm; while(t != o1, i = 0; b = t; while(b != o1, b = b^2; i = i+1); b = c^(2^(e-i-1)); c = b^2; x = x*b; t = t*c); return(x); }
mk(re, im) = { re + im*I2 };
DATA = read("bytes.gp");
MVAL = PVAL + 1;
I2 = ffsqrt_ts(-1 + z0);
d0 = DATA[1];
Ax = mk(d0[1], d0[2]); Ay = mk(d0[3], d0[4]); Bx = mk(d0[5], d0[6]); By = mk(d0[7], d0[8]);
RA = Ay^2 - Ax^3; RB = By^2 - Bx^3;
a4 = (RA - RB)/(Ax - Bx); a6 = RA - a4*Ax;
Ep = ellinit([0,0,0,a4,a6]);
A = [Ax, Ay]; B = [Bx, By]; OP = ellmul(Ep, A, 0);
for(j = 1, 3, l = PR[j]; e = EE[j]; print("l=", l, " e=", e); for(k = 1, min(KM[j], 7), sc = 37*LVAL*MVAL/l^(e+k); Xk = ellmul(Ep, A, sc); Yk = ellmul(Ep, B, sc); ox = (Xk == OP); oy = (Yk == OP); pv = if(ox || oy, -1, ellweilpairing(Ep, Xk, Yk, l^k) == o1); print("  k=", k, " X=O:", ox, " Y=O:", oy, " pair==1:", pv); ));
