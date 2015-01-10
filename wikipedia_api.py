import urllib
import json
import logging
import re

def latest_revision(pagename):
	logging.debug("latest_revision(%r)", pagename)
	assert isinstance(pagename, unicode)
	req = urllib.urlopen("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&format=json" % (urllib.quote(pagename.encode("utf8")),))
	page = req.read()
	try:
		data = json.loads(page)
		page_data, = data["query"]["pages"].values()
		revision, = page_data["revisions"]
		return revision["*"]
	except Exception:
		logging.exception("Invalid response for %r", page)
		raise

def parliament_constituencies():
	page = latest_revision("List of United Kingdom Parliament constituencies")
	table = re.search(r'class="wikitable sortable"(.*?)\|}\s*==', page, re.DOTALL).group(1)
	after_tr = True
	for line in table.split("\n")[1:]:
		if line.startswith("!"):
			continue
		if line.startswith("|-"):
			after_tr = True
			continue
		if after_tr:
			after_tr = False
			m = re.search(r"^\s*\|\s*\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]", line)
			if m is None:
				raise ValueError(line)
			yield m.group(1).strip()

