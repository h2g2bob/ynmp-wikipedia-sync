import logging
import json
import urllib
import json
import re
from shared import Candidate

def latest_revision(pagename):
	logging.debug("latest_revision(%r)", pagename)
	assert isinstance(pagename, unicode)
	req = urllib.urlopen("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&format=json" % (urllib.quote(pagename.encode("utf8")),))
	page = req.read()
	try:
		data = json.loads(page)
		page_data, = data["query"]["pages"].values()
		revision, = page_data["revisions"]
		return revision["*"]
	except Exception:
		logging.exception("Invalid response for %r", page)
		raise

def parliament_constituencies():
	page = latest_revision(u"List of United Kingdom Parliament constituencies")
	table = re.search(r'class="wikitable sortable"(.*?)\|}\s*==', page, re.DOTALL).group(1)
	after_tr = True
	for line in table.split("\n")[1:]:
		if line.startswith("!"):
			continue
		if line.startswith("|-"):
			after_tr = True
			continue
		if after_tr:
			after_tr = False
			m = re.search(r"^\s*\|\s*\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]", line)
			if m is None:
				raise ValueError(line)
			yield m.group(1).strip()

def section_for_2015(page):
	for section in re.findall(r"\{\{Election box begin.*?\{\{Election box end\}\}", page, re.DOTALL | re.I):
		if "United Kingdom general election, 2015" in section or "Next United Kingdom general election" in section or "|General Election 2015]]" in section:
			assert section.lower().count("election box begin") == 1
			return section
	# does not have any 2015 section
	return None

def candidates_from_section(section):
	# Handles:
	#    {{EBC
	#    | candidate = 
	#    | votes =  }}
	# And:
	#    {{EBC
	#    | votes =
	#    }}{{EBC
	#    | votes =
	#    }}
	candidates = re.findall(r"\{\{Election box candidate.*?(?:\n\s*\}\}|\}\}\s*\n)", section, re.DOTALL | re.I)
	candidates_check = re.findall(r"candidate\s*=", section, re.DOTALL | re.I)
	if len(candidates_check) != len(candidates):
		raise ValueError((candidates, candidates_check))
	return [parse_candidate_wikitext(c) for c in candidates]

def remove_wikilink(name):
	m = re.search("^\[\[(.*)\]\]$", name.strip())
	if m is not None:
		return m.group(1).split("|", 1)[-1]
	return name

def remove_references(name):
	name = re.sub(r"<ref.*?</ref>", "", name)
	name = re.sub(r"<ref.*?/>", "", name)
	name = name.strip()
	if name.startswith("[http"):
		name = name.split(" ",1)[-1].replace("]", "", 1)
	name = re.sub(r"\{\{citation needed.*?\}\}", "", name, flags=re.I)
	return name

def parse_candidate_wikitext(wikitext):
	try:
		name = re.search(r"^[\s\|]*candidate\s*=(.*)$", wikitext, re.M).group(1).strip()
	except Exception:
		raise ValueError(wikitext) # name
	name = remove_wikilink(remove_references(name))
	name = name.strip()
	try:
		party = re.search(r"^[\s\|]*party\s*=(.*)$", wikitext, re.M).group(1).strip()
	except Exception:
		raise ValueError(wikitext) # party
	party = remove_wikilink(party)
	party = party.strip()
	references = list(re.findall(r"\b(https?://[^\"'\s<>\[\]]+)[\"'\s<>\[\]]", wikitext))
	return Candidate(name, party, person_id=name, party_id=party, references=references)

def fetch_and_parse_candidates(constituency_name):
	try:
		page = latest_revision(constituency_name).encode("utf8")
		section = section_for_2015(page)
		if section is None:
			if "2015" not in page:
				logging.info("No section for 2015 in %r", constituency_name)
				return []
			raise Exception("No section on page")
		return list(candidates_from_section(section))
	except Exception:
		logging.exception("Unable to parse %r", constituency_name)
		return []

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	data = {}
	for constituency_name in parliament_constituencies():
		candidates = fetch_and_parse_candidates(constituency_name)
		logging.debug("Found %d candidates for %r", len(candidates), constituency_name)
		data[constituency_name] = candidates

	with open("candidates_from_wikipedia.json", "w") as f:
		json.dump({
			constituency_name : [c.to_dict() for c in candidates]
			for (constituency_name, candidates)
			in data.items() }, f)

