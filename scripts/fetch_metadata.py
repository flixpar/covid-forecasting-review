import requests
import pandas as pd
import json
import arxiv
import tqdm


def main():
    data = pd.read_csv("../data/finaldata.csv")
    dois = data.doi.tolist()
    titles = data.title.tolist()

    raw_responses = []
    metadata = []

    for (i,d) in tqdm.tqdm(enumerate(dois), total=len(dois)):
        if d[:3] == "10.":
            m, resp = fetch_crossref(d)
        elif d != "NONE":
            m, resp = fetch_semanticscholar(d)
        else:
            m = {"doi": d, "title": titles[i]}
            resp = m
        raw_responses.append(resp)
        metadata.append(m)

    metadata_df = pd.DataFrame(metadata)
    metadata_df.to_csv("../data/metadata.csv", index=False)

    with open("../rawdata/metadata_raw.json", "w") as f:
        json.dump(raw_responses, f)

def fetch_crossref(d):
    baseurl = "http://api.crossref.org/works/"
    query_url = baseurl + d
    resp_raw = requests.get(query_url)
    resp = resp_raw.json()

    if resp["status"] != "ok":
        print(f"Error! Metadata fetch failed for {d}")
        return {"doi": d}, resp

    r = resp["message"]

    try:
        title = r.get("title", [])
        title = title[0] if title else ""

        doi = r.get("doi", d)
        date_published = r.get("created", {}).get("date-time", "")

        date_published_print = r.get("published-print", {}).get("date-parts", [])
        date_published_print = "-".join([str(s) for s in date_published_print[0]]) if date_published_print else ""

        journal = r.get("container-title", [])
        journal = ";".join(journal)

        publisher = r.get("publisher", "")
        citations = r.get("is-referenced-by-count")
        paper_type = r.get("type", "")

        authors = r.get("author", [])
        n_authors = len(authors) if authors else None

        m = {
            "title": title,
            "doi": doi,
            "date_published": date_published,
            "date_published_print": date_published_print,
            "journal": journal,
            "publisher": publisher,
            "citations": citations,
            "paper_type": paper_type,
            "n_authors": n_authors,
        }

        return m, resp

    except:
        return {"doi": d}, resp

def fetch_semanticscholar(d):
    baseurl = "https://api.semanticscholar.org/v1/paper/"
    query_url = baseurl + d
    resp_raw = requests.get(query_url)
    r = resp_raw.json()

    if r["doi"]:
        return fetch_crossref(r["doi"])

    if d[:5] == "arxiv":
        p = next(arxiv.Search(id_list=[d[6:]]).results())
        date_published = p.published.isoformat().replace("+00:00", "Z")
        paper_type = "preprint"
        venue = "arXiv"
    else:
        date_published = ""
        paper_type = ""
        venue = r["venue"]

    m = {
        "title": r["title"],
        "doi": d,
        "date_published": date_published,
        "date_published_print": "",
        "journal": venue,
        "publisher": venue,
        "citations": r["numCitedBy"],
        "paper_type": paper_type,
        "n_authors": len(r["authors"]),
    }
    return m, r

if __name__ == "__main__":
    main()
