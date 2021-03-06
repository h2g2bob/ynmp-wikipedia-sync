import combined_data
from mapping import MappingDatabase
import logging
import re
import json

def subst_words(gen):
	replacements = {
		"joseph" : "jo",
		"joe" : "jo",
		"josephine" : "jo",
		"steven" : "steve",
		"jeffrey" : "jeff",
		"matthew" : "matt",
		"christopher" : "chris",
		"kristopher" : "chris",
		"kris" : "chris",
		"cristian" : "chris",
		"cris" : "chris",
		"vincent" : "vince",
		"michael" : "mike",
		"mick" : "mike",
		"sue" : "su",
		"janet" : "jan",
		"robert" : "rob",
		"bob" : "rob",
		"oliver" : "ollie",
		"peter" : "pete",
		"philip" : "phil",
		'phillip' : 'phil',
		'phill' : 'phil',
		"cammy" : "cameron",
		"david" : "dave",
		"stephen" : "steve",
		"clifford" : "cliff",
		"edward" : "ed",
		"eddy" : "ed",
		"ted" : "ed",
		"nicholas" : "nick",
		"nic" : "nick",
		"chinyelu" : "chi",
		"ernest" : "ernie",
		"victoria" : "vicky",
		"vicki" : "vicky",
		"thomas" : "tom",
		"charles" : "charlie",
		"anthony" : "tony",
		"christian" : "chris",
		"patricia" : "pat",
		"trish" : "pat",
		"patrick" : "pat",
		"benjamin" : "ben",
		"terence" : "terry",
		"ibrahim" : "ibby",
		"rebecca" : "beci",
		"gareth" : "gaz",
		"tadeusz" : "tad",
		"gregory" : "greg",
		"andrew" : "andy",
		"kenneth" : "ken",
		"martin" : "martie",
		"elizabeth" : "lizzie",
		"jacqueline" : "jack",
		"jacky" : "jack",
		"james" : "jim",
		"jimmy" : "jim",
		"gareth" : "gary",
		"daniel" : "dan",
		"danny" : "dan",
		"william" : "bill",
		"will" : "bill",
		"jaspreet" : "jas",
		"katharina" : "kat",
		"stuart" : "stu",
		"raymond" : "ray",
		"jonathan" : "jon",
		"jonny" : "jon",
		"gabriella" : "gabby",
		"debra" : "debbie",
		"gerrard" : "gerry",
		"samuel" : "sam",
		"richard" : "rick",
		"rich" : "rick",
		"dominic" : "dom",
		"geoffrey" : "geoff",
		"jennifer" : "jenny",
		"jessica" : "jess",
		"catherine" : "cathy",
		"theodora" : "theo",
		"annie" : "ann",
		"geraldine" : "gerri",

		# Unicode fixes:
		"andr" : "andree", # u"andr\xe9e"
		"skwirczy" : "skwirczynski",
	}
	for word in gen:
		yield replacements.get(word, word)

def similar_name(aname, bname):
	awords = set(subst_words(re.findall(r"[a-z]+", aname.lower())))
	bwords = set(subst_words(re.findall(r"[a-z]+", bname.lower())))
	if len(awords & bwords) >= 2:
		return True
	else:
		return False

def find_matching_candidate(candidate, possible_matches):
	matches = []
	for poss_match in possible_matches:
		if similar_name(poss_match["name"], candidate["name"]):
			matches.append(poss_match)
	if len(matches) == 1:
		return matches[0]
	elif len(matches) == 0:
		return None
	else:
		# Suppress this -- ynmp people will merge these later
		logging.info("Too many matches for %r %r", candidate, matches)
		return None

if __name__=='__main__':
	logging.root.setLevel(logging.WARN)

	with open("candidates_from_wikipedia.json", "r") as f:
		wikipedia = json.load(f)
	with open("candidates_from_ynmp.json", "r") as f:
		ynmp = json.load(f)

	with open("mappings_constituency.csv", "r") as f:
		constituency_map = MappingDatabase.load(f)
	with open("mappings_candidate.csv", "r") as f:
		candidate_map = MappingDatabase.load(f)

	
	for constituency_name, wp_candidates, ynmp_candidates in sorted(combined_data.merge_constituencies(constituency_map, "wikipedia", wikipedia, "ynmp", ynmp)):
		for wp_candidate in wp_candidates:
			ynmp_candidate = find_matching_candidate(wp_candidate, ynmp_candidates)
			if ynmp_candidate is not None:
				ynmp_name = constituency_name + ":" + ynmp_candidate["name"]
				wp_name = constituency_name + ":" + wp_candidate["name"]
				canonical_ynmp_name = candidate_map.lookup_or_add("ynmp", ynmp_name, ynmp_name)
				canonical_wp_name = candidate_map.lookup_or_add("wikipedia", wp_name, wp_name) # assert the wikipedia name has a mapping, so we can merge it
				logging.info("merge %r %r", wp_name, canonical_ynmp_name)
				candidate_map.merge("wikipedia", wp_name, canonical_ynmp_name)

	with open("mappings_constituency.csv", "w") as f:
		constituency_map.save(f)
	with open("mappings_candidate.csv", "w") as f:
		candidate_map.save(f)

