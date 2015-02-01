import ynmp
import logging
from collections import defaultdict
import re
import os.path
import os
import json
import tempfile
import csv

"""
done	party_2010_only[party]
done	party_2015_only[party]
done	party_2010_and_2015[party]
done	same_candidate_same_constituency[party]
done	same_candidate_different_constituency[party]
done	candidate_changed_party[party, party]
done	candidate_changed_party_from[party]
done	candidate_changed_party_to[party]
done	has_twitter[party]
done	has_facebook[party]
done	has_homepage[party]
done	has_ppc[party]
done	has_wikipedia[party]
done	has_dob[party]
	is_sitting_mp[party]  # XXX can't do this one without more data
done	gender_male[party]
done	gender_female[party]
done	gender_undefined[party]
done	gender_other[party]
"""



def merge_counters(stats, moredata):
	for statname, statvalues in moredata.items():
		for party, counter in statvalues.items():
			stats[statname][party] += counter

def extract_party_name(person, year):
	memberships = person["party_memberships"]
	if memberships is None:
		return None
	m_year = memberships.get(year)
	if m_year is None:
		return None
	return m_year["name"]

def extract_post_id(person, year):
	standings = person["standing_in"]
	if standings is None:
		return None
	s_year = standings.get(year)
	if s_year is None:
		return None
	return s_year["post_id"]

def parse_constituency_data(data):
	stats = defaultdict(lambda: defaultdict(int))
	post_id = data["result"]["id"]
	parties_2015 = set()
	parties_2010 = set()
	people_seen_this_constuency = set()
	constituency_name = data["result"]["area"]["name"]
	for candidate in data["result"]["memberships"]:
		try:
			person = candidate["person_id"]
			if person["id"] in people_seen_this_constuency:
				continue
			else:
				people_seen_this_constuency.add(person["id"])

			party_2015 = extract_party_name(person, "2015")
			party_2010 = extract_party_name(person, "2010")
			standing_2015 = extract_post_id(person, "2015")
			standing_2010 = extract_post_id(person, "2010")
			standing_here_2015 = standing_2015 == post_id
			standing_here_2010 = standing_2010 == post_id

			if standing_here_2015 and standing_2010: # only interested in those standing HERE this year, to avoid double-counting
				if party_2015 == party_2010:
					if standing_here_2010:
						stats["same_candidate_same_constituency"][party_2015] += 1
					else:
						stats["same_candidate_different_constituency"][party_2015] += 1
				else:
					stats["candidate_changed_party"]["%s to %s" % (party_2010, party_2015,)] += 1
					stats["candidate_changed_party_from"][party_2010] += 1
					stats["candidate_changed_party_to"][party_2015] += 1

			if standing_here_2015:
				parties_2015.add(party_2015)
			if standing_here_2010:
				parties_2010.add(party_2010)

			if standing_here_2015:
				if person.get("birth_date", "1970-01-01") != "1970-01-01":
					stats["has_dob"][party_2015] += 1

				if person.get("email"):
					stats["has_email"][party_2015] += 1

				if person.get("gender") == None:
					logging.info("Gender not set https://yournextmp.com/person/%d/ %s", int(person.get("id")), person.get("name"))
					stats["gender_undefined"][party_2015] += 1
				elif person.get("gender").lower() == "male":
					stats["gender_male"][party_2015] += 1
				elif person.get("gender").lower() == "female":
					stats["gender_female"][party_2015] += 1
				else:
					logging.info("Unknown gender %r for %r in %r", person.get("gender"), person.get("name"), constituency_name)
					stats["gender_other"][party_2015] += 1

				has_fb = False
				for link in person["links"]:
					if link["note"] == "party PPC page":
						stats["has_ppc"][party_2015] += 1
					elif link["note"] == "homepage":
						stats["has_homepage"][party_2015] += 1
					elif link["note"] == "wikipedia":
						stats["has_wikipedia"][party_2015] += 1
					elif link["note"] == "facebook page":
						has_fb = True
					elif link["note"] == "facebook personal":
						has_fb = True
					else:
						logging.info("unhandled link type %r", link["note"])
				if has_fb:
					stats["has_facebook"][party_2015] += 1

				for contact in person["contact_details"]:
					if contact["type"] == "twitter":
						stats["has_twitter"][party_2015] += 1
					else:
						logging.info("unhandled contact type %r", contact["type"])
		except Exception:
			logging.info("candidate %r", candidate)
			raise

	for party in parties_2010 - parties_2015:
		stats["party_2010_only"][party] += 1
	for party in parties_2015 - parties_2010:
		stats["party_2015_only"][party] += 1
	for party in parties_2010 & parties_2015:
		stats["party_2010_and_2015"][party] += 1
	for party in parties_2015:
		stats["party_2015"][party] += 1
		
	return stats

