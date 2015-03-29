import csv
from collections import defaultdict
from collections import namedtuple

class Pty(object):
	def __init__(self, ynmp, name, rank=3, color="white"):
		self.ynmp = ynmp
		self.name = name.replace('"', '').replace("'", "")
		self.rank = rank
		self.color = color
		self.code = "".join(x for x in self.ynmp if x.isalpha())
	def __hash__(self):
		return hash(self.ynmp)
	def __cmp__(self, other):
		return cmp(self.ynmp, other)

parties = dict((x.ynmp, x) for x in (
	Pty("Conservative Party", "Conservative", 0, "dodgerblue"),
	Pty("Labour Party", "Labour", 0, "firebrick1"),
	Pty("Liberal Democrats", "Lib Dem", 0, "orange"),
	Pty("UK Independence Party (UKIP)", "UKIP", 1, "purple"),
	Pty("Green Party", "Green", 1, "green"),

	Pty("British National Party", "BNP"),
	Pty("Christian Party \"Proclaiming Christ's Lordship\"", "Christian"),
	Pty("English Democrats", "Eng Democrats"),
	Pty("Ulster Unionist Party", "UUP"),
))

party_others = Pty("Others", "Others")

def get_party(ynmp_name, args):
	if ynmp_name == "Conservative and Unionist Party":
		ynmp_name = "Conservative Party"

	try:
		party = parties[ynmp_name]
	except KeyError:
		if ynmp_name == "Independent":
			party = Pty("Independent", "Independent", rank=0 if args.independent else 100)
		else:
			party = Pty(ynmp_name, ynmp_name)

	if party.rank > 5 - args.hide_small:
		party = party_others

	return party

def format_name(name):
	return name

def name_grouping_individual(l):
	return [[x] for x in l]

def name_grouping_grouped(l):
	return [l]

def print_digraph(by_parties, name_grouping, args):
	print "digraph {"

	for party in set(n for (n, _) in by_parties.keys()) | set(n for (_, n) in by_parties.keys()):
		print "%s [label=\"%s\",style=filled,fillcolor=%s];" % (party.code, party.name, party.color if args.color else "white",)

	for ((old, new), full_namelist) in by_parties.items():
		for namelist in name_grouping(full_namelist):
			print "%s -> %s [label=\"%s\", penwidth=%d, weight=%d, fontsize=10];" % (
				old.code,
				new.code,
				"\\n".join(format_name(name) for name in namelist) if args.names else "",
				len(namelist),
				len(namelist))

	print "}"

def main(args):
	by_parties = defaultdict(list)
	for _, name, old_name, new_name in csv.reader(open("chgparty.txt")):
		old = get_party(old_name, args)
		new = get_party(new_name, args)
		by_parties[old, new].append(name)

	if not args.no_others:
		by_parties = dict(((old, new), namelist) for ((old, new), namelist) in by_parties.items() if old != "Others" and new != "Others")
	if not args.others_to_others:
		by_parties = dict(((old, new), namelist) for ((old, new), namelist) in by_parties.items() if old != "Others" or new != "Others")
	if args.trim:
		by_parties = dict(((old, new), namelist) for ((old, new), namelist) in by_parties.items() if len(namelist) > args.trim or max((old.rank, new.rank)) < args.dont_trim_large)

	print_digraph(by_parties, name_grouping_individual if args.single_line else name_grouping_grouped, args)

if __name__=='__main__':
	import argparse
	import sys

	parser = argparse.ArgumentParser()

	parser.add_argument("-t", "--trim", action="count", default=0, help="Hide single defections (multiple times to hide less than N defections)")
	parser.add_argument("-T", "--dont-trim-large", action="count", default=0, help="Do not hide single defections to/from large political parties")
	parser.add_argument("-s", "--hide-small", action="count", default=0, help="Hide small parties (multiple times to hide more parties)")
	parser.add_argument("-o", "--no-others", action="store_false", default=True, help="Hide the combined \"others\" for small parties")
	parser.add_argument("-2", "--others-to-others", action="store_true", default=False, help="Show defections from \"others\" to itself")
	parser.add_argument("-i", "--independent", action="store_true", default=False, help="Show independent and others as different")
	parser.add_argument("-1", "--single-line", action="store_true", default=False, help="Show one line per candidate")
	parser.add_argument("-c", "--no-color", action="store_false", dest="color", default=True, help="No color")
	parser.add_argument("-n", "--no-names", action="store_false", dest="names", default=True, help="No names")
	args = parser.parse_args()

	if args.dont_trim_large and not args.trim:
		raise ValueError("You can't use -T without -t")

	main(args)

