
def escape_html(text):
	return "".join(
		c if c.isalnum() or c.isspace() else "&#x%04x;" % (ord(c),)
		for c in text
		).encode("utf8")

class Candidate(object):
	def __init__(self, name, party, person_id, party_id, references, citation_needed=False):
		self.name = name
		self.party = party
		self.person_id = person_id
		self.party_id = party_id
		self.references = references
		self.citation_needed = citation_needed
	@classmethod
	def from_dict(cls, dct):
		return cls(**dct)
	def to_dict(self):
		return dict(name=self.name, party=self.party, person_id=self.person_id, party_id=self.party_id, references=self.references, citation_needed=self.citation_needed)
	def __repr__(self):
		return "Candidate.from_dict(%r)" % (self.to_dict(),)

