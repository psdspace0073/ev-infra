[out:json][timeout:900][maxsize:1073741824];
area["ISO3166-2"="IN-KA"]["admin_level"="4"]->.ka;
way["highway"~"^(motorway|trunk|primary|secondary|tertiary)(_link)?$"](area.ka);
out geom;
