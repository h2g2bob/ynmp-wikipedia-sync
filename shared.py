
class Candidate(object):
	def __init__(self, name, party):
		self.name = name
		self.party = party
	@classmethod
	def from_dict(cls, dct):
		return cls(**dct)
	def to_dict(self):
		return dict(name=self.name, party=self.party)
	def __repr__(self):
		return "Candidate(%r, %r)" % (self.name, self.party,)

