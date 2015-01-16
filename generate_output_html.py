import combined_data
import logging
import json
from mapping import MappingDatabase
import party_names
import re
import time
import urllib

def escape(text):
	return "".join(
		c if c.isalnum() or c.isspace() else "&#x%04x;" % (ord(c),)
		for c in text
		).encode("utf8")

def ynmp_url(data, canonical_name, constituency_map):
	yid = ynmp_id(data, canonical_name, constituency_map)
	if yid is not None:
		return "https://yournextmp.com/constituency/%d" % (yid,)
	logging.error("ynmp_url(%r) did not find any matching entries in the map", canonical_name)
	return "#"

def ynmp_id(data, canonical_name, constituency_map):
	source_constituency_names = data.keys()
	for source_name in source_constituency_names:
		if canonical_name == constituency_map.lookup_or_add("ynmp", source_name, source_name):
			return int(source_name.split(":")[0])
	return None

def format_party(party):
	short = party_names.to_short_name(party)
	if short is None:
		return ""
	else:
		return "<span class=\"party\">%s</span>" % (short,)

def wikipedia_url(data, canonical_name, constituency_map):
	source_name = wikipedia_name(data, canonical_name, constituency_map)
	if source_name is not None:
		return "https://en.wikipedia.org/wiki/%s" % (source_name,)
	logging.error("wikipedia_url(%r) did not find any matching entries in the map", canonical_name)
	return "#"

def wikipedia_name(data, canonical_name, constituency_map):
	source_constituency_names = data.keys()
	for source_name in source_constituency_names:
		if canonical_name == constituency_map.lookup_or_add("wikipedia", source_name, source_name):
			return source_name
	return None

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	with open("candidates_from_wikipedia.json", "r") as f:
		wikipedia = json.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)
	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)
	with open("mappings_candidate.csv", "r") as f:
		candidate_map = MappingDatabase.load(f)

	with open("output.html", "w") as outfile:
		both=0
		wponly=0
		ynmponly=0
		outfile.write("<style> th, td { text-align: left; width: 20em; } td.links { width: 8em; } td.links a {color : #99ccff; } .missing { font-weight: bold; background: #cc7777; color: #000000; } .missing > a { color: #000000; } .constituency { background: #777777; color: #ffffff; } span.party { font-size: 70%; color: #cccccc; } </style>")
		outfile.write("<table>")
		for constituency_name, wp_candidates, ynmp_candidates in sorted(combined_data.merge_constituencies(constituency_map, "wikipedia", wikipedia, "ynmp", ynmp)):
			logging.debug("compare %r", constituency_name)
			outfile.write("<tr><th class=\"constituency\" colspan=\"2\">%s</th><th>&nbsp;</th></tr>" % (escape(constituency_name),))
			outfile.write("<tr>")
			outfile.write("<th><a href=\"%s\">YNMP</a></th>" % (escape(ynmp_url(ynmp, constituency_name, constituency_map)),))
			outfile.write("<th><a href=\"%s\">Wikipedia</a></th>" % (escape(wikipedia_url(wikipedia, constituency_name, constituency_map)),))
			outfile.write("</tr>")
			for candidate_name, wp_candidate, ynmp_candidate in sorted(combined_data.merge_candidates(candidate_map, constituency_name, "wikipedia", wp_candidates, "ynmp", ynmp_candidates)):
				# logging.debug("%r %r: %r -- %r", constituency_name, candidate_name, wp_candidate, ynmp_candidate)
				outfile.write("<tr>")
				if wp_candidate is None:
					ynmponly += 1
				elif ynmp_candidate is None:
					wponly += 1
				else:
					both += 1

				if ynmp_candidate is None:
					outfile.write("<td class=\"missing\">missing</td>")
				else:
					outfile.write("<td>%s %s</td>" % (escape(ynmp_candidate["name"]), format_party(ynmp_candidate["party"]),))

				if wp_candidate is None:
					fix_url = "run/edit_wp?wppage=%s&ynmpid=%d&ynmpname=%s" % (
						urllib.quote(wikipedia_name(wikipedia, constituency_name, constituency_map).encode("utf8")),
						ynmp_id(ynmp, constituency_name, constituency_map),
						urllib.quote(ynmp_candidate.get("name", "no_candidate").encode("utf8")))
					outfile.write("<td class=\"missing\">missing (<a href=\"%s\">fix</a>)</td>" % (fix_url,))
				else:
					outfile.write("<td>%s %s</td>" % (escape(wp_candidate["name"]), format_party(wp_candidate["party"]),))


				references = (ynmp_candidate["references"] if ynmp_candidate is not None else []) + (wp_candidate["references"] if wp_candidate is not None else [])
				outfile.write("<td class=\"links\">%s</td>" % (",".join(
					"<a href=\"%s\">link</a>" % (escape(x),)
					for x in references,)))

				outfile.write("</tr>\n")
		outfile.write("</table>")
		outfile.write("both=%d +ynmp=%d +wp=%d" % (both, ynmponly, wponly))
		outfile.write("<br/>Generated %s" % (time.ctime(),))
			

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)
	with open("mappings_candidate.csv", "w") as f:
		candidate_map.save(f)

