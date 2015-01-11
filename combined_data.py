import json
import logging
from mapping import MappingDatabase

def normalise_names(map, source, data):
	return {
		map.lookup_or_add(source, name, name) : value
		for (name, value)
		in data.items() }

def merge_constituencies(constituency_map, aname, adata, bname, bdata):
	# two datasets have different constituency names
	# so put them through the mapper
	adata = normalise_names(constituency_map, aname, adata)
	bdata = normalise_names(constituency_map, bname, bdata)

	adata_only = set(adata.keys()) - set(bdata.keys())
	if adata_only:
		logging.warn("Unmapped: in %s only: %r", aname, adata_only)
	bdata_only = set(bdata.keys()) - set(adata.keys())
	if bdata_only:
		logging.warn("Unmapped: in %s only: %r", bname, bdata_only)

	for name in set(adata.keys()) & set(bdata.keys()):
		yield name, adata[name], bdata[name]

def merge_candidates(candidate_map, aname, adata, bname, bdata):
	# two datasets have different constituency names
	# so put them through the mapper
	adata = normalise_names(candidate_map, aname, dict((constituency_name + ":" + c["name"], c) for c in adata))
	bdata = normalise_names(candidate_map, bname, dict((constituency_name + ":" + c["name"], c) for c in bdata))

	for name in set(adata.keys()) | set(bdata.keys()):
		yield name, adata.get(name, None), bdata.get(name, None)


if __name__=='__main__':
	logging.root.setLevel(logging.DEBUG)

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
		outfile.write("<style> th, tr { text-align: left; width: 20em; } .missing { font-weight: bold; background: #cc7777; } .constituency { background: #777777; color: #ffffff; } </style>")
		outfile.write("<table>")
		outfile.write("<tr><th>YNMP</th><th>Wikipeia</th></tr>")
		for constituency_name, wp_candidates, ynmp_candidates in sorted(merge_constituencies(constituency_map, "wikipedia", wikipedia, "ynmp", ynmp)):
			logging.debug("compare %r", constituency_name)
			outfile.write("<tr><th class=\"constituency\" colspan=\"2\">%s</th></tr>" % (constituency_name.encode("utf8"),))
			for candidate_name, wp_candidate, ynmp_candidate in sorted(merge_candidates(candidate_map, "wikipedia", wp_candidates, "ynmp", ynmp_candidates)):
				# logging.debug("%r %r: %r -- %r", constituency_name, candidate_name, wp_candidate, ynmp_candidate)
				outfile.write("<tr>")
				if wp_candidate is None:
					ynmponly += 1
					outfile.write("<td>%s</td><td class=\"missing\">missing</td>" % (ynmp_candidate["name"].encode("utf8"),))
				elif ynmp_candidate is None:
					wponly += 1
					outfile.write("<td class=\"missing\">missing</td><td>%s</td>" % (wp_candidate["name"].encode("utf8"),))
				else:
					both += 1
					outfile.write("<td>%s</td><td>%s</td>" % (ynmp_candidate["name"].encode("utf8"), wp_candidate["name"].encode("utf8")))
				outfile.write("</tr>\n")
		outfile.write("</table>")
		outfile.write("both=%d +ynmp=%d +wp=%d" % (both, ynmponly, wponly))
			

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)
	with open("mappings_candidate.csv", "w") as f:
		candidate_map.save(f)

