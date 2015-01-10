import re
from shared import Candidate
import logging

def section_for_2015(page):
	for section in re.findall(r"\{\{Election box begin.*?\{\{Election box end\}\}", page, re.DOTALL | re.I):
		if "United Kingdom general election, 2015" in section:
			assert section.lower().count("election box begin") == 1
			return section
	# does not have any 2015 section
	return None

def candidates_from_section(section):
	candidates = re.findall(r"\{\{Election box candidate.*?\n\}\}", section, re.DOTALL | re.I)
	candidates_check = re.findall(r"candidate\s*=", section, re.DOTALL | re.I)
	assert len(candidates_check) == len(candidates)
	return [parse_candidate_wikitext(c) for c in candidates]

def remove_wikilink(name):
	m = re.search("^\[\[(.*)\]\]$", name.strip())
	if m is not None:
		return m.group(1).split("|", 1)[-1]
	return name

def remove_references(name):
	return re.sub(r"<ref.*?</ref>", "", name)

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
	return Candidate(name, party)

