import pandas as pd

flatten = lambda l: [item for sublist in l for item in sublist]

subjects_df = pd.read_csv("../rawdata/journal_subjects.csv")
allfields = subjects_df.field.tolist()

manual_df = pd.read_csv("../rawdata/journal_subjects_manual.csv")
manual_subject_lookup = {row[1]["field"]: row[1]["subject_manual"] for row in manual_df.iterrows()}

journal_metadata = pd.read_csv("../data/journal_metadata.csv")
meta_fields = [s.split("; ") for s in journal_metadata.subjects.tolist()]
meta_fields = sorted(list(set(flatten(meta_fields))))

subjects_df = subjects_df[subjects_df.field.isin(meta_fields)]

missing_fields = set.difference(set(meta_fields), set(allfields))
missing_fields.add("preprint")
for field in missing_fields:
	subjects_df = subjects_df.append({"field": field, "subject_area": "Unknown", "asjc_code": "NA"}, ignore_index=True)

subjects_df["subject_area_manual"] = subjects_df.field.map(manual_subject_lookup)

subjects_df.to_csv("../data/journal_subjects.csv", index=False)
