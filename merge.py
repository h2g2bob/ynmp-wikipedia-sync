from mapping import MappingDatabase
import re

def cleanup_canonical_names(constituency_map):
	for ((source, alias), canonical) in constituency_map.entries.items():
		constituency_map.entries[source, alias] = canonical.split(":",1)[-1].lower().replace("(uk parliament constituency)", "").strip()

def words(canonical):
	return tuple(sorted(re.findall("[a-z]+", canonical)))

def build_word_lookup(constituency_map, exclude_source):
	word_lookup = {}
	for ((source, alias), canonical) in constituency_map.entries.items():
		if source != exclude_source:
			word_lookup[words(canonical)] = canonical
	return word_lookup

def map_same_words(constituency_map, source):
	# things we can map to:
	word_lookup = build_word_lookup(constituency_map, source)
	# things we're mapping from:
	for (alias, canonical) in constituency_map.mappings_for_source(source):
		try:
			merge_to_canonical = word_lookup[words(canonical)]
		except KeyError:
			pass
		else:
			constituency_map.merge(source, alias, merge_to_canonical)

if __name__=='__main__':
	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)

	cleanup_canonical_names(constituency_map)
	map_same_words(constituency_map, "wikipedia")
	map_same_words(constituency_map, "ynmp")

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)
