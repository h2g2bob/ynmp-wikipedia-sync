import json
import logging
from mapping import MappingDatabase

def normalise_names(constituency_map, source, data):
	return {
		constituency_map.lookup_or_add(source, name) : candidates
		for (name, candidates)
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

def compare_candidates(adata, bdata):
	logging.debug("%r vs %r", adata, bdata)
	# TODO

if __name__=='__main__':
	logging.root.setLevel(logging.DEBUG)

	with open("candidates_from_wikipedia.json", "r") as f:
		wikipedia = json.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)
	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)

	for constituency_name, wp_candidates, ynmp_candidates in merge_constituencies(constituency_map, "wikipedia", wikipedia, "ynmp", ynmp):
		logging.debug("compare %r", constituency_name)
		compare_candidates(wp_candidates, ynmp_candidates)

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)

