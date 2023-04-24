#!/usr/bin/env python3

import pickle
from collections import defaultdict

class Cache:
	CACHE_DATA_FILE = 'cache_data.txt'

	def __init__(self):
		try:
			self.cache_data = pickle.load(open(self.CACHE_DATA_FILE, 'rb'))
		except Exception as e:
			self.cache_data = {}
	    

	def get(self, key):
		return self.cache_data.get(key)


	def put(self, key, value):
		self.cache_data[key] = value


	def finalize(self):
		pickle.dump(self.cache_data, open(self.CACHE_DATA_FILE, 'wb'))

