from collections import namedtuple

Party = namedtuple("Party", "ynmp wikipedia short alternatives")
parties = (
	Party("Labour Party", "Labour Party (UK)", "L", ["The Labour Party"]),
	Party("Conservative Party", "Conservative Party (UK)", "C", []),
	Party("Liberal Democrats", "Liberal Democrats", "LD", ["Liberal Democrats (UK)"]),
	Party("Green Party", "Green Party of England and Wales" , "G", ["Green Party (UK)"]),
	Party("UK Independence Party (UKIP)", "UK Independence Party", "UKIP", ["United Kingdom Independence Party"]),
	Party("Plaid Cymru - The Party of Wales", "Plaid Cymru", "PC", []),
	Party("Scottish National Party (SNP)", "Scottish National Party", "SNP", []),
	Party("Independent", "Independent (politician)", "Ind", []),
	Party("Trade Unionist and Socialist Coalition", "Trade Unionist and Socialist Coalition", "TUSC", []),
	Party("Alliance - Alliance Party of Northern Ireland", "Alliance", "A", ["Alliance Party of Northern Ireland"]),
	Party("SDLP (Social Democratic & Labour Party)", "Social Democratic and Labour Party", "SDLP", []),
	Party(u'Sinn F\xe9in', u'Sinn F\xe9in', "SF", ["Sinn Fein"]),
	Party("Class War", "Class War", "CW", []),
	Party("National Health Action Party", "National Health Action Party", "NHA", []),
	Party("Democratic Unionist Party - D.U.P.", "Democratic Unionist Party", "DUP", []),
	Party("Mebyon Kernow - The Party for Cornwall", "Mebyon Kernow", "MK", []),
	Party("Ulster Unionist Party", "Ulster Unionist Party", "UUP", []),
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

