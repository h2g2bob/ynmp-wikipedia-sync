import wikipedia_api
import wikitext_parser
import logging

def fetch_and_parse_candidates(constituency_name):
	try:
		page = wikipedia_api.latest_revision(constituency_name).encode("utf8")
		section = wikitext_parser.section_for_2015(page)
		if section is None:
			raise Exception("No section on page")
		return list(wikitext_parser.candidates_from_section(section))
	except Exception:
		logging.exception("Unable to parse %r" % (constituency_name,))
		return []

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	data = {}
	for constituency_name in wikipedia_api.parliament_constituencies():
		candidates = fetch_and_parse_candidates(constituency_name)
		logging.debug("Found %d candidates for %r", len(candidates), constituency_name)
		data[constituency_name] = candidates

	with open("candidates_from_wikipedia.json", "w") as f:
		json.dumps({
			constituency_name : [c.to_json() for c in candidates]
			for (constituency_name, candidates)
			in data.items() })

