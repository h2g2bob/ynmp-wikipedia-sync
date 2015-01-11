import json
import logging
from mapping import MappingDatabase

def normalise_names(constituency_map, source, data):
	return {
		constituency_map.lookup_or_add(source, name) : candidates
		for (name, candidates)
		in data.items() }

def merge_constituencies(constituency_map, aname, adata, bname, bdata):
	adata = normalise_names(constituency_map, aname, adata)
	bdata = normalise_names(constituency_map, bname, bdata)

	adata_only = set(adata.keys()) - set(bdata.keys())
	if adata_only:
		logging.warn("Unmapped: in %s only: %r", aname, adata_only)
	bdata_only = set(bdata.keys()) - set(adata.keys())
	if bdata_only:
		logging.warn("Unmapped: in %s only: %r", bname, bdata_only)

	for name in set(adata.keys()) | set(bdata.keys()):
		# print name, adata.get(name, None), bdata.get(name, None)
		print repr(name)

if __name__=='__main__':
	with open("candidates_from_wikipedia.json", "r") as f:
		wikipedia = json.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)
	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)

	merge_constituencies(constituency_map, "wikipedia", wikipedia, "ynmp", ynmp)

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)

