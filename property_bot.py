#!/usr/bin/env python3

import webbrowser
import sys
import requests
import json
import urllib.parse
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--postcode', '-p', help="postcode of the property", type= str)
parser.add_argument('--address', '-a', help="address of the property", type= str)

print(parser.format_help())
args = parser.parse_args()
print(args)
print(args.postcode)
print(args.address)

if (args.postcode == None and args.address == None):
	print('Should specify at postcode or address!')
	exit(0)

google_maps_key = ''


def get_distance_matrix_response(origin, destinations, mode):
	url_dest = '|'.join(destinations)

	url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&mode={}&units=metric&departure_time=1682323255&key={}".format(origin, url_dest, mode, google_maps_key)

	print('Generated url: {}'.format(url))

	payload={}
	headers = {}

	response = requests.request("GET", url, headers=headers, data=payload)
	print(response.text)
	return json.loads(response.text)


def print_distance_result(distances_parsed_response, idx, destination_name):
	duration = distances_parsed_response["rows"][0]["elements"][idx]["duration"]["text"]
	destination_address = distances_parsed_response["destination_addresses"][idx]
	print('Time to {} ({}): {}'.format(destination_name, destination_address, duration))


def get_postcode_by_address(address):
	if (address == None):
		print('Can not get postcode by empty address!')
		exit(0)

	geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(address, google_maps_key)
	geocode_response = requests.request("GET", geocode_url, headers={}, data={})
	parsed_geocode_response = json.loads(geocode_response.text)

	lat = parsed_geocode_response["results"][0]["geometry"]["location"]["lat"]
	lng = parsed_geocode_response["results"][0]["geometry"]["location"]["lng"]

	postcode_url = "https://api.postcodes.io/postcodes?lon={}&lat={}".format(lng, lat)
	postcode_response = requests.request("GET", postcode_url, headers={}, data={})
	parsed_postcode_response = json.loads(postcode_response.text)

	postcode = parsed_postcode_response["result"][0]["postcode"]
	
	return postcode.replace(' ', '')


property_address = urllib.parse.quote(args.address) if args.address != None else None
print('prop address: {}'.format(property_address))
property_postcode = args.postcode if args.postcode != None else get_postcode_by_address(property_address)
print('prop postcode: {}'.format(property_postcode))


swimming_pool_post_code = 'HA48DZ'
ruislip_post_code = 'HA48LD'
ruislip_manor_post_code = 'HA49AA'
eastcote_post_code = 'HA51QZ'


print('Open info for {}'.format(property_address))

crystalroof = 'https://crystalroof.co.uk/report/postcode/{}/overview'.format(property_postcode)

webbrowser.open(crystalroof)


distances_parsed_response = get_distance_matrix_response(property_address, [swimming_pool_post_code, ruislip_post_code, ruislip_manor_post_code, eastcote_post_code], 'walking')
origin_address = distances_parsed_response["origin_addresses"]

print('Property address: {}'.format(origin_address))
print_distance_result(distances_parsed_response, 0, "swimming pool")
print_distance_result(distances_parsed_response, 1, "Ruislip station")
print_distance_result(distances_parsed_response, 2, "Ruislip Manor station")
print_distance_result(distances_parsed_response, 3, "Eastcote station")

