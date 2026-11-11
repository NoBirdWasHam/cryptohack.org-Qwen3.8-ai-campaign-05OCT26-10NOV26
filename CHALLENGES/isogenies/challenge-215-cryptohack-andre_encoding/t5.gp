for(idx = 1, 2,
  res = 0;
  forstep(k = 3, 1, -1,
    if(res == 0,
      if(k == 2, res = -k, res = k);
    );
  );
  print(res);
);
