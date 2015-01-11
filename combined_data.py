import logging

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

def merge_candidates(candidate_map, constituency_name, aname, adata, bname, bdata):
	# two datasets have different constituency names
	# so put them through the mapper
	adata = normalise_names(candidate_map, aname, dict((constituency_name + ":" + c["name"], c) for c in adata))
	bdata = normalise_names(candidate_map, bname, dict((constituency_name + ":" + c["name"], c) for c in bdata))

	for name in set(adata.keys()) | set(bdata.keys()):
		yield name, adata.get(name, None), bdata.get(name, None)


