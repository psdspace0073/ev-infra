[out:json][timeout:900][maxsize:1073741824];
area["ISO3166-2"="IN-KA"]["admin_level"="4"]->.ka;
nwr["amenity"~"^(parking|motorcycle_parking)$"](area.ka);
out center tags;
