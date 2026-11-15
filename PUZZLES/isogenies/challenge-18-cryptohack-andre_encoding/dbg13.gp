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
for(idx = 1, 4, d0 = DATA[idx]; Ax = mk(d0[1], d0[2]); Ay = mk(d0[3], d0[4]); Bx = mk(d0[5], d0[6]); By = mk(d0[7], d0[8]); RA = Ay^2 - Ax^3; RB = By^2 - Bx^3; a4 = (RA - RB)/(Ax - Bx); a6 = RA - a4*Ax; Ep = ellinit([0,0,0,a4,a6]); A = [Ax, Ay]; B = [Bx, By]; OP = ellmul(Ep, A, 0); U = 37*LVAL*MVAL; while(U % 2 == 0, U = U \ 2); for(lam = 1, 2, AB = elladd(Ep, A, ellmul(Ep, B, lam)); res = 0; forstep(k = 7, 1, -1, if(res == 0, sc = U*2^(71-k); Xk = ellmul(Ep, AB, sc); Yk = ellmul(Ep, B, sc); if(Xk == OP, res = -k, if(ellweilpairing(Ep, Xk, Yk, 3*2^k) == o1, res = k)))); print("byte ", idx, " lam=", lam, " res=", res); ));
