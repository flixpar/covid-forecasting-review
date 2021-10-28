import requests
import pandas as pd
import json
import tqdm


def main():
    data = pd.read_csv("../data/finaldata.csv")
    dois = data.doi.tolist()

    journals_found = [None]

    raw_responses = []
    metadata = []

    manual_overrides = {"1080-6040": "1080-6059"}

    for d in tqdm.tqdm(dois):
        if d == "NONE":
            continue
        i = fetch_issn(d)
        if i in manual_overrides:
            i = manual_overrides[i]
        if i not in journals_found:
            m, resp = fetch_crossref(i)
            raw_responses.append(resp)
            metadata.append(m)
            journals_found.append(i)

    metadata_df = pd.DataFrame(metadata)
    metadata_df.sort_values(by="title", inplace=True)
    metadata_df.to_csv("../data/journal_metadata.csv", index=False)

    with open("../rawdata/journal_metadata_raw.json", "w") as f:
        json.dump(raw_responses, f)

def fetch_issn(d):
    baseurl = "http://api.crossref.org/works/"
    query_url = baseurl + d
    resp_raw = requests.get(query_url)
    if not resp_raw.ok:
        return None
    resp = resp_raw.json()
    if resp["status"] == "ok" and "ISSN" in resp["message"]:
        return resp["message"]["ISSN"][0]
    else:
        return None

def fetch_crossref(d):
    baseurl = "http://api.crossref.org/journals/"
    query_url = baseurl + d
    resp_raw = requests.get(query_url)
    if not resp_raw.ok:
        print(f"Error! Metadata fetch failed for {d}")
        return {"issn": d}, {}
    resp = resp_raw.json()

    if resp["status"] != "ok":
        print(f"Error! Metadata fetch failed for {d}")
        return {"issn": d}, resp

    r = resp["message"]

    try:
        subjects = r.get("subjects")
        subjects = [s["name"] for s in subjects]
        subjects = "; ".join(subjects)
        m = {
            "title": fix_journal_title(r.get("title")),
            "issn": d,
            "subjects": subjects,
        }
        return m, resp
    except:
        return {"issn": d}, resp

manual_journal_fixes = {
    "Chaos Solitons & Fractals": "Chaos, Solitons & Fractals",
    "PLoS Biology": "PLOS Biology",
    "PLoS ONE": "PLOS ONE",
    "PLoS Computational Biology": "PLOS Computational Biology",
    "Proceedings of the Royal Society A Mathematical Physical and Engineering Sciences": "Proceedings of the Royal Society A: Mathematical, Physical and Engineering Sciences",
    "Journal Of Big Data": "Journal of Big Data",
    "Physica A Statistical Mechanics and its Applications": "Physica A: Statistical Mechanics and its Applications",
    "The Science of The Total Environment": "Science of The Total Environment",
}
def fix_journal_title(j):
    return manual_journal_fixes.get(j, j)

if __name__ == "__main__":
    main()
