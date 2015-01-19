import urllib
import lxml.etree as etree
import re
import logging
import json
import sys
import time
from combined_data import normalise_names
from mapping import MappingDatabase
from party_names import lookup_long_name as party_name_lookup
from shared import escape_html as escape

def getpage(url):
	req = urllib.urlopen(url)
	return req.read()

def rss_links():
	page = getpage("http://www.electionleaflets.org/feeds/latest/")
	doc = etree.XML(page)
	return tuple(str(x) for x in doc.xpath("channel/item/link/text()"))

def most_recent_id():
	link = tuple(rss_links())[0]
	id = int(re.search(r"/leaflets/(\d+)/", link).group(1))
	return id

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
	if el_party == "Other":
		# we can't make any assumptions about it
		logging.info("Leaflet for Other %r", el_url)
		return None
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

	leaflets_to_fetch = 50

	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)
	ynmp = normalise_names(constituency_map, "ynmp", ynmp)

	print "<h1>Unknown candidates from last %d election leaflets</h1>" % (leaflets_to_fetch,)

	new_last_fetched_id = most_recent_id()
	for id in xrange(new_last_fetched_id - leaflets_to_fetch, new_last_fetched_id+1):
		url = "http://www.electionleaflets.org/leaflets/%d/" % (id,)
		try:
			el_data = fetch_leaflet(url)
			new_candidate = match_el_ynmp(constituency_map, el_data, ynmp)
			if new_candidate is not None:
				el_constituency_name, _, el_party = new_candidate
				print "<a href=\"%s\">%s %s</a><br/>" % (url, escape(el_constituency_name), escape(el_party),)
		except Exception:
			logging.info("Cannot parse leaflet page %r", url, exc_info=sys.exc_info())
	print "(generated %r)" % (time.ctime(),)

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)

