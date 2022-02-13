import googlemaps
import time
import json
import geopy
import sys
import config
import os

from geopy import distance
from pathlib import Path
from datetime import datetime


def queryPlaces(location):
	filename = "cache/places_" + str(round(location[0], 5)) + "_" + str(round(location[1],5))
	filename = filename.replace(".", "") + ".result"

	my_file = Path(filename)
	if my_file.is_file():
		print("\t\tCache HIT @ " + filename)
		with open(filename) as json_file:
			results = json.load(json_file)

	else:
		places = gmaps.places(radius=500, location=location, type="restaurant", query="McDonald's")
		results = places["results"]

		f = open(filename, "w")
		f.write(json.dumps(results))
		f.close()

	return results


gmaps = googlemaps.Client(
		key=config.GOOGLE_API_KEY,
		timeout=10,
		retry_timeout=10
	)

with open("restaurants.json") as json_file:
	restaurants = json.load(json_file)

with open("fast_chargers.json") as json_file:
	chargers = json.load(json_file)

try:
	os.mkdir("cache")
except FileExistsError:
	print("cache already exists")

restaurants_with_chargers = []

for charger in chargers:
	print("(%s, %s)" % (charger["lat"], charger["lon"]))
	charger_coords = (charger["lat"], charger["lon"])

	restaurant_found = False
	restaurant_distance = None
	this_restaurant = None

	for restaurant in restaurants:
		restaurant_coords = (restaurant["lat"], restaurant["lon"])

		distance = geopy.distance.distance(charger_coords, restaurant_coords).km

		if distance < 0.5:
			print("\tRestaurant found (in File)")
			restaurant_found = True
			restaurant_distance = distance	
			this_restaurant = {
				"id": restaurant["id"],
				"lat": restaurant["lat"],
				"lon": restaurant["lon"],
				"source": "osm",
			}
			break

	if not restaurant_found:
		print("\tGoogling for restaurant:")

		try:	
			results = queryPlaces(charger_coords)		
		except googlemaps.exceptions.Timeout:
			continue

		for place in results:
			lat = place["geometry"]["location"]["lat"]
			lon = place["geometry"]["location"]["lng"]
			name = place["name"]
			id = place["place_id"]

			print("\t\t(%s, %s)" % (lat, lon))
	
			restaurant_coords = (lat, lon)
	
			distance = geopy.distance.distance(charger_coords, restaurant_coords).km

			if distance < 0.5:
				print("\tRestaurant found (via API)")
				restaurant_found = True
				restaurant_distance = distance
				this_restaurant = {
					"id": id,
					"lat": lat,
					"lon": lon,
					"name": name,
					"source": "gmaps",
				}		
				break
	

	if restaurant_found:
		charger["distance"] = restaurant_distance
		charger["restaurant"] = this_restaurant
		restaurants_with_chargers.append(charger)

	print("")

f = open("restaurants_with_chargers.json", "w")
f.write(json.dumps(restaurants_with_chargers))
f.close()

print(str(len(restaurants_with_chargers)) + " chargers written")
