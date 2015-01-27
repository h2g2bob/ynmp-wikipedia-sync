import urllib
import json
import logging
import re

def eu_region_from_url(mapit_area_url):
	logging.debug("eu_region_from_url(%r)", mapit_area_url)
	mapit_area_id = int(re.search(r"^http://mapit.mysociety.org/area/(\d+)$", mapit_area_url).group(1))
	req = urllib.urlopen("http://mapit.mysociety.org/area/%d/covered?type=EUR" % (mapit_area_id,))
	page = req.read()
	covered_regions_dict = json.loads(page)
	data, = covered_regions_dict.values()
	return data["name"]

