import wikipedia
import ynmp
import re
import logging
import party_names
import urllib
import datetime
from shared import escape_html as escape

def fmt_today():
	return fmt_date(datetime.date.today())

def fmt_date(date):
	# strftime %d pads day with a zero
	month_name = (None, "January", "February", "March", "April", "May", "June", "July", "August", "September", "November", "December",)
	return "%d %s %d" % (date.day, month_name[date.month], date.year,)


def get_reference(ynmp_data, candidate_name, party, ynmp_constituency_data):
	for link in ynmp_data["person_id"]["links"]:
		if link["note"] == "party PPC page":
			return "{{cite web |url=%s |title=%s PPC page |publisher=%s |accessdate=%s }}" % (link["url"],  candidate_name, party, fmt_today(),)

	for version in ynmp_data["person_id"]["versions"]:
		m = re.search(r'(https?://[^ ]+)', version["information_source"])
		if m is not None:
			url = m.group(1)
			title = re.search('(?:^|/)([^/]+)/?$', url).group(1)
			return "{{cite web |url=%s |title=%s |accessdate=%s }}" % (url, title, fmt_today(),)

	return "{{cite web |url=https://yournextmp.com/constituency/%d/ |publisher=YourNextMP |title=%s |accessdate=%s }}" % (int(ynmp_constituency_data["result"]["id"]), ynmp_constituency_data["result"]["label"], fmt_today(),)

def wiki_template_for_ynmp_person(ynmp_data, ynmp_constituency_data):
	candidate_name = ynmp_data["person_id"]["name"]

	ynmp_party = ynmp_data["person_id"]["party_memberships"]["2015"]["name"]
	wikipedia_party_name = party_names.to_wikipedia_name(ynmp_party)
	if wikipedia_party_name is not None:
		party = wikipedia_party_name
		templatename = "Election box candidate with party link"
	else:
		party = ynmp_party
		templatename = "Election box candidate"

	reference = get_reference(ynmp_data, candidate_name, party, ynmp_constituency_data)

	return """{{%s
 |party      = %s
 |candidate  = %s<ref>%s</ref>
 |votes      = 
 |percentage = 
 |change     = 
}}
""" % (templatename, party, candidate_name, reference,)

def get_candidate(ynmp_data, candidate_name):
	candidate_data_list = {
		person["person_id"]["id"] : person # de-duplicates repetition of the same person
		for person in ynmp_data["result"]["memberships"]
		if person["person_id"]["name"] == candidate_name
		and person["person_id"].get("standing_in", {}).get("2015", None) }
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

	m = re.search(r"(\{\{Election box (?:end|majority|turnout).*)$", section, flags=re.I | re.DOTALL)
	if m is None:
		raise Exception("Could not find end tag on wikipage")
	section = section.replace(m.group(1), extratext + m.group(1))

	return head + section + tail

def generate_updated_wikitext(wikipedia_pagename, ynmp_constituency_id, ynmp_candidate_name):
	wikipage = wikipedia.latest_revision(wikipedia_pagename, allow_redirect=False)
	ynmp_constituency_data = ynmp.fetch_candidates_in_constituency(ynmp_constituency_id)
	candidate_data = get_candidate(ynmp_constituency_data, ynmp_candidate_name)
	candidate_template = wiki_template_for_ynmp_person(candidate_data, ynmp_constituency_data)
	return insert_candidate_in_election_box(wikipage, candidate_template)

def generate_upload_form(form_id, wikipedia_pagename, text, summary):
	return """
<form id="%s" method="POST" action="https://en.wikipedia.org/w/index.php?title=%s&action=submit">
	<input type="hidden" name="format" value="text/x-wiki" />
	<input type="hidden" name="wpSummary" value="%s" />
	<input type="hidden" name="wpDiff" value="Show changes" />
	<input type="hidden" name="wpTextbox1" value="%s" />
	<input type="submit" value="Preview changes on Wikipedia" />
</form>""" % (form_id, escape(urllib.quote(wikipedia_pagename)), escape(summary), escape(text),)

def cgi_response(wikipedia_pagename, ynmp_constituency_id, ynmp_candidate_name):
	wikitext = generate_updated_wikitext(wikipedia_pagename.decode("utf8"), int(ynmp_constituency_id), ynmp_candidate_name.decode("utf8"))
	return (
		"Content-type: text/html; charset=utf8\n\n"
		+ generate_upload_form("wp_upload_form", wikipedia_pagename, wikitext, "Update list of candidates")
		+ """\n<script for="window" action="onload">window.setTimeout(function () { document.getElementById("wp_upload_form").submit(); }, 500);</script>""")

if __name__=='__main__':
	logging.root.setLevel(logging.DEBUG)
	print cgi_response(u"Aberavon (UK Parliament constituency)", u"66101", u"Captain Beany")
