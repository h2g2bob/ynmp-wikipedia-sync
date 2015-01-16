from collections import namedtuple

Party = namedtuple("Party", "ynmp wikipedia short alternatives")
parties = (
	Party("Labour Party", "Labour Party (UK)", "L", []),
	Party("Conservative Party", "Conservative Party (UK)", "C", []),
	Party("Liberal Democrats", "Liberal Democrats", "LD", []),
	Party("Green Party", "Green Party of England and Wales" , "G", []),
	Party("UK Independence Party (UKIP)", "UK Independence Party", "UKIP", []),
	Party("Plaid Cymru - The Party of Wales", "Plaid Cymru", "PC", []),
	Party("Scottish National Party (SNP)", "Scottish National Party", "SNP", []),
	Party("Independent", "Independent (politician)", "Ind", []),
)

lookup_long_name = {}
for p in parties:
	lookup_long_name[p.ynmp] = p
	lookup_long_name[p.wikipedia] = p
	for alt in p.alternatives:
		lookup_long_name[alt] = p

def to_wikipedia_name(long_name):
	try:
		return lookup_long_name[long_name].wikipedia
	except KeyError:
		return None

def to_short_name(long_name):
	try:
		return lookup_long_name[long_name].short
	except KeyError:
		return None

