import logging
import re
import wikipedia
import json
from mapping import MappingDatabase

UNKNOWN="unknown"

def ynmp_spelling(constituency_map, wp_constituency_name):
	canonical_name = constituency_map.lookup_or_add("wikipedia", wp_constituency_name, wp_constituency_name)
	ynmp_spellings = [alias
		for (alias, canonical) in constituency_map.mappings_for_source("ynmp")
		if canonical == canonical_name]
	if len(ynmp_spellings) == 1:
		return ynmp_spellings[0]
	else:
		raise ValueError("ynmp_spelling(%s) -> %r", wp_constituency_name, ynmp_spellings)

def eu_name_from_page(page):
	m = re.search(r"\|\s*(?:EP|european)\s*=([^<>\{\}\|]+)", page, flags=re.DOTALL|re.I)
	if m is None:
		logging.info("eu_name_from_page failed regexp for %r", page)
		return UNKNOWN
	eu_name = m.group(1).strip()
	if not eu_name:
		logging.info("eu_name_from_page empty string for %r", page)
		return UNKNOWN
	logging.debug("found eu_name_from_page %r", eu_name)
	return eu_name

def county_from_page(page):
	m = re.search(r"\|\s*(?:Division|county)\s*=([^<>\{\}\|]+)", page, flags=re.DOTALL|re.I)
	if m is None:
		logging.info("county_from_page failed regexp for %r", page)
		return UNKNOWN
	county = m.group(1).strip()
	if county.startswith("[["):
		county = county.split("|")[-1].rstrip("]")
	if not county:
		logging.info("county_from_page empty string for %r", page)
		return UNKNOWN
	logging.debug("found county_from_page %r", county)
	return county

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)

	constituency_name_to_eu_name = {}
	for constituency_name in tuple(wikipedia.parliament_constituencies()):
		page = wikipedia.latest_revision(constituency_name)
		eu_name = eu_name_from_page(page)
		if eu_name == UNKNOWN:
			logging.warn("Did not get an eu name for %r", constituency_name)
		county = county_from_page(page)
		if county == UNKNOWN:
			logging.warn("Did not get a county for %r", constituency_name)
		ynmp_constituency_name = ynmp_spelling(constituency_map, constituency_name)
		constituency_name_to_eu_name[ynmp_constituency_name] = [eu_name, county]

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)

	with open("constituency_name_to_region_name.json", "w") as f:
		json.dump(constituency_name_to_eu_name, f)

