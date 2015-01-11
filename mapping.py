import csv

class MappingDatabase(object):
	def __init__(self, entries):
		self.entries = entries

	def save(self, f):
		w = csv.writer(f, dialect="excel-tab")
		for ((source, alias), canonical) in sorted(self.entries.items()):
			w.writerow((source, alias.encode("utf8"), canonical.encode("utf8")))

	@classmethod
	def load(cls, f):
		entries = {
			(source, alias.decode("utf8")) : canonical.decode("utf8")
			for source, alias, canonical
			in csv.reader(f, dialect="excel-tab")}
		return cls(entries)

	def lookup_or_add(self, source, alias, default_canonical):
		return self.entries.setdefault((source, alias), default_canonical)

	def merge(self, source, alias, canonical):
		assert (source, alias) in self.entries
		self.entries[source, alias] = canonical

	def mappings_for_source(self, source):
		for ((this_source, alias), canonical) in self.entries.items():
			if this_source == source:
				yield alias, canonical