def escape_eu_name(eu_name):
	return re.sub(r"[^a-z0-9A-Z]", "", eu_name).lower()

def get_region(constituency_id, constituency_name):
	with open("constituency_name_to_region_name.json", "r") as f:
		constituency_name_to_region_name = json.load(f)
	eu_name, county_name = constituency_name_to_region_name["%s:%s" % (constituency_id, constituency_name,)]
	return escape_eu_name(eu_name), escape_eu_name(county_name)

def gather_stats(csvfile):
	stats = defaultdict(lambda: defaultdict(int))
	stats_by_eu_region = defaultdict(lambda : defaultdict(lambda: defaultdict(int)))

	for constituency_id, constituency_name in tuple(ynmp.all_constituencies()):
		constituency_data = ynmp.fetch_candidates_in_constituency(constituency_id)
		constituency_stats = parse_constituency_data(constituency_data)

		merge_counters(stats, constituency_stats)

		eu_region_name, county = get_region(constituency_id, constituency_name)
		merge_counters(stats_by_eu_region[eu_region_name], constituency_stats)

		write_csv_line(csvfile, constituency_name, eu_region_name, county, constituency_stats)

	return stats, stats_by_eu_region

csv_headers = [u'constituency_name', u'eu_region', u'county', u'party',
	u'gender_male', u'gender_female', 
	u'party_2010_only', u'party_2010_and_2015', u'party_2015',
	u'same_candidate_same_constituency', u'same_candidate_different_constituency',
	u'has_dob', u'has_email', u'has_ppc', u'has_homepage',
	u'has_twitter', u'has_facebook', u'has_wikipedia']

def write_csv_header(csvfile):
	csvfile.writerow(csv_headers)

def write_csv_line(csvfile, constituency_name, eu_region, county, stats):
	def enc(u):
		return unicode(u).encode("utf8")
	parties = set(sum((stat.keys() for stat in stats.values()), []))
	for party in parties:
		line = [enc(constituency_name), enc(eu_region), enc(county), enc(party)] + [
			enc(stats.get(stat_name, {}).get(party, 0))
			for stat_name in csv_headers[4:]]
		csvfile.writerow(line)

def atomic_write(directory, filename, text):
	full_dest_filename = os.path.join(directory, filename)
	temp_name = os.path.join(directory, ".tmp" + filename) # not using tempfile because the target directory is chmod ug+s
	with open(temp_name, "w") as temp_f:
		temp_f.write(text)
	os.rename(temp_name, full_dest_filename) # atomic

def format_stats(stats):
	return json.dumps({k : dict(v.items()) for k, v in stats.items()}, indent=True)


if __name__=='__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument("--directory", "-d", metavar="DIR", type=str, help="directory for datafiles", required=True)
	parser.add_argument("--verbose", "-v", action="count", help="More logging (can use multiple times)")
	parser.add_argument("--csv",  metavar="FILENAME", default="ynmp_stats.csv", help="Output to CSV file")
	args = parser.parse_args()

	logging.root.setLevel({
		0 : logging.WARN,
		1 : logging.INFO,
		}.get(args.verbose or 0, logging.DEBUG))

	with open(args.csv, "w") as csvf:
		csvfile = csv.writer(csvf)
		write_csv_header(csvfile)

		stats, eu_stats = gather_stats(csvfile)

	atomic_write(args.directory, "ynmp_stats.json", format_stats(stats))
	for eu_name, eu_data in eu_stats.items():
		atomic_write(args.directory, "ynmp_stats_%s.json" % (eu_name,), format_stats(eu_data))

	atomic_write(args.directory, "ynmp_stats_index.json", json.dumps(list(eu_stats.keys())))


