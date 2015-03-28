import csv
from collections import defaultdict

def fmt_pty(x):
	if "(UKIP)" in x:
		return "UKIP"
	return x.split("-")[0].replace(" ", "").replace("'", "").replace('"', '').replace("&", "")

def pty(x):
	return {
		# These parties have more than one defection on 28 March 2015
		# TODO: we should work that out automatically
		"ChristianPartyProclaimingChristsLordship" : "Christian",
		"NationalHealthActionParty" : "NHA",
		"TradeUnionistandSocialistCoalition" : "TUSC",
		"BritishNationalParty" : "BNP",
		"UlsterUnionistParty" : "UUP",
		"GreenParty" : "Green",
		"LiberalDemocrats" : "LibDem",
		"ConservativeParty" : "Conservative",
		"ConservativeandUnionistParty" : "Conservative", # Con and Unionists are really the same thing
		"EnglishDemocrats" : "EngDem",
		"Independent" : "Others", # Independent and small parties are pretty much interchangable
		"UKIP" : "UKIP",
	}.get(fmt_pty(x), "Others")


def nm(x):
	return x


every = defaultdict(list)
for _, name, old, new in csv.reader(open("chgparty.txt")):
	every[pty(old), pty(new)].append(nm(name))

print "digraph {"
# Labour[style=filled,fillcolor=firebrick1];
print """
	Christian[style=filled,fillcolor=white];
	BNP[style=filled,fillcolor=white];
	UUP[style=filled,fillcolor=white];
	Green[style=filled,fillcolor=green];
	LibDem[style=filled,fillcolor=orange];
	Conservative[style=filled,fillcolor=dodgerblue];
	EngDem[style=filled,fillcolor=white];
	UKIP[style=filled,fillcolor=purple];
"""
for ((old, new), namelist) in every.items():
	if old == "Others" or new == "Others":
		continue
	print "%s -> %s [label=\"%s\", penwidth=%d, weight=%d, fontsize=10];" % (old, new, "\\n".join(namelist), len(namelist), len(namelist),)
print "}"

