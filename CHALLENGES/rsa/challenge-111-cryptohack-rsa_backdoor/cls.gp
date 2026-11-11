D = -427;
print("h(-427) = ", qfbclassno(D));
print("h(4*D) = ", qfbclassno(4*D));
print("h(-1708) = ", qfbclassno(-1708));
G = qfbclassgroup(D);
print("class group params: ", G);
print("bnf struct: ", bnfinit(x^2+427).no);
/* is [1,1,107] reduced? disc = 1 - 428 = -427 */
f = Qfb(1,1,107);
print("order of [1,1,107]: ", qfborder(G, f));
print("pow h: ", qfbpow(G, f, qfbclassno(D)));
