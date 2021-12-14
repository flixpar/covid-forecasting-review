import requests
import pandas as pd
import json
import tqdm


url_template = "https://api.semanticscholar.org/graph/v1/paper/<ID>/references?fields=title,externalIds&limit=1000"

data = pd.read_csv("../data/finaldata.csv")
dois = data.doi.tolist()

def getDOI(x):
	if x["externalIds"] and "DOI" in x["externalIds"]:
		return x["externalIds"]["DOI"]
	elif x["externalIds"] and "arXiv" in x["externalIds"]:
		return "arxiv:" + x["externalIds"]["arXiv"]
	else:
		return None

references_data = {}
for d in tqdm.tqdm(dois):
	if d[:3] == "10.":
		_d = "DOI:" + d
	elif d == "NONE":
		continue
	else:
		_d = d

	query_url = url_template.replace("<ID>", _d)
	response_raw = requests.get(query_url)

	if not response_raw.ok:
		print(f"Error! References fetch failed for {d}")
		references_data[d] = []
		continue
	response = response_raw.json()

	data = [x["citedPaper"] for x in response["data"]]
	data = [{"id": x["paperId"], "title": x["title"], "doi": getDOI(x)} for x in data]
	references_data[d] = data

with open("../raw_responses/references_metadata_raw.json", "w") as f:
	json.dump(references_data, f)
