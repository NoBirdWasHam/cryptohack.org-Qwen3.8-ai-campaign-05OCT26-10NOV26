
p = 2^110 * 3^67 - 1;
ea = 110; eb = 67;
f2 = ffinit(p, 2, 'x);
w = ffgen(f2, 'w);
a1 = lift(polcoeff(f2, 1)) % p;
a0 = lift(polcoeff(f2, 0)) % p;
D = (a1*a1 - 4*a0) % p;
beta = lift(sqrt(Mod(-4, p) / Mod(D, p)));
alpha = (a1 * beta * ((p+1) \ 2)) % p;
i_gp = Mod(alpha, p) + Mod(beta, p)*w;
if(lift(i_gp^2) != p-1, print("BAD i basis"));
P2x = Mod(57638278144985143549644316704182130279784191379170896458696787312, p) + Mod(118242575052254473701407051403380184157502700009529430046122822477, p)*i_gp;
P2y = Mod(35228327576503752484578273317308597612913304063200715424014549037, p) + Mod(80915735815367072410310689908590367651933218830435520913424043510, p)*i_gp;
Q2x = Mod(101349537690838191347553037323956940169953967852439843389873653018, p) + Mod(27856673727210297071672501895829918842041821446996051944738115273, p)*i_gp;
Q2y = Mod(76499786039494489791183573966490259392789635716963920208794989512, p) + Mod(45955772915614774101614751673022340983778200451506382887743008335, p)*i_gp;
P3x = Mod(63162905189208938201083385603424075109355856156240516441321158383, p) + Mod(68702305424425607424554396971378391833152415806389206440833676844, p)*i_gp;
P3y = Mod(110903430163815016394569999096524527007769669322432532390635606190, p) + Mod(14452401602439328239712793251073780692192036710425129093829067649, p)*i_gp;
Q3x = Mod(39165103284419354968504615023980382940222714919046676966425620242, p) + Mod(50967992419888058158544483269655763559879646024537212566396940681, p)*i_gp;
Q3y = Mod(74814862075401178218909769629701747112662266906635780085603780902, p) + Mod(113476160032430656302485251779124302915433268423829474022852380544, p)*i_gp;

P2 = [P2x, P2y]; Q2 = [Q2x, Q2y]; P3 = [P3x, P3y]; Q3 = [Q3x, Q3y];
sA = 225902606209514408534212339057054; sB = 38410379124791756271891302485727;
E0 = ellinit([Mod(1,p) + 0*w, Mod(0,p) + 0*w]);
\\ generic isogeny chain: kernel <R> of order ell^e; track images of extras
chain(E, R, ell, e, extras) = {
  my(n = #extras);
  for(i=1, e,
    if(1,
      Q = ellmul(E, R, ell^(e-i));
      iso = ellisogeny(E, Q);
      R = ellisogenyapply(iso[2], R);
      for(j=1, n, extras[j] = ellisogenyapply(iso[2], extras[j]));
      E = ellinit(iso[1])
    )
  );
  [E, R, extras]
}
RA = elladd(E0, P2, ellmul(E0, Q2, sA));
RB = elladd(E0, P3, ellmul(E0, Q3, sB));
resA = chain(E0, RA, 2, ea, [P3, Q3]);
EA = resA[1]; P3A = resA[3][1]; Q3A = resA[3][2];
jinv(E) = { 6912 * E.a4^3 / (4*E.a4^3 + 27*E.a6^2) };
print("Alice done");
resB = chain(E0, RB, 3, eb, [P2, Q2]);
EB = resB[1]; P2B = resB[3][1]; Q2B = resB[3][2];
print("Bob done");
RA2 = elladd(EB, P2B, ellmul(EB, Q2B, sA));
resAB = chain(EB, RA2, 2, ea, []);
jAB = jinv(resAB[1]);
print("EAB done");
RB2 = elladd(EA, P3A, ellmul(EA, Q3A, sB));
resBA = chain(EA, RB2, 3, eb, []);
jBA = jinv(resBA[1]);
print("EBA done");
if(jAB != jBA, print("MISMATCH"));
print("JW ", jAB);
print("ALPHA ", alpha);
print("BETA ", beta);
