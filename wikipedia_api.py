import urllib
import json

def latest_revision(pagename):
	req = urllib.urlopen("https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&format=json" % (urllib.quote(pagename),))
	page = req.read()
	try:
		data = json.loads(page)
		page_data, = data["query"]["pages"].values()
		revision, = page_data["revisions"]
		return revision["*"]
	except Exception:
		print page
		raise

def pages_in_category(catname):
	cmcontinue = ""
	while True:
		req = urllib.urlopen("https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:%s&format=json&cmcontinue=%s" % (urllib.quote(catname), cmcontinue,))
		page = req.read()
		try:
			data = json.loads(page)
			for page_data in data["query"]["categorymembers"]:
				yield page_data["title"]
			if "query-continue" not in data:
				break
			cmcontinue = data["query-continue"]["categorymembers"]["cmcontinue"]
		except Exception:
			print page
			raise

def categories_only(gen):
	cat_prefix = "Category:"
	for name in gen:
		if name.startswith(cat_prefix):
			yield name[len(cat_prefix):]

def parliament_constituencies():
	base_cats = [
		"Parliamentary constituencies in the East Midlands",
		"Parliamentary constituencies in the East of England",
		"Parliamentary constituencies in London",
		"Parliamentary constituencies in North East England",
		"Parliamentary constituencies in North West England",
		"Parliamentary constituencies in South East England",
		"Parliamentary constituencies in South West England",
		"Parliamentary constituencies in the West Midland",
		"Parliamentary constituencies in Yorkshire and the Humber"]
	for base_cat in base_cats:
		for cat in categories_only(pages_in_category(base_cat)):
			for title in pages_in_category(cat):
				if "historic" in title.lower():
					continue
				if "list of" in title.lower():
					continue
				if "defunct" in title.lower():
					continue
				yield title


def parliament_constituencies_fromcache():
	with open("list_of_parliament_constituencies.txt", "r") as f:
		return f.readlines()

