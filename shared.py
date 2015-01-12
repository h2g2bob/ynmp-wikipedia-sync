
class Candidate(object):
	def __init__(self, name, party, person_id, party_id, references):
		self.name = name
		self.party = party
		self.person_id = person_id
		self.party_id = party_id
		self.references = references
	@classmethod
	def from_dict(cls, dct):
		return cls(**dct)
	def to_dict(self):
		return dict(name=self.name, party=self.party, person_id=self.person_id, party_id=self.party_id, references=self.references)
	def __repr__(self):
		return "Candidate.from_dict(%r)" % (self.to_dict(),)

