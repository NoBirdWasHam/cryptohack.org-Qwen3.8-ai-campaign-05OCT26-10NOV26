p = 419;
E0 = ellinit(Mod([1,0], p));
print("E0: j = ", lift(E0[13]), " card = ", ellcard(E0));

points_of(E) = {
  my(a1 = E[1], a2 = E[2], a3 = E[3], a4 = E[4], a6 = E[5],
     L = [], x, y, B, C, D, sq, B1, B2, inv2 = Mod(2, p)^(-1));
  for (x = 0, p-1,
    B = (a1*x + a3) % p;
    C = (-(x^3 + a2*x^2 + a4*x + a6)) % p;
    D = (B^2 - 4*C) % p;
    for (y = 0, (p-1)/2,
      sq = Mod(y^2, p);
      if (sq == Mod(D, p),
        B1 = (-B + y) * inv2 % p;
        B2 = (-B - y) * inv2 % p;
        L = concat(L, [[Mod(x, p), Mod(B1, p)]]);
        if (B2 != B1, L = concat(L, [[Mod(x, p), Mod(B2, p)]]));
      );
    );
  );
  L
}

krnl(E, l) = {
  my(pts = points_of(E), S = [], i);
  for (i = 1, #pts,
    if (#ellmul(E, pts[i], l) == 1, S = concat(S, [pts[i]]));
  );
  S
}

is_iso_E0(E) = (lift(E[5]) == 0 && lift(Mod(lift(E[4]), p)^((p-1)/2)) == 1)

chain7() = {
  my(E = E0, d, S, ph);
  for (d = 1, 30,
    S = krnl(E, 7);
    ph = ellisogeny(E, S[1]);
    E = ellinit(ph[1]);
    print("d=", d, " a4=", lift(E[4]), " a6=", lift(E[5]), " j=", lift(E[13]), " card=", ellcard(E), " isoE0=", is_iso_E0(E));
    if (is_iso_E0(E), break);
  );
}

chain5() = {
  my(E = E0, d, S, ph);
  for (d = 1, 9,
    S = krnl(E, 5);
    ph = ellisogeny(E, S[1]);
    E = ellinit(ph[1]);
    print("d=", d, " a4=", lift(E[4]), " a6=", lift(E[5]), " j=", lift(E[13]), " isoE0=", is_iso_E0(E));
  );
}

print("=== 7-chain ===");
chain7();
print("=== 5-chain ===");
chain5();
