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
A = [Ax, Ay];
Z2 = ellmul(Ep, A, 2);
Z2p = [mk(4882229290345458793326693606293958879849613238768213262758758948448186946586252093527946636805812615623909308928786333701894924443, 840877806051021943644810098734274432809271693159218409067328590011393662768549229323438669494097945770904739478287240126290442545), mk(4765660410226957632747926008683580249536905222332711322810042719022591002446707099947553118211023147176416513026215199523880016333, 4798779304651017778427606090616071204166180218755417132267085485377628136818012793090634135804896626614166081205324929636075176427)];
print("GP [2]A == python [2]A: ", Z2 == Z2p);
Z3 = ellmul(Ep, A, 3);

U = 37*LVAL*MVAL; while(U % 2 == 0, U = U \ 2);
X1 = ellmul(Ep, A, U*2^70);
print("GP X1 == O: ", X1 == ellmul(Ep, A, 0));
ordA2 = ellmul(Ep, A, U);
print("GP [U]A: O?", ordA2 == ellmul(Ep, A, 0), " [2U]A: O?", ellmul(Ep, ordA2, 2) == ellmul(Ep, A, 0));
