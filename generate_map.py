import overpy
import http.client
import json
import sys
from pykml.factory import KML_ElementMaker as KML
from lxml import etree

with open("restaurants_with_chargers.json") as json_file:
        chargers = json.load(json_file)

kml_folder = KML.Folder()

for charger in chargers:
	if charger["status"] != "Operational" and charger["status"] != "Unknown":
		continue

	description = ""
	if charger["power"] != None:
		description += "Power: " + str(charger["power"]) + " kW\n"
	
	if charger["operator"] != None:
		description += "Operator: " + charger["operator"] + "\n"
	
	if charger["usage"] != None:
		description += "Usage: " + charger["usage"] + "\n"
			
	if charger["status"] != None:
		description += "Status: " + charger["status"] + "\n"

	icon = None

	if charger["power"] >= 150:
		icon = "#150kwplus"
	elif charger["power"] >= 100:
		icon = "#100kw_plus"
	else:
		icon = "#50kwplus"

	charger = KML.Placemark(
		KML.name(charger["name"] + " (" + str(round(charger["distance"] * 1000, 0)) + " m)"),
		KML.description(description),
		KML.styleUrl(icon),
		KML.Point(
			KML.coordinates("%s,%s" % (str(charger["lon"]), str(charger["lat"])))
		)
	)

	kml_folder.append(charger)

kml = KML.kml(
	KML.Document(
		KML.name("Schnellader mit McDonalds in der Nähe"),
		KML.description("Basiert auf Daten von Openstreetmap.org, openchargemap.org sowie maps.google.com. Alle Daten ohne Gewähr!\n\nIm Titel steht jeweils die Entfernung in Metern von McDonald's"),
		KML.Style(
			KML.IconStyle(
				KML.color("ff3644db"),
				KML.scale(1),
				KML.Icon(
					KML.href("https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png")
				),
				KML.hotSpot(
					x="32",
					xunits="pixels",
					y="64",
					yunits="insetPixels"
				),
			),	
			id="50kwplus",
		),
		KML.Style(
			KML.IconStyle(
				KML.color("ff00b4f4"),
				KML.scale(1),
				KML.Icon(
					KML.href("https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png")
				),
				KML.hotSpot(
					x="32",
					xunits="pixels",
					y="64",
					yunits="insetPixels"
				),
			),	
			id="100kw_plus",
		),
		KML.Style(
			KML.IconStyle(
				KML.color("ff579d00"),
				KML.scale(1),
				KML.Icon(
					KML.href("https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png")
				),
				KML.hotSpot(
					x="32",
					xunits="pixels",
					y="64",
					yunits="insetPixels"
				),
			),	
			id="150kwplus",
		),
		kml_folder
	)
)

et = etree.ElementTree(kml)
et.write("chargers.kml", pretty_print=True)
