#!/usr/bin/env python3

import webbrowser
import sys
import requests
import json
import urllib.parse
import argparse

from config_parser import *
from convertbng.util import convert_bng

parser = argparse.ArgumentParser()
parser.add_argument('--postcode', '-p', help="postcode of the property", type= str)
parser.add_argument('--address', '-a', help="address of the property", type= str)
parser.add_argument('--points_of_interest', '-pi', help="points of interest config", type= str, default='points_of_interest_config.json')

print(parser.format_help())
args = parser.parse_args()
print(args)

if (args.postcode == None and args.address == None):
	print('Should specify postcode or address!')
	exit(0)


app_config = read_config('app_config.json')
google_maps_key = app_config["google_maps_key"]


def get_distance_matrix_response(origin, destinations, mode):
	url_dest = '|'.join(destinations)

	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode={}&units=metric&key={}".format(origin, url_dest, mode, google_maps_key)

	#print('Generated url: {}'.format(url))

	response = requests.request("GET", url, headers={}, data={})
	#print(response.text)
	return json.loads(response.text)


def print_distance_result(distances_parsed_response, idx, destination_name, mode):
	duration = distances_parsed_response["rows"][0]["elements"][idx]["duration"]["text"]
	destination_address = distances_parsed_response["destination_addresses"][idx]
	print('{} time to {} ({}): {}'.format(mode, destination_name, destination_address, duration))


lat = None
lng = None

def get_postcode_by_address(address):
	if (address == None):
		print('Can not get postcode by empty address!')
		exit(0)

	geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address, google_maps_key)
	geocode_response = requests.request("GET", geocode_url, headers={}, data={})
	parsed_geocode_response = json.loads(geocode_response.text)
	#print(geocode_response.text)

	global lat
	lat = parsed_geocode_response["results"][0]["geometry"]["location"]["lat"]
	global lng
	lng = parsed_geocode_response["results"][0]["geometry"]["location"]["lng"]

	postcode_url = "https://api.postcodes.io/postcodes?lon={}&lat={}".format(lng, lat)
	postcode_response = requests.request("GET", postcode_url, headers={}, data={})
	parsed_postcode_response = json.loads(postcode_response.text)

	postcode = parsed_postcode_response["result"][0]["postcode"]
	
	return postcode.replace(' ', '')


# Parse address and postcode
property_address = urllib.parse.quote(args.address) if args.address != None else None
property_postcode = args.postcode if args.postcode != None else get_postcode_by_address(property_address)


# Open sites with information
print('Open crystalroof for {}'.format(property_postcode))
crystalroof = 'https://crystalroof.co.uk/report/postcode/{}/overview'.format(property_postcode)
webbrowser.open(crystalroof, new=1)

if (property_address != None):
	print('Open google maps for {}'.format(property_address))
	google_maps = 'https://www.google.co.uk/maps/place/{}'.format(property_address)
	webbrowser.open(google_maps)

print('Property lat is {}, lng is {}'.format(lat, lng))
if (lat != None and lng != None):
	print('Open locrating')
	locrating = 'https://www.locrating.com/school_catchment_areas.aspx?lat={}&lng={}'.format(lat, lng)
	webbrowser.open(locrating, new=0)

	bng = convert_bng(lng, lat)
	easting = bng[0][0]
	northing = bng[1][0]

	print('Open flood risk maps for easting {} and northing {}'.format(easting, northing))

	surface_water_flood_risk = 'https://check-long-term-flood-risk.service.gov.uk/map?easting={}&northing={}&map=SurfaceWater'.format(easting, northing)
	webbrowser.open(surface_water_flood_risk, new=0)

	river_flood_risk = 'https://check-long-term-flood-risk.service.gov.uk/map?easting={}&northing={}&map=RiversOrSea'.format(easting, northing)
	webbrowser.open(river_flood_risk, new=0)
	


# Read points of interest config
points_of_interest_config = read_config(args.points_of_interest)
points_of_interest = points_of_interest_config["points_of_interest"]

# Calculate points of interest destinations
destinations = []
for point_of_interest in points_of_interest:
	destinations.append(point_of_interest["post_code"].replace(' ', ''))


distances_parsed_response = get_distance_matrix_response(property_address, destinations, 'walking')
origin_address = distances_parsed_response["origin_addresses"]

print('Property address: {}'.format(origin_address))

idx = 0
for point_of_interest in points_of_interest:
	print_distance_result(distances_parsed_response, idx, point_of_interest["name"], "Walking")
	idx += 1

