import wikipedia
import ynmp
import re
import logging
import party_names

def wiki_template_for_ynmp_person(ynmp_data, ynmp_constituency_id):
	name = ynmp_data["person_id"]["name"]

	possibe_references = [
		link["url"]
		for link in ynmp_data["person_id"]["links"]
		if link["note"] == "party PPC page" ]
	if len(possibe_references) == 1:
		reference = "[%s Party PPC page]" % (possibe_references[0],)
	elif len(possibe_references) == 0:
		reference = "[https://yournextmp.com/constituency/%d/ YourNextMP]" % (ynmp_constituency_id,)
	else:
		raise ValueError(possibe_references)

	ynmp_party = ynmp_data["person_id"]["party_memberships"]["2015"]["name"]
	wikipedia_party_name = party_names.to_wikipedia_name(ynmp_party)
	logging.debug("to_wikipedia_name(%r) = %r", ynmp_party, wikipedia_party_name)
	if wikipedia_party_name is not None:
		party = wikipedia_party_name
		templatename = "Election box candidate with party link"
	else:
		party = ynmp_party
		templatename = "Election box candidate"

	return """{{%s
 |party = %s
 |candidate = %s<ref>%s</ref>
 |votes = 
 |percentage = 
 |change = 
}}
""" % (templatename, party, name, reference,)

def fetch_ynmp_candidate_data(constituency_id, candidate_name):
	ynmp_data = ynmp.fetch_candidates_in_constituency(constituency_id)
	candidate_data_list = {
		person["person_id"]["id"] : person # de-duplicates repetition of the same person
		for person in ynmp_data["result"]["memberships"]
		if person["person_id"]["name"] == candidate_name }
	if len(candidate_data_list) == 1:
		return candidate_data_list.values()[0]
	else:
		raise ValueError(candidate_data_list)

def insert_candidate_in_election_box(wikipage, extratext):
	# Inserts to the end of the box, but should really be alphabetized

	section = wikipedia.section_for_2015(wikipage)
	if section is None:
		raise Exception("No 2015 section on the page")
	head, tail = wikipage.split(section, 1)

	m = re.search(r"(\{\{Election box end.*)$", section, flags=re.I | re.DOTALL)
	if m is None:
		raise Exception("Could not find end tag on wikipage")
	section = section.replace(m.group(1), extratext + m.group(1))

	return head + section + tail

def generate_updated_wikitext(wikipedia_pagename, ynmp_constituency_id, ynmp_candidate_name):
	wikipage = wikipedia.latest_revision(wikipedia_pagename)
	candidate_data = fetch_ynmp_candidate_data(ynmp_constituency_id, ynmp_candidate_name)
	candidate_template = wiki_template_for_ynmp_person(candidate_data, ynmp_constituency_id)
	return insert_candidate_in_election_box(wikipage, candidate_template)

if __name__=='__main__':
	logging.root.setLevel(logging.DEBUG)
	print generate_updated_wikitext(u"Aberavon (UK Parliament constituency)", int(u"66101"), u"Captain Beany").encode("utf8")

	
