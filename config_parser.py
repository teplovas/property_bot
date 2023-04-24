#!/usr/bin/env python3

import json


def read_config(file_name):
	f = open(file_name)
	data = json.load(f)

	f.close()
	return data
