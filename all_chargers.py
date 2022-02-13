import http.client
import json
import sys
import config

def getMaxPowerPerChargepoint(chargepoint):
	max_power = None

	for connection in chargepoint["Connections"]:
		if connection["PowerKW"] == None:
			continue

		power = int(connection["PowerKW"])

		if max_power == None or power > max_power:
			max_power = power
	
	return max_power

def getMaxPower(chargepoints):
	max_power = None

	for chargepoint in chargepoints:
		power = getMaxPowerPerChargepoint(chargepoint)

		if power == None:
			continue

		if max_power == None or power > max_power:
			max_power = power
	
	return max_power


def hasConnection(chargepoint, text):
	for connection in chargepoint["Connections"]:
		if connection["ConnectionType"]["Title"] == text:
			return True
	
	return False


def getChargepointsByLocation(lat, lon):
	conn = http.client.HTTPSConnection("api.openchargemap.io")

	headers = { 'Content-Type': "application/json" }
	
	url = "/v3/poi?connectiontypeid=33&latitude=%s&output=json&countrycode=DE&maxresults=10000&longitude=%s&distance=800&distanceunit=km&key=%s" % (str(lat), str(lon), config.OCM_API_KEY)

	conn.request("GET", url, headers=headers)

	res = conn.getresponse()
	data = res.read()

	data = json.loads(data.decode("utf-8"))
	
	return data


# Get all chargers around (roughly) the center of Germany
stations = getChargepointsByLocation(50.5139474422301, 10.010603824637528)

print("Received " + str(len(stations)) + " stations")
all_stations = []

for station in stations:
	id = station["ID"]
	name = station["AddressInfo"]["Title"]
	lat = station["AddressInfo"]["Latitude"]
	lon = station["AddressInfo"]["Longitude"]
	power = getMaxPowerPerChargepoint(station)

	try:
		operator = station["OperatorInfo"]["Title"]
	except TypeError:
		operator = None
	try:
		usage = station["UsageType"]["Title"]
	except TypeError:
		usage = None
	
	try:
		status = station["StatusType"]["Title"]
	except TypeError:
		status = None

	if power == None or power < 50:
		continue

	if not hasConnection(station, "CCS (Type 2)"):
		continue

	this_station = {
		"id": id,
		"name": name,
		"lat": lat,
		"lon": lon,
		"power": power,
		"operator": operator,
		"usage": usage,
		"status": status,
	}

	all_stations.append(this_station)

	print("%s: %s @ %s, %s (%s kW)" % (id, name, lat, lon, power))

f = open("fast_chargers.json", "w")
f.write(json.dumps(all_stations))
f.close()

print("Wrote " + str(len(all_stations)) + " stations")
