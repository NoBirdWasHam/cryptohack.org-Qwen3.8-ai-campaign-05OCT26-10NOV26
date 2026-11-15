default(parisize,"1g"); \ 
print(VERSION);
\ \ 
print("has ellTate: ", if(strsearch(help("ellTate"), "not a function") > 0, 0, 1));
