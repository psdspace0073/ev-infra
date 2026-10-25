[out:json][timeout:900][maxsize:1073741824];
area["ISO3166-2"="IN-KA"]["admin_level"="4"]->.ka;
nwr["power"~"^(plant|substation|generator|transformer|switch|compensator|converter)$"](area.ka);
out center tags;
