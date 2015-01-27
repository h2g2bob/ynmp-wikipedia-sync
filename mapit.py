import urllib
import json
import logging
import re
import ynmp

def fetch_eu_region_cache(mapit_area_id, context):
	fn = "./mapit-cache/mapit-cache-%d-%s" % (mapit_area_id, context,)
	try:
		with open(fn, "r") as f:
			return json.load(f)
	except Exception:
		logging.info("Not in cache %r %r" % (mapit_area_id, context,))
		data = fetch_eu_region(mapit_area_id, context)
		with open(fn, "w") as f:
			json.dump(data, f)
		return data

def fetch_eu_region(mapit_area_id, context):
	req = urllib.urlopen("http://mapit.mysociety.org/area/%d/%s?type=EUR" % (mapit_area_id, context,))
	page = req.read()
	return json.loads(page)

def eu_region_from_url(mapit_area_url):
	try:
		logging.debug("eu_region_from_url(%r)", mapit_area_url)
		mapit_area_id = int(re.search(r"^http://mapit.mysociety.org/area/(\d+)$", mapit_area_url).group(1))
		covered_regions_dict = fetch_eu_region_cache(mapit_area_id, "covered")
		if len(covered_regions_dict) == 0:
			logging.info("Using intersects for eu_region_from_url(%r)", mapit_area_url)
			covered_regions_dict = fetch_eu_region_cache(mapit_area_id, "intersects")
		if len(covered_regions_dict) == 1:
			data, = covered_regions_dict.values()
			return data["name"]
		else:
			raise ValueError(covered_regions_dict)
	except Exception:
		logging.exception("eu_region_from_url(%r)", mapit_area_url)
		return "unknown"


if __name__=='__main__':
	logging.root.setLevel(logging.INFO)

	constituency_id_to_eu_name = {}
	for constituency_id, constituency_name in tuple(ynmp.all_constituencies()):
		constituency_data = ynmp.fetch_candidates_in_constituency(constituency_id)
		eu_region_name = eu_region_from_url(constituency_data["result"]["area"]["identifier"])
		constituency_id_to_eu_name[constituency_id] = eu_region_name

	with open("constituency_id_to_eu_name.json", "w") as f:
		json.dump(constituency_id_to_eu_name, f)

