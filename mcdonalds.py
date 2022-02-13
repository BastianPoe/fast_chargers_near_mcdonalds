import overpy
import http.client
import json
import sys
import config

overpass_api = overpy.Overpass()

# Fetch all McDonalds in DE
result = overpass_api.query("""
[out:json];
area["ISO3166-1"="DE"][admin_level=2]->.searchArea;
(
	node[amenity=fast_food][brand="McDonald's"](area.searchArea);
);
out;
>;
    """)

all_restaurants = []

for node in result.nodes:
	if node == None:
		continue

	this_restaurant = {
		"id": str(node.id),
		"lat": str(node.lat),
		"lon": str(node.lon),
	}

	all_restaurants.append(this_restaurant)

	print("%s: (%s, %s)" % (str(node.id), str(node.lat), str(node.lon)))

f = open("restaurants.json", "w")
f.write(json.dumps(all_restaurants))
f.close()

print("Written " + str(len(all_restaurants)) + " restaurants")
