import urllib
import json
import logging
import re

def fetch_eu_region(mapit_area_id, context):
	req = urllib.urlopen("http://mapit.mysociety.org/area/%d/%s?type=EUR" % (mapit_area_id, context,))
	page = req.read()
	return json.loads(page)

def eu_region_from_url(mapit_area_url):
	logging.debug("eu_region_from_url(%r)", mapit_area_url)
	mapit_area_id = int(re.search(r"^http://mapit.mysociety.org/area/(\d+)$", mapit_area_url).group(1))
	covered_regions_dict = fetch_eu_region(mapit_area_id, "covered")
	if len(covered_regions_dict) == 0:
		logging.info("Using intersects for eu_region_from_url(%r)", mapit_area_url)
		covered_regions_dict = fetch_eu_region(mapit_area_id, "intersects")
	if len(covered_regions_dict) == 1:
		data, = covered_regions_dict.values()
		return data["name"]
	else:
		logging.error("eu_region_from_url(%r) -> %r", mapit_area_url, covered_regions_dict)
		return "unknown"

