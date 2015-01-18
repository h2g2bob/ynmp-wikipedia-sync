import urllib
import lxml.etree as etree
import re
import logging
import json
import sys
from combined_data import normalise_names
from mapping import MappingDatabase
from party_names import lookup_long_name as party_name_lookup

def getpage(url):
	req = urllib.urlopen(url)
	return req.read()

def rss_links():
	page = getpage("http://www.electionleaflets.org/feeds/latest/")
	doc = etree.XML(page)
	return tuple(str(x) for x in doc.xpath("channel/item/link/text()"))

def fetch_leaflet(url):
	page = getpage(url)
        party = re.search(r"<p>Published by <a href=\"[^\"]+?\">([^<>]+?)</a></p>", page).group(1)
	constituency = re.search(r"Delivered in <a href=\"[^\"]+?\">([^<>]+?)</a>", page).group(1)
	return (url, party, constituency,)

def match_el_ynmp(constituency_map, el_data, ynmp):
	el_url, el_party, el_name = el_data
	canonical_name = constituency_map.lookup_or_add("electionleaflets", el_name, el_name.lower())
	try:
		ynmp_constituency = ynmp[canonical_name]
	except KeyError:
		logging.debug("ynmp_constituency mapping missing: not mapped %r (from %r)", canonical_name, ynmp.keys())
		raise
	party = party_name_lookup[el_party] # can KeyError on no mapping
	ynmp_party_name = party.ynmp
	matching_candidates = [ can for can in ynmp_constituency if can["party"] == ynmp_party_name ]
	if len(matching_candidates) == 0:
		# new, interesting candidate
		return canonical_name, el_url, el_party
	elif len(matching_candidates) == 1:
		# already know about this candidate -- boring
		return None
	else:
		raise ValueError(matching_candidates)

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)

	ynmp = normalise_names(constituency_map, "ynmp", ynmp)
	for url in rss_links():
		try:
			el_data = fetch_leaflet(url)
			new_candidate = match_el_ynmp(constituency_map, el_data, ynmp)
			if new_candidate is not None:
				print new_candidate
		except Exception:
			logging.info("Cannot parse leaflet page %r", url, exc_info=sys.exc_info())

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)

