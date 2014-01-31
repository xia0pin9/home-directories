#!/usr/bin/env python

import requests
import time

baseurl = 'http://localhost:9200/'

with open("indexes.txt") as f:
    for line in f:
	index = line.replace("\"", "").rstrip()
	r = requests.delete(baseurl + index)
	if r.status_code != 200:
	    print(r.text)
        else:
	    print index, "OK"
	time.sleep(10)
